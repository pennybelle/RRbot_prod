import discord, googletrans, logging, re
from discord.ext import commands
from difflib import SequenceMatcher
from pathlib import Path
from cleantext import remove_emoji
from . import _constants as c

# TODO: add character limit for translation, omit code blocks, use reaction to translate messages
# TODO: test 'hmu' to fis 'lus' error
# TODO: test /translate gen imi to japanese for list index out of range error

logger = logging.getLogger(__name__)
blacklist = Path.cwd().joinpath(
    "src", "refined", "cogs", "core", "blacklisted_words.txt"
)


def create_embed(
    title,
    description,
    pronunciation=None,
    footer=None,
    color=discord.Color.from_rgb(243, 169, 206),
    thumbnail=False,
):
    # send embed, pronunciation not always needed
    embed = discord.Embed(
        title=title,
        description=description + pronunciation if pronunciation else description,
        color=color,
    )
    if footer:
        embed.set_footer(text=footer)
    if thumbnail:
        embed.set_thumbnail(url="https://i.imgur.com/NBHsCzm.png")
    # if image: embed.set_image(url='attachment://resources/translate.png')
    return embed


def format_text(message):
    # remove unicode emojis
    message = remove_emoji(message)
    # remove discord emojis
    message = re.sub(c.DISCORD_EMOJI, "", message)
    # replace code blocks with token
    message = re.sub(c.CODE_BLOCK, "<code>", message)
    # replace email addresses with token
    message = re.sub(c.EMAIL, "<email>", message)
    # replace phone numbers with token
    message = re.sub(c.PHONE_NUMBER, "<phone>", message)
    # replace urls with token
    message = re.sub(c.URL, "<url>", message)
    # reformat and make message lowercase
    message = " ".join(message.split("\n")).lower()

    return message


def word_is_in_blacklist(message):
    logger.info("checking blacklist...")

    # remove symbols for check
    message = re.sub(c.SYMBOLS, "", message)

    # read blacklist and format as list
    with open(blacklist, "r", encoding="utf-8") as f:
        blacklisted_words = f.read()
        blacklisted_words = list(filter(None, blacklisted_words.lower().split("\n")))

    # check message as a whole against blacklist entries
    if message in blacklisted_words:
        return blacklisted_words
    logger.info("message not in blacklist...")

    # format lists of words from blacklist and message
    message = message.lower().split()

    # iterate entire blacklist by word until word is found, then return blacklist contents
    for word in message:

        # check if word in blacklist
        if word in blacklisted_words:
            # when word matches with blacklisted word
            return blacklisted_words
        logger.info("word not in blacklist...")

    # if word is not found return False
    return False


def similarity_ratio(first, second):
    ratio = SequenceMatcher(None, first, second).ratio()
    return float(ratio)


