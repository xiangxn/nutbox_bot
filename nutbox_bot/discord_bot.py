import discord

from nutbox_bot.logger import Logger


class DiscordBot(discord.Client):

    def __init__(self, logger: Logger, loop=None, **options):
        self.logger = logger
        self.config = options.pop("config", {"token": "", "proxy": "", "channels": {}})
        self.proxy = self.config['proxy']
        self.channels = {}
        if len(self.proxy) > 0:
            super().__init__(loop=loop, proxy=self.proxy, **options)
        else:
            super().__init__(loop=loop, **options)

    async def on_ready(self):
        self.logger.debug(f"Logged on as {self.user}")
        keys = self.config['channels'].keys()
        for key in keys:
            self.channels[key] = self.get_channel(self.config['channels'][key])

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.content == 'ping':
            await message.channel.send('pong')

    async def send(self, channel: str, msg: str):
        if channel and channel in self.channels.keys():
            if not self.channels[channel]:
                self.channels[channel] = self.get_channel(self.config['channels'][channel])
            await self.channels[channel].send(msg)
        else:
            self.logger.warning(f"Channel '{channel}' does not exist")

    async def start(self, *args, **kwargs):
        return await super().start(self.config['token'], *args, **kwargs)

    async def on_error(self, event_method, *args, **kwargs):
        self.logger.error(f"event error: {event_method}")
        return await super().on_error(event_method, *args, **kwargs)


if __name__ == '__main__':
    import json
    cf = open("./config.json", "r")
    config_info = json.load(cf)
    intents = discord.Intents.default()
    intents.messages = True
    client = DiscordBot(intents=intents, config=config_info)
    client.run()
