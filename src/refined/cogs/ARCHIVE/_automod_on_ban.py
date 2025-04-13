import discord.ext
from discord.ext import commands
from __main__ import traceback

class automod_on_ban(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_ban(self, guild, user):
		channel_counter = 0
		msg_counter = 0
		channels_to_clear = [1208144053045166100]
		log_channel = self.bot.get_channel(1224371034908655700) # usagi/bot-spam
		try:
			await log_channel.send(f'{user} was banned from {guild}')
			async for channel in guild:
				if not channel.id in channels_to_clear: continue
				channel_counter += 1
				async for message in channel.history(limit=100):
					if not message.author == user: continue
					await message.delete()
					msg_counter += 1
		except Exception as e: await traceback(log_channel, e)

def setup(bot):
	bot.add_cog(automod_on_ban(bot))
