import discord, logging
from discord.ext import commands

# from asyncio import sleep
# from __main__ import traceback

logger = logging.getLogger(__name__)


class wave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(1222570897244688454)

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     await self.channel.send(f"Welcome!")

    @commands.Cog.listener()
    async def on_message(self, message):

        # identity_bot = str(await self.bot.application_info()).split(' ')[1].strip('id=')
        triggers = (
            "hi",
            "hello",
            "hey",
            "good morning",
            "good night",
            "good evening",
            "bye",
            "later",
            "see ya",
            "howdy",
        )

        try:
            if message.author.bot:
                return  # guard clause
            if not message.content.startswith(triggers):
                return
            await message.add_reaction("👋")
            # await sleep(1)
            # await message.remove_reaction('👋', self.bot.get_user(int(identity_bot)))
        except Exception as e:
            logger.info(e)
            # await traceback(message.channel, e)


def setup(bot):
    bot.add_cog(wave(bot))
