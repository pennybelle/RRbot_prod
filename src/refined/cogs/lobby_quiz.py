import discord.ext, logging
from discord.ext import commands

logger = logging.getLogger(__name__)

# from __main__ import traceback


class lobby_auto_delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = {
            "Refined RP LOCKED/lobby": 1223311561691627582,
            "Refined RP LOCKED/tickets/help": 1222375659188256909,
            "Refined RP LOCKED/tickets/faction": 1222664310765916281,
        }

    @commands.Cog.listener()
    async def on_message(self, message):

        try:
            if message.author.bot:
                return  # if from bot then ignore
            if message.channel.id in self.channels.values():
                await message.delete()  # delete all messages in #lobby
        except Exception as e:
            logger.info(e)
            # await traceback(message.channel, e)


class lobby_quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


# 	@commands.Cog.listener()
# 	async def on_message(self, message):

# 		try:
# 			if message.author.bot: return # if from bot then ignore
# 			if not message.channel.id == 1223311561691627582: return # only accepts messages in #lobby
# 			if message.content.lower() == 'verify':
# 				await message.author.add_roles('1')
# 				await message.channel.send('__QUIZ START__: **What term or abbreviation does the admin team use to describe itself ingame, as to not break immersion?**')

# 		except Exception as e: await traceback(message.channel, e)


# class lobby_quiz_1(commands.Cog):
# 	def __init__(self, bot):
# 		self.bot = bot

# 	@commands.Cog.listener()
# 	@commands.has_role('1')
# 	async def on_message(self, message):

# 		content = message.content.lower()
# 		try:
# 			if content == 'crr' or content == 'chernarus republic regulations':
# 				await message.author.remove_roles('1')
# 				await message.author.add_roles('2')
# 				await message.channel.send('PLACEHOLDER')

# 		except Exception as e: await traceback(message.channel, e)


def setup(bot):
    bot.add_cog(lobby_auto_delete(bot))
    # bot.add_cog(lobby_quiz(bot))
    # bot.add_cog(lobby_quiz_1(bot))
