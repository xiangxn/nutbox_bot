import discord


class DiscordBot(discord.Client):

    def __init__(self, *, loop=None, logger=None, **options):
        self.logger = logger
        self.config = options.pop("config", {"token": "", "proxy": "", "channels": {}})
        self.proxy = self.config['proxy']
        self.channels = {}
        if len(self.proxy) > 0:
            super().__init__(loop=loop, proxy=self.proxy, **options)
        else:
            super().__init__(loop=loop, **options)

    async def on_ready(self):
        print('Logged on as', self.user)
        keys = self.config['channels'].keys()
        for key in keys:
            self.channels[key] = self.get_channel(self.config['channels'][key])
        await self.send("service-monitoring", "🟢 nutbox-bot start...")

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.content == 'ping':
            await message.channel.send('pong')

    async def send(self, channel: str, msg: str):
        if channel and channel in self.channels.keys():
            await self.channels[channel].send(msg)
        else:
            print(f"Channel '{channel}' does not exist")

    async def start(self, *args, **kwargs):
        return await super().start(self.config['token'], *args, **kwargs)


if __name__ == '__main__':
    import json
    cf = open("./config.json", "r")
    config_info = json.load(cf)
    intents = discord.Intents.default()
    intents.messages = True
    client = DiscordBot(intents=intents, config=config_info)
    client.run()
