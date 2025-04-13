import discord.ext
from discord.ext import commands
from __main__ import traceback

class mime(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):

		triggers = (
			'>:3',
			'uwu',
			'owo',
		)

		try:
			if message.author.bot: return # if from bot then ignore
			if not message.content.lower() in triggers: return
			await message.channel.send(message.content)
		except Exception as e: await traceback(message.channel, e)

def setup(bot):
	bot.add_cog(mime(bot))
