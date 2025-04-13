# from __main__ import traceback
# import datetime

import discord.ext, asyncio, re, logging
from discord.ext import commands, tasks

rate_limit = 1
role = "developer"
logger = logging.getLogger(__name__)


class guggy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clean_timer.start()

    @commands.command()
    @commands.has_role(role)
    async def cut(self, ctx, start_id, stop_id, limit=50000000):
        await ctx.message.delete()
        await self._cut(ctx.message.channel, start_id, stop_id, limit=50000000)

    async def _cut(self, channel, start_id, stop_id, limit=50000000):

        if start_id == "*":
            start_id = 0
            is_deleting = True
        else:
            start_id = int(start_id)  # Converting the id to an int
            is_deleting = False

        if stop_id == "*":
            stop_id = 0
        else:
            stop_id = int(stop_id)  # Converting the id to an int

        async for msg in channel.history(limit=limit):
            if msg.id == start_id:
                is_deleting = True

            if is_deleting:
                asyncio.create_task(msg.delete())
                await asyncio.sleep(rate_limit)

            if msg.id == stop_id:
                break

    @commands.command()
    @commands.has_role(role)
    async def clean(self, ctx, seconds=None, limit=None):
        await ctx.message.delete()
        if seconds == "*":
            await self._clean(ctx.message.channel, 0, 50000000)
        else:
            await self._clean(ctx.message.channel, seconds, limit)

    async def _clean(self, channel, seconds=600, limit=1000, delete_before=True):
        limit = int(limit)  # Converting the amount of messages to delete to an integer

        time_channel = self.bot.get_channel(1223721730246316122)  # Refined RP/ROOT/test

        if channel is None:
            return

        # Get the current time
        get_current_time_message = await time_channel.send(f"bye bye", delete_after=1)
        current_time = get_current_time_message.created_at
        # print(current_time)
        # print(datetime.datetime.combine)
        # await asyncio.sleep(rate_limit)
        # await get_current_time_message.delete() # Delete the message used for current time

        async for msg in channel.history(limit=limit):
            if (current_time - msg.created_at).total_seconds() > seconds:
                await msg.delete()
                await asyncio.sleep(rate_limit)

    def cog_unload(self):
        self.clean_timer.cancel()

    @tasks.loop(minutes=5)
    async def clean_timer(self):
        await self._clean(
            self.bot.get_channel(1208144053045166100), 1800, 1000
        )  # usagi_has_a_gun/bot
        await self._clean(
            self.bot.get_channel(1222328766932455466), 21600, 1000
        )  # Refined RP LOCKED/radio-transmissions
        await self._clean(
            self.bot.get_channel(1248112852695519242), 10800, 1000
        )  # Refined RP/server-status
        # await self._clean(self.bot.get_channel(804787907751182338), 21600, 1000) #radio-transmissions
        # await self._clean(self.bot.get_channel(855880520399454218), 300, 1000) #the-void
        # await self._clean(self.bot.get_channel(806648155264385065), 604800, 1000) #testing
        # await self._clean(self.bot.get_channel(809931339087216700), 300, 1000) #bots

    @commands.Cog.listener()
    async def on_message(self, message):
        blacklist_word = set([])
        blacklist_contains = ["free rugrat"]
        blacklist_regex = [
            "n+\s*g+\s*g+\s*r+$",
            "n+\s*g+\s*r+$",
            "n+\s*i+\s*g+\s*g+\s*r+$",
            "n+\s*g+\s*g+\s*e+\s*r+$",
            "n+\s*i+\s*g+\s*r+$",
            "n+\s*i+\s*g+\s*e+\s*r+$",
            "n+\s*i+\s*g+\s*e+\s*r+\s*s+$",
            "n+\s*i+\s*g+\s*g+\s*e+\s*r",
            "n+\s*i+\s*g+\s*g+\s*e+\s*r",
            "n+\s*i+\s*g+\s*g+\s*a+$",
            "c+\s*h+\s*i+\s*n+\s*k+$",
            "f+\s*a+\s*g+$",
            "f+\s*a+\s*g+\s*s+$",
            "f+\s*a+\s*g+\s*o+$",
            "f+\s*a+\s*g+\s*g+\s*o+$",
            "f+\s*a+\s*g+\s*g+\s*o+\s*t",
            "f+\s*a+\s*g+\s*g+\s*e+\s*t",
        ]

        yikes = self.bot.get_channel(
            1222560582759223327
        )  # message deletion log channel

        message_words = set(message.content.lower().split())
        message_text = message.content.lower()
        if (
            len(blacklist_word & message_words) > 0
            or any(substring in message_text for substring in blacklist_contains)
            or any(
                re.search(cur_regex, message_text) is not None
                for cur_regex in blacklist_regex
            )
        ):
            if (
                not message.author.bot
            ):  # if message was sent by a bot, ignore the message
                logger.info("\nMessage deleted: ", message.content, "\n", message, "\n")
                await message.delete()
                # log message details
                await yikes.send(
                    f"@here\n\n<@{message.author.id}> [{message.author} - {message.author.id}] __**just sent a message that was autodeleted!**__"
                    f"\n\n__**The message that was deleted:**__\n```{message.content}```\n__**Technical Details:**__\n```{message}```"
                )
                await asyncio.sleep(rate_limit)


def setup(bot):
    bot.add_cog(guggy(bot))
