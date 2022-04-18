import asyncio
from concurrent import futures
import os
from queue import Queue, Full
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "grpc"))

import grpc
from nutbox_bot.discord_bot import DiscordBot
from nutbox_bot.grpc.nutbox_bot_pb2_grpc import add_NutboxBotServicer_to_server
from nutbox_bot.grpc_server import GrpcServer, TokenInterceptor
from nutbox_bot.logger import Logger
import discord


class BotServer:

    def __init__(self, config, debug=False) -> None:
        self.config = config
        self.logger = Logger("nutbox_bot", debug=debug)
        self.monitor = None
        self.msg_queue = Queue()
        self.RUN_SYNC = True

    def post_message(self, message: str, channel_name: str = "service-monitoring"):
        if self.monitor and self.monitor.is_ready() and self.msg_queue:
            data = {"channel": channel_name, "msg": message}
            try:
                self.msg_queue.put_nowait(data)
            except Full as e:
                self.logger.error("post_message error ", e=e, extra=data)

    def stop(self):
        self.logger.debug("Bot Server is stopping...")
        self.RUN_SYNC = False

    def get_tasks(self, loop):
        return [loop.create_task(self.run_monitor()), loop.create_task(self.monitor_message()), loop.create_task(self.run_grpc(loop))]

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(self.get_tasks(loop)))
        loop.close()

    def start_grpc(self):
        # 这里通过thread pool来并发处理server的任务
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=(TokenInterceptor(), ))

        # 将对应的任务处理函数添加到rpc server中
        svr = GrpcServer(self.logger, self.config, self)
        add_NutboxBotServicer_to_server(svr, self.grpc_server)

        # 这里使用的非安全接口，世界gRPC支持TLS/SSL安全连接，以及各种鉴权机制
        port = "[::]:{}".format(self.config['grpc_port'])
        self.logger.debug("grpc start {}".format(port))
        self.grpc_server.add_insecure_port(port)
        self.grpc_server.start()
        try:
            while self.RUN_SYNC:
                time.sleep(10)
        except Exception as e:
            self.logger.error("grpc server error: ", e=e)
        finally:
            self.grpc_server.stop(0)
            self.logger.error("grpc server stop")

    async def run_grpc(self, loop):
        try:
            await loop.run_in_executor(None, self.start_grpc)
        except Exception as e:
            self.logger.error("grpc error: ", e=e)

    async def run_monitor(self):
        intents = discord.Intents.default()
        intents.messages = True
        self.monitor = DiscordBot(self.logger, intents=intents, config=self.config)
        try:
            self.logger.debug("nutbox bot start...")
            await self.monitor.start()
        except Exception as e:
            self.logger.error("nutbox bot error", e=e)
        finally:
            self.logger.debug("nutbox bot stop...")
            if not self.monitor.is_closed():
                await self.monitor.close()

    async def monitor_message(self):
        self.logger.debug("monitor_message start...")
        try:
            while self.RUN_SYNC:
                if self.monitor.is_ready() and self.msg_queue.qsize() > 0:
                    data = self.msg_queue.get()
                    await self.monitor.send(data['channel'], data['msg'])
                    self.msg_queue.task_done()
                await asyncio.sleep(1)
        except Exception as e:
            self.logger.error("monitor message error", e=e)
        finally:
            self.logger.debug("monitor_message stop...")
            if self.monitor and not self.monitor.is_closed():
                await self.monitor.close()
