import logging
from discord.ext import commands

role = "developer"
logger = logging.getLogger(__name__)


class nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(role)
    async def kill(self, ctx):
        exit()

    @commands.command()
    @commands.has_role(role)
    async def nuke(self, ctx):
        logger.info(f"nuking {ctx.channel.name}...")
        try:
            await ctx.channel.purge()
            logger.info(f"successfully purged {ctx.channel.name}...")

        except Exception as e:
            logger.warning(e)


def setup(bot):
    bot.add_cog(nuke(bot))
