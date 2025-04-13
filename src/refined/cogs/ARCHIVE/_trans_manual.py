import discord.ext, googletrans
from discord.ext import commands
from __main__ import traceback


class trans_manual(commands.Cog):

    # TODO: add reaction to allow controlled auto translations
    # reaction is added to a message that is not self.LANGUAGE
    # if reaction is clicked by anyone, message is translated

    def __init__(self, bot):
        self.bot = bot
        self.debugging = True
        self.translator = googletrans.Translator()
        self.COLOR = discord.Color.from_rgb(243, 169, 206)
        self.LANGUAGES = googletrans.LANGUAGES  # all supported langs in a dict
        self.LANGCODES = googletrans.LANGCODES  # reverse of self.gl

    def parse_pronunciation(self, message, translation):
        # get list containing pronunciation
        if self.debugging:
            print(f"translation: {translation}")
        if self.debugging:
            print(f"extra_data: {translation.extra_data}")  # debug print
        pronunciation_list = translation.extra_data["translation"][-1][::-1]
        if self.debugging:
            print(f"pronunciation before parse: {pronunciation_list}")  # debug print

        # find string in list
        for i in pronunciation_list:
            if type(i) is not str:
                continue  # guard clause

            # if string == message or string == translated message, set to None and move on
            if i.lower() == message.lower() or i.lower() == translation.text.lower():
                if self.translator.detect(i).lang != translation.src:
                    pronunciation = None

            # otherwise format string and break to return
            else:
                pronunciation = i
                break

        if self.debugging:
            print(f"pronunciation after parse: {pronunciation}")  # debug print
        return pronunciation

    @commands.slash_command(
        description=("Example: `/translate hello world to japanese`")
    )
    async def translate(self, ctx, message, to):
        # auto detect language of message for translation
        old = self.translator.detect(message).lang

        # initial checks
        to = str(to).lower()
        if to in ["chinese traditional", "traditional chinese", "mandarin"]:
            to = "chinese (traditional)"
        elif to in ["chinese", "simplified chinese", "chinese simplified"]:
            to = "chinese (simplified)"
        elif to in ["kurdish", "kurmanji"]:
            to = "kurdish (kurmanji)"
        elif to in ["myanmar", "burmese"]:
            to = "myanmar (burmese)"

        try:
            # translate and parse translation for pronunciation
            translation = self.translator.translate(
                message, src=old, dest=self.LANGCODES[to]
            )
            pronunciation = self.parse_pronunciation(message, translation)
            if pronunciation:
                pronunciation = f"\npronounced: {pronunciation.lower()}"

            # send embed, sometimes there is no pronunciation
            embed = discord.Embed(
                title=f"{message}:",
                description=(
                    f'"**{translation.text}**"'
                    f'{pronunciation if type(pronunciation) is str else ""}'
                ),
                color=self.COLOR,
            )
            embed.set_footer(text=f"translated from {self.LANGUAGES[old]} to {to}")
            await ctx.respond(embed=embed)

        except KeyError or ValueError:
            embed = discord.Embed(
                title="Not a supported language!",
                description="Please enter a supported language.",
                color=self.COLOR,
            )
            embed.set_footer(
                text=("Type /languages to get a list of supported languages.")
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            await traceback(ctx, e)
            embed = discord.Embed(
                title="Something went wrong!",
                description=f"Please contact a developer for support.\nTraceback: {e}",
                color=self.COLOR,
            )
            embed.set_footer(text=("Sorry! This bot is still in development <3"))
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(description="All supported languages for /translate")
    async def languages(self, ctx):
        # set string to fill with data from googletrans languages dict
        languages = ""

        # parse languages from db and add to string
        for lang in self.LANGUAGES.items():
            languages += f"\n- {lang[1].title()}"

        try:
            # send language list as embed
            embed = discord.Embed(
                title="Supported Languages for Translation:",
                description=languages.title(),
                color=self.COLOR,
            )
            embed.set_footer(
                text="Not case sensitive but must otherwise be entered as seen"
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            await traceback(ctx, e)


def setup(bot):
    bot.add_cog(trans_manual(bot))
