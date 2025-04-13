import discord.ext, logging, asyncio
from discord.ext import commands

logger = logging.getLogger(__name__)

bug_report_channel = 1222328472676991047  # prod
log_channel_id = 1246454436444901389  # prod
# bug_report_channel = 1245840444135309322  # dev
# log_channel_id = 1246456765160362075  # dev


def log_bug_report(
    message,
    author,
    color=discord.Color.from_rgb(255, 0, 0),
):
    embed = discord.Embed(
        title="Bug Report",
        description=(
            f"{message}\n\n**Sent by {author.name}\n[<@{author.id}>]\n[{author.id}]**"
        ),
        color=color,
    )
    return embed


class bug_report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != bug_report_channel:
            return

        try:
            await message.delete()

            channel = self.bot.get_channel(bug_report_channel)
            logger.debug(f"bug_report: {channel}")
            embed = discord.Embed(
                description="Thank you for the report, this will be looked into asap!",
                color=discord.Color.from_rgb(255, 0, 0),
            )
            await channel.send(embed=embed, delete_after=10)

            embed = log_bug_report(message.content, message.author)
            channel = self.bot.get_channel(log_channel_id)
            logger.debug(f"log_channel: {channel}")
            await channel.send(embed=embed)

        except Exception as e:
            logger.warning(e)

    @staticmethod
    async def initial_purge(bot):
        count = 0

        try:
            channel = bot.get_channel(bug_report_channel)
            logger.debug(f"beginning initial purge in {channel}...")
            async for message in channel.history(limit=1000, oldest_first=True):
                if message.author.bot:
                    continue

                # delete message
                await message.delete()
                count += 1

                # log message replacement
                log_channel = bot.get_channel(log_channel_id)
                embed = log_bug_report(message.content, message.author)
                await log_channel.send(embed=embed)

                # wait a sec to prevent rate limit
                await asyncio.sleep(1)

            if count >= 1:
                # mark as reported
                embed = discord.Embed(
                    description="Thank you for the report, this will be looked into asap!",
                    color=discord.Color.from_rgb(255, 0, 0),
                )
                await channel.send(embed=embed, delete_after=10)

            logger.debug(
                f"initial purge in {channel} is complete, moved {count} messages..."
            )

        except Exception as e:
            logger.warning(e)


def setup(bot):
    bot.add_cog(bug_report(bot))
