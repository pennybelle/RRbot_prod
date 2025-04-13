import discord.ext
from discord.ext import commands
from __main__ import traceback

class send_embed(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command()
	async def create_embed(self, ctx, channel_id=None, title='', message='', footer=''):

		embed = discord.Embed(title=title, description=message)
		embed.set_footer(text=footer)
		try:
			if channel_id:
				channel = self.bot.get_channel(int(channel_id))
				print(channel)
				await channel.send(embed=embed)
				await ctx.respond(f'embed sent to <#{channel_id}>', ephemeral=True)
				return
			await ctx.send(embed=embed)
			await ctx.respond('embed posted successfully', ephemeral=True)
		except Exception as e:
			print(e)
			await ctx.respond(f'Error: {e}')

	# @commands.command()
	# async def embed(self, ctx, title='', message='', footer=''):

	# 	embed = discord.Embed(title=title, description=message)
	# 	embed.set_footer(text=footer)
	# 	try:
	# 		await ctx.message.delete()
	# 		await ctx.send(embed=embed)
	# 	except Exception as e:
	# 		print(e)
	# 		await ctx.send(f'Error: {e}')

def setup(bot):
	bot.add_cog(send_embed(bot))
