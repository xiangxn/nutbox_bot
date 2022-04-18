from concurrent import futures
import time
import grpc
from nutbox_bot.grpc.nutbox_bot_pb2 import BaseReply
from nutbox_bot.grpc.nutbox_bot_pb2_grpc import add_NutboxBotServicer_to_server, NutboxBotServicer


def check_ip(f):

    def wrapper(server, request, context):
        peer = context.peer()
        info = peer.split(":")
        ip = info[1]
        if ip in server.config['whitelist']:
            return f(server, request, context)
        else:
            server.logger.warning(f"Illegal access request: {peer}")
            br = BaseReply()
            br.code = 403
            br.msg = "No access"
            return br

    return wrapper


class TokenInterceptor(grpc.ServerInterceptor):

    def __init__(self):

        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'No access')

        self._abortion = grpc.unary_unary_rpc_method_handler(abort)

    def intercept_service(self, continuation, handler_call_details):
        method_name = handler_call_details.method.split('/')
        # meta = dict(handler_call_details.invocation_metadata)
        # print(self)
        flag = False
        allows = ['PushMessage']
        if method_name[-1] in allows:
            flag = True
        if flag:
            return continuation(handler_call_details)
        else:
            return self._abortion


class GrpcServer(NutboxBotServicer):

    def __init__(self, config, bot_server) -> None:
        self.config = config
        self.server = bot_server
        super().__init__()

    @check_ip
    def PushMessage(self, request, context):
        br = BaseReply()
        if request.channel and request.message and self.server:
            self.server.post_message(request.message, channel_name=request.channel)
            br.code = 0
        elif not self.server or not self.server.monitor.is_ready():
            br.code = 1
            br.msg = "Bot service is not ready yet."
        else:
            br.code = 1
            br.msg = "Invalid parameter."
        return br

    @classmethod
    def Run(cls, config, bot_server):
        # 这里通过thread pool来并发处理server的任务
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=(TokenInterceptor(), ))

        # 将对应的任务处理函数添加到rpc server中
        svr = cls(config, bot_server)
        add_NutboxBotServicer_to_server(svr, server)

        # 这里使用的非安全接口，世界gRPC支持TLS/SSL安全连接，以及各种鉴权机制
        port = "[::]:{}".format(config['grpc_port'])
        print("start {}".format(port))
        server.add_insecure_port(port)
        server.start()
        try:
            while True:
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)
