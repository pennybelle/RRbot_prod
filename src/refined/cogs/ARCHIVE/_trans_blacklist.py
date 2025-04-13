import discord.ext
from discord.ext import commands

# from __main__ import traceback


class trans_blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.debugging = True
        self.COLOR = discord.Color.from_rgb(243, 169, 206)
        self.BLACKLISTED_WORDS = "blacklisted_words.txt"

    @commands.slash_command(description="All supported languages for /translate")
    async def blacklistadd(self, ctx, word):
        try:
            # read db
            with open(self.BLACKLISTED_WORDS, "r") as blacklist:
                if word.lower() in blacklist.read():
                    embed = discord.Embed(
                        title="Word is already in blacklist",
                        description="Ignoring request",
                        color=self.COLOR,
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

            # add word to db
            with open(self.BLACKLISTED_WORDS, "a") as blacklisted_words:
                if self.debugging:
                    print(f"adding {word} to blacklist...")
                    blacklisted_words.write(f"{word}\n")

            # send response to confirm
            embed = discord.Embed(
                title="Successfully added to blacklist",
                description=f"{word} was added to blacklist",
                color=self.COLOR,
            )
            embed.set_footer(text="This change should take immediate effect")
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Something went wrong", description=e, color=self.COLOR
            )
            await ctx.respond(embed=embed, ephemeral=True)


    @commands.slash_command(description="All supported languages for /translate")
    async def blacklistremove(self, ctx, word):
        try:
            # if word is in db, delete word
            with open(self.BLACKLISTED_WORDS, "r") as blacklist:
                data = blacklist.read()
                if self.debugging:
                    print(f"blacklist data: {data}")

            # if word is not in db
            if word.lower() not in data:
                embed = discord.Embed(
                    title="Could not find word",
                    description=f"{word} was not found in blacklist",
                    color=self.COLOR,
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # if word is in db
            with open(self.BLACKLISTED_WORDS, "w") as blacklist:
                data = data.replace(f"{word}\n", "")
                if self.debugging:
                    print(f"blacklist data after removal: {data}")
                blacklist.write(data)
                embed = discord.Embed(
                    title="Deletion request successful",
                    description=f"{word} was removed from blacklist",
                    color=self.COLOR,
                )
                embed.set_footer(text="This change should take immediate effect")
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Something went wrong", description=e, color=self.COLOR
            )
            await ctx.respond(embed=embed, ephemeral=True)


    @commands.slash_command(description="All supported languages for /translate")
    async def blacklist(self, ctx):
        try:
            # if word is in db, delete word
            with open(self.BLACKLISTED_WORDS, "r") as blacklist:
                blacklist_entries = blacklist.read().split('\n')
                blacklist_entries = '\n-'.join(blacklist_entries)
                if self.debugging: print(f"blacklist data: {blacklist_entries}")

            if blacklist_entries:
                if self.debugging: print(f"blacklist has data...")
                embed = discord.Embed(
                    title="Blacklist entries:",
                    description=blacklist_entries,
                    color=self.COLOR,
                )
                embed.set_footer(text="Use /blacklistadd or /blacklistremove to change entries.")
                await ctx.respond(embed=embed, ephemeral=True)

            else:
                if self.debugging: print(f"blacklist has no data...")
                embed = discord.Embed(
                    title="The blacklist is currently empty",
                    description="Use /blacklistadd or /blacklistremove to change blacklist entries",
                    color=self.COLOR,
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Something went wrong", description=e, color=self.COLOR
            )
            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(trans_blacklist(bot))
