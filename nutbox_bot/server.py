import asyncio
from queue import Queue, Full
from nutbox_bot.discord_bot import DiscordBot
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
        return [loop.create_task(self.run_monitor()), loop.create_task(self.monitor_message())]

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(self.get_tasks(loop)))
        loop.close()

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
