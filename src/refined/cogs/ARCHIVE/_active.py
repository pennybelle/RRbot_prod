import discord.ext
from discord.ext import commands, tasks
from asyncio import sleep
from __main__ import traceback

class is_active(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@tasks.loop(minutes=5)
	async def active(self, ctx):
		test_message = await self.bot.get_channel(1208144053045166100).send('test')
		# await sleep(59)
		await test_message.delete(delay = 59)

	@commands.command()
	async def test(self, ctx):
		test_message = await self.bot.get_channel(1208144053045166100).send('test')
		await test_message.delete()

def setup(bot):
	bot.add_cog(is_active(bot))
