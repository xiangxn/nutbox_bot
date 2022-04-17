import logging
import logging.handlers
import time


class Logger(object):

    def __init__(self, name="nutbox_bot", debug=False):
        self.is_debug = debug
        self.dir = "logs/"
        self.logger = logging.getLogger("%s_logger" % name)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)
        self.formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s %(message)s")
        self.err_handler = logging.FileHandler(filename=f"{self.dir}{name}_error.log")
        self.err_handler.setLevel(logging.ERROR)
        self.err_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.err_handler)

        self.warn_handler = logging.FileHandler(filename=f"{self.dir}{name}_warning.log")
        self.warn_handler.setLevel(logging.WARNING)
        self.warn_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.warn_handler)

        self.debug_handler = logging.FileHandler(filename=f"{self.dir}{name}_debug.log")
        self.debug_handler.setLevel(logging.DEBUG)
        self.debug_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.debug_handler)

    def debug(self, msg, e=None, extra=None, screen=False):
        self.logger.debug(msg, exc_info=e, stack_info=False, extra=extra)
        if screen and self.is_debug:
            print("[{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg), extra if extra else "")

    def error(self, msg, e=None, extra=None, screen=False):
        self.logger.error(msg, exc_info=e, stack_info=False, extra=extra)
        if screen:
            print("[{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg), extra if extra else "")

    def warning(self, msg, e=None, extra=None, screen=False):
        self.logger.warning(msg, exc_info=e, extra=extra)
        if screen:
            print("[{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg), extra if extra else "")