class trans_auto(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()
        self.NATIVE_LANGUAGE = "english"  # default lang to not be translated
        self.REACTION_EMOJI = "<:translate:1245807067131023521>"
        self.EMOJI_ARROW = "<:translatedto:1245807125578649662>"
        self.LANGUAGES = googletrans.LANGUAGES  # all supported langs in a dict
        self.LANGCODES = googletrans.LANGCODES  # reverse of self.LANGUAGES
        self.CONFIDENCE_THRESHOLD = 0.85  # if confidence lower than this then return
        self.SIMILARITY_THRESHOLD = 0.70  # similarity threshold for translated text

    def parse_pronunciation(self, message, translation):
        # get list containing pronunciation
        pronunciation_list = translation.extra_data["translation"][-1][::-1]
        logger.info(f"pronunciation before parse: {pronunciation_list}")  # info print

        # seperate list into formatted strings only
        pronunciation_list = [
            string for string in pronunciation_list if type(string) is str
        ]

        msg = message.lower()
        translated = translation.text.lower()
        pronunciation = None

        # if no pronuncation options return None
        if len(pronunciation_list) == 0:
            return None

        # if only one available and doesnt match msg or translated return that one option else return None
        if len(pronunciation_list) == 1:
            if pronunciation_list[0] != msg and pronunciation_list[0] != translated:
                return pronunciation_list[0]
            else:
                return None

        # parse pronunciations for whichever is least similar to the translated message
        if similarity_ratio(translated, pronunciation_list[0]) > similarity_ratio(
            msg, pronunciation_list[0]
        ):
            pronunciation = pronunciation_list[0]

        else:
            pronunciation = pronunciation_list[1]

        # return None if msg or translated is same as pronunciation to reduce repeated text in embed
        if pronunciation == msg or pronunciation == translated:
            return None

        return pronunciation

    def detect_lang(self, message):
        # remove format tokens for language detection only
        detected = re.sub(r"<url>|<email>|<phone>|<code>", "", message.content.lower())

        # detect language of message
        detected = self.translator.detect(detected)
        logger.info(f"detected: {detected}")  # info print
        confidence = detected.confidence

        # if detection picks up 2 potential languages
        if type(detected.lang) is list:
            # assign lang to first item in lang list to use as translation src
            lang = detected.lang[0].lower()
            # format for embed response
            translated_from = f"{self.LANGUAGES[lang[0]]}/{self.LANGUAGES[lang[1]]}"
        else:
            lang = detected.lang.lower()
            translated_from = f"{self.LANGUAGES[lang]}"

        return lang, confidence, translated_from

    def should_translate(self, message, lang, confidence):
        # if lang == NATIVE_LANGUAGE then dont translate
        if lang == self.LANGCODES[self.NATIVE_LANGUAGE]:
            logger.info(
                f"lang == NATIVE_LANGUAGE ({lang}), aborting translation..."
            )  # info print
            return False  # guard clause

        # check blacklisted_words.txt
        # (prevents edge cases not able to be easily caught by the rest of the checks)
        # TODO: We should add this to the Database
        if word_is_in_blacklist(message):
            logger.info("word is in blacklist, aborting translation...")
            return False

        # if not >= the CONFIDENCE_THRESHOLD of NATIVE_LANGUAGE then dont translate
        if float(confidence) < float(self.CONFIDENCE_THRESHOLD):
            logger.info(
                f"lang = {lang}\n"
                f"confidence < THRESHOLD ({confidence}), aborting translation..."
            )  # info print
            return False  # guard clause

        return True

    def should_add_reaction(self, message, translation):
        # if translation == message, dont translate
        if translation.text == message.content:
            logger.info("translation == message, aborting translation...")  # info print
            return False

        # check similarity between original and translated text, dont translate if too similar
        similarity = similarity_ratio(message.content, translation.text)
        if similarity > self.SIMILARITY_THRESHOLD:
            logger.info(
                f"similarity > THRESHOLD, aborting translation... ({similarity})"
            )
            return False  # guard clause

        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        # initial checks
        if message.author.bot:
            return  # guard clause

        # debug chunk seperator
        logger.info("---")

        # returns formatted text
        message.content = format_text(message.content)

        # only continue if all pre translation checks pass
        lang, confidence, translated_from = self.detect_lang(message)
        should_translate = self.should_translate(message.content, lang, confidence)
        if should_translate is False:
            return

        # translate message to native language
        translation = self.translator.translate(
            message.content, src=lang.lower(), dest=self.LANGCODES[self.NATIVE_LANGUAGE]
        )
        translation.text = translation.text.lower()

        # if all checks pass then add reaction
        should_add_reaction = self.should_add_reaction(message, translation)
        if should_add_reaction:
            await message.add_reaction(self.REACTION_EMOJI)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji

        # initial checks
        if user.bot:
            return  # guard clause

        if str(emoji) != self.REACTION_EMOJI:
            return  # guard clause

        try:
            # clean up text
            message.content = format_text(message.content)

            # remove reactions
            await message.clear_reaction(emoji)

            # translate message to native language
            logger.info("translating...")  # info print
            lang, confidence, translated_from = self.detect_lang(message)
            translation = self.translator.translate(
                message.content,
                src=lang.lower(),
                dest=self.LANGCODES[self.NATIVE_LANGUAGE],
            )
            translation.text = translation.text.lower()
            logger.info(f"translation: {translation.text}")

            # parse pronunciation from extra_data
            pronunciation = self.parse_pronunciation(message.content, translation)
            logger.info(f"pronunciation after parse: {pronunciation}")

            # format and create embed object
            description = f"**{translation.text}**"
            description += (
                f"\n- pronounced: {pronunciation.lower()}" if pronunciation else ""
            )
            description += (
                f"\n- translated from {translated_from} to {self.NATIVE_LANGUAGE}"
            )
            embed = create_embed(
                title=f"{message.content} {self.EMOJI_ARROW}",
                description=description,
                thumbnail=True,
            )

            # send embed as untagged reply to message
            await message.reply(embed=embed, mention_author=False)

        # if error, send error message to channel that caused it
        except Exception as e:
            logger.info(e)
            embed = create_embed(
                title="Something went wrong with the auto translator!",
                description=f"Please contact a developer for support.\nTraceback: ```{e}```",
                footer="Sorry! This message auto deletes after 30 seconds.",
            )
            await message.channel.send(embed=embed, delete_after=30)

    @commands.slash_command(description="Example: /translate hello world to japanese")
    async def translate(self, ctx, message, to):
        # find and omit any emojis
        message = format_text(message)

        # auto detect language of message for translation
        new_lang = str(to).lower()
        old_lang = self.translator.detect(message).lang.lower()
        logger.info(f"new_lang: {new_lang}\nold_lang: {old_lang}")

        # initial checks
        if new_lang in ["chinese traditional", "traditional chinese", "mandarin"]:
            new_lang = "chinese (traditional)"
        elif new_lang in ["chinese", "simplified chinese", "chinese simplified"]:
            new_lang = "chinese (simplified)"
        elif new_lang in ["kurdish", "kurmanji"]:
            new_lang = "kurdish (kurmanji)"
        elif new_lang in ["myanmar", "burmese"]:
            new_lang = "myanmar (burmese)"

        try:
            # translate and parse translation for pronunciation
            translation = self.translator.translate(
                message, src=old_lang, dest=self.LANGCODES[new_lang]
            )
            pronunciation = self.parse_pronunciation(message, translation)
            logger.info(f"pronunciation after parse: {pronunciation}")

            # format and create embed object
            description = f"**{translation.text}**"
            description += (
                f"\n- pronounced: {pronunciation.lower()}" if pronunciation else ""
            )
            description += (
                f"\n- translated from {self.LANGUAGES[old_lang]} to {new_lang}"
            )
            embed = create_embed(
                title=f"{message} {self.EMOJI_ARROW}",
                description=description,
                thumbnail=True,
            )

            # send embed as a reply to command
            await ctx.respond(embed=embed)

        except KeyError or ValueError:
            embed = create_embed(
                title="Not a supported language!",
                description="Please enter a supported language.",
                footer="Type /languages to get a list of supported languages.",
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            logger.info(e)
            embed = create_embed(
                title="Something went wrong!",
                description=f"Please contact a developer for support.\nTraceback: {e}",
                footer="Sorry! This bot is still in development <3",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        description="All supported languages for auto translator and /translate"
    )
    async def languages(self, ctx):
        # set string to fill with data from googletrans languages dict
        languages = ""

        # parse languages from db and add to string
        for lang in self.LANGUAGES.items():
            languages += f"\n- {lang[1].title()}"

        try:
            # send language list as embed
            embed = create_embed(
                title="Supported Languages for Translation:",
                description=languages.title(),
                footer="Not case sensitive but must otherwise be entered as seen",
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            logger.info(e)
            embed = create_embed(
                title="Something went wrong!",
                description=f"Please contact a developer for support.\nTraceback: {e}",
                footer="Sorry! This bot is still in development <3",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(description="All supported languages for /translate")
    @commands.has_permissions(manage_messages=True)
    async def blacklist(self, ctx):
        try:
            # read blacklist db
            with open(blacklist, "r", encoding="utf-8") as f:
                blacklist_entries = f.read().strip().split("\n")
                logger.info(f"blacklist data: {blacklist_entries}")

            # remove blank entries
            blacklist_entries = list(filter(None, blacklist_entries))

            # if word is in db, delete word
            if blacklist_entries[0] != "":
                blacklist_entries = "- " + "\n- ".join(blacklist_entries)
                logger.info(f"blacklist has data...")
                embed = create_embed(
                    title="Blacklist entries:",
                    description=blacklist_entries,
                    footer="Use /blacklistadd or /blacklistremove to change entries.",
                )
                await ctx.respond(embed=embed, ephemeral=True)

            else:
                logger.info(f"blacklist has no data...")
                embed = create_embed(
                    title="The blacklist is currently empty",
                    description="Use /blacklistadd or /blacklistremove to change blacklist entries",
                    footer="Changes to the blacklist take immediate effect.",
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            logger.info(e)
            embed = create_embed(
                title="Something went wrong!",
                description=f"Please contact a developer for support.\nTraceback: {e}",
                footer="Sorry! This bot is still in development <3",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        description="Add a word to be blacklisted from the auto translator"
    )
    @commands.has_permissions(manage_messages=True)
    async def blacklistadd(self, ctx, word):
        try:
            # check blacklist
            if word_is_in_blacklist(word):
                embed = create_embed(
                    title="Word is already in blacklist", description="Ignoring request"
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # read blacklist to append word
            with open(blacklist, "r", encoding="utf-8") as f:
                logger.info("reading blacklist...")
                blacklisted_words = f.read().split("\n")

            # append word to blacklist
            blacklisted_words.append(word)

            # add word to db
            with open(blacklist, "w") as f:
                logger.info(f"adding {word} to blacklist...")
                f.write("\n".join(blacklisted_words))

            # send response to confirm
            embed = create_embed(
                title="Successfully added to blacklist",
                description=f"{word} was added to blacklist",
                footer="This change should take immediate effect",
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            logger.info(e)
            embed = create_embed(
                title="Something went wrong!",
                description=f"Please contact a developer for support.\nTraceback: {e}",
                footer="Sorry! This bot is still in development <3",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        description="Remove a word from the auto translator blacklist"
    )
    @commands.has_permissions(manage_messages=True)
    async def blacklistremove(self, ctx, word):
        try:
            # if word is in db, delete word
            word = word.lower()
            word_in_blacklist = word_is_in_blacklist(word)
            logger.info(f"blacklist contents: {word_in_blacklist}")
            if word_in_blacklist:
                i = word_in_blacklist.index(word)
                word_in_blacklist.pop(i)
                logger.info(f"blacklist contents after removal: {word_in_blacklist}")
                with open(blacklist, "w") as f:
                    f.write("\n".join(word_in_blacklist) if word_in_blacklist else "")
                    embed = create_embed(
                        title="Deletion request successful",
                        description=f"{word} was removed from blacklist",
                        footer="This change should take immediate effect",
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                return

            # if word is not in db
            embed = create_embed(
                title="Deletion request successful",
                description=f"{word} was removed from blacklist",
                footer="No need to remove! :3",
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            logger.info(e)
            embed = create_embed(
                title="Something went wrong!",
                description=f"Please contact a developer for support.\nTraceback: {e}",
                footer="Sorry! This bot is still in development <3",
            )
            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(trans_auto(bot))
