import discord
from discord.ext import commands
from __main__ import bot

class testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def emojis(self, ctx):
        emoji_list = ''
        await ctx.send("printing emoji list...")
        for emoji in ctx.guild.emojis:
            emoji_list += f'<:{emoji.name}:{emoji.id}>'
        await ctx.send(emoji_list)


def setup(bot):
    bot.add_cog(testing(bot))