import discord.ext
from discord.ext import commands
from asyncio import sleep
from __main__ import traceback

class general_attachment_handler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):

		try:
			if message.channel.id != 1208144053045166100: return
			if not len(message.attachments) > 0: return
			print(f'message has an attachment!')
			await sleep(120)
			await message.delete()
		except Exception as e: await traceback(message.channel, e)

def setup(bot):
	bot.add_cog(general_attachment_handler(bot))
