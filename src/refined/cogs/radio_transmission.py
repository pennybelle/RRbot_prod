import discord.ext, logging, asyncio
from discord.ext import commands

logger = logging.getLogger(__name__)

radio_transmissions = 1222328766932455466  # prod
log_channel_id = 1222560582759223327  # prod
# radio_transmissions = 1245840444135309328  # dev
# log_channel_id = 1245840444999471256  # dev


def log_anon_message(
    message,
    author,
    color=discord.Color.from_rgb(255, 0, 0),
):
    embed = discord.Embed(
        title="Anonymous message log",
        description=(
            f"{message}\n\n**Sent by {author.name}\n[<@{author.id}>]\n[{author.id}]**"
        ),
        color=color,
    )
    return embed


class radio_transmission(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.initial_purge.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != radio_transmissions:
            return

        try:
            await message.delete()

            channel = self.bot.get_channel(radio_transmissions)
            logger.debug(f"radio_transmissions: {channel}")
            embed = discord.Embed(
                description=message.content, color=discord.Color.from_rgb(255, 0, 0)
            )
            await channel.send(embed=embed)

            embed = log_anon_message(message.content, message.author)
            channel = self.bot.get_channel(log_channel_id)
            logger.debug(f"log_channel: {channel}")
            await channel.send(embed=embed)

        except Exception as e:
            logger.warning(e)

    @commands.slash_command(
        description="Send an anonymous message in #radio-trasmissions"
    )
    async def click(
        self,
        ctx,
        message: discord.Option(
            str,
            description="Type the message you want to send anonymously",
        ),  # type: ignore
    ):
        if ctx.channel.id != radio_transmissions:
            await ctx.respond(
                f"This command only works in <#{radio_transmissions}>",
                ephemeral=True,
                delete_after=5,
            )
            return

        try:
            embed = discord.Embed(
                description=message, color=discord.Color.from_rgb(255, 0, 0)
            )
            await ctx.send(embed=embed)

            await ctx.respond(
                "Message sent completely anonymously"
                ", ||no one can see when you're typing a slash command.||",
                ephemeral=True,
                delete_after=6,
            )

            embed = log_anon_message(message, ctx.author)
            channel = self.bot.get_channel(log_channel_id)
            logger.debug(f"log_channel: {channel}")
            await channel.send(embed=embed)

        except Exception as e:
            await ctx.respond(
                f"A problem has occured. Traceback: ```{e}```",
                ephemeral=True,
            )
            logger.warning(e)

    @staticmethod
    async def initial_purge(bot):
        channel = bot.get_channel(radio_transmissions)
        logger.debug(f"beginning initial purge in {channel}...")
        async for message in channel.history(limit=1000, oldest_first=True):
            if message.author.bot:
                continue

            # delete message
            await message.delete()

            # replace message
            logger.debug(f"replacing message: {message.content}...")
            embed = discord.Embed(
                description=message.content, color=discord.Color.from_rgb(255, 0, 0)
            )
            await channel.send(embed=embed)

            # log message replacement
            log_channel = bot.get_channel(log_channel_id)
            embed = log_anon_message(message.content, message.author)
            await log_channel.send(embed=embed)

            # wait a sec to prevent rate limit
            await asyncio.sleep(1)
        logger.debug("initial purge is complete...")


def setup(bot):
    bot.add_cog(radio_transmission(bot))
