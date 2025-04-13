import discord.ext
from discord.ext import commands
from __main__ import traceback

class automod_on_ban(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command()
	async def oust(self, ctx: commands.Context, amount: int, member: discord.Member=None):
		await ctx.respond(f'Purging all messages from {member} in {ctx.guild}')
		channel_counter = 0
		msg_counter = 0
		limiter = 0
		channels_to_clear = [1208144053045166100] # usagi/bot
		log_channel = self.bot.get_channel(1224371034908655700) # usagi/bot-spam
		try:
			async for channel in ctx.guild:
				if not channel.id in channels_to_clear: continue
				limiter = 0
				channel_counter += 1

				async for message in channel.history(limit=100):
					if amount <= limiter: break 
					if not message.author == member: continue
					await message.delete()
					limiter += 1
					msg_counter += 1

			await log_channel.send(f'{member} was banned from {ctx.guild}')

		except Exception as e: await traceback(log_channel, e)

def setup(bot):
	bot.add_cog(automod_on_ban(bot))
