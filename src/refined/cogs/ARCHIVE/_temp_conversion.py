from discord.ext import commands
from __main__ import traceback

class temp_converter(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	async def f(self, ctx, celsius):
		try:
			fahrenheit = (float(celsius) * 1.8) + 32
			await ctx.send(f'{celsius} Celsius is {fahrenheit} Fahrenheit')
		except Exception as e:
			# e_type, e_value, e_traceback = exc_info()
			await traceback(ctx, e)

	@commands.command()
	async def c(self, ctx, fahrenheit):
		try:
			celsius = 0.55555555556 * (float(fahrenheit) - 32)
			await ctx.send(f'{fahrenheit} Fahrenheit is {celsius} Celsius')
		except Exception as e:
			# e_type, e_value, e_traceback = exc_info()
			await traceback(ctx, e)

def setup(bot):
	bot.add_cog(temp_converter(bot))
