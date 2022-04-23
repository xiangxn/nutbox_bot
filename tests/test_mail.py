import json
import sys

sys.path.append('./nutbox_bot')
from nutbox_bot.logger import Logger


class TestMail(object):

    def test_mail(self):
        import socket
        import socks
        socks.set_default_proxy(socks.HTTP,addr='127.0.0.1',port=8001)
        socket.socket = socks.socksocket
        config_info = {}
        cf = open("./config.json", "r")
        config_info = json.load(cf)
        logger = Logger("test", email=config_info['email'])
        logger.exception("test mail")
