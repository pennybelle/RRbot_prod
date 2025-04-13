# import random

from discord.ext import commands
import datetime


class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def hello(self, ctx):
        if 10 <= datetime.datetime.now().hour < 19:
            await ctx.respond("こんにちは『good day』!")
        elif 19 <= datetime.datetime.now().hour <= 24:
            await ctx.respond("こんばんは『good evening』!")
        else:
            await ctx.respond("おはよう『good morning』!")


def setup(bot):
    bot.add_cog(Hello(bot))
