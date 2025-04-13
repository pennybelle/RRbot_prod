import discord.ext, googletrans, logger
from discord.ext import commands
from difflib import SequenceMatcher


def similarity_check(first, second):
    ratio = SequenceMatcher(None, first, second).ratio()
    logger.debug(f"Similarity between {first} and {second} = {ratio}")  # debug print
    return ratio


def trans_embed(
        native_lang
        , detected_lang
        , confidence
        , similarity
        , message_content
        , translation_text
        , pronunciation
        , color
) -> discord.Embed:
    # send results of translation as embed
    embed = discord.Embed(
        title=f"{message_content}:",
        description=(
            f'"**{translation_text}**"'
            f'{pronunciation if type(pronunciation) is str else ""}'
        ),
        color=color,
    )
    embed.set_footer(
        text=(
            f"translated from {detected_lang} to {native_lang}\n"
            f"auto detection confidence: {confidence}%\n"
            f"similarity to original text: {similarity:.2}%"
        )
    )


def word_is_in_blacklist(database_lol, message_content):
    with open(database_lol, "r") as blacklisted_words:
        logger.debug("checking blacklist...")
        for word in message_content.lower().split():
            if word in blacklisted_words.read().lower():
                logger.debug("word is blacklisted, aborting translation...")
                return True
        logger.debug("message does not contain any blacklisted words...")
        return False

def more_than_one_language_detected(lang, confidence, threshhold):
    if isinstance(lang, list):
        logger.debug(f"lang is list...")
        if confidence[0] < threshhold:
            return False # guard clause
    return True

class trans_auto(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.debugging = True
        self.translator = googletrans.Translator()
        self.COLOR = discord.Color.from_rgb(243, 169, 206)
        self.NATIVE_LANGUAGE = "english"  # default lang to not be translated
        self.LANGUAGES = googletrans.LANGUAGES  # all supported langs in a dict
        self.LANGCODES = googletrans.LANGCODES  # reverse of self.gl
        self.CONFIDENCE_THRESHOLD = 0.85  # if confidence lower than this & not multi_lang then return
        self.SIMILARITY_THRESHOLD = 0.75  # similarity threshold for translated text
        self.BLACKLISTED_WORDS = "blacklisted_words.txt"

    def parse_pronunciation(self, message, translation):
        # get list containing pronunciation
        logger.debug(f"translation: {translation}")  # debug print
        logger.debug(f"extra_data: {translation.extra_data}")  # debug print
        pronunciation_list = translation.extra_data["translation"][-1][::-1]
        logger.debug(f"pronunciation before parse: {pronunciation_list}")  # debug print

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

        logger.debug(f"pronunciation after parse: {pronunciation}")  # debug print
        return pronunciation

    @commands.Cog.listener()
    async def on_message(self, message):
        # initial checks
        if message.author.bot:
            return  # guard clause
        if message.channel.id in self.IGNORE_CHANNELS.values():
            return  # guard clause
        # check blacklisted_words.txt (prevents edge cases not able to be easily caught by the rest of the checks)
        # TODO: We should add this to the Database
        if word_is_in_blacklist(self.BLACKLISTED_WORDS, message.content):
            return

        try:
            logger.debug("---")  # debug print

            detected_language = None

            # detect language of message
            detected = self.translator.detect(message.content)
            logger.debug(f"detected = {detected}")  # debug print
            lang = detected.lang

            # if detection picks up 2 potential languages
            if more_than_one_language_detected(
                    lang, detected.confidence, self.CONFIDENCE_THRESHOLD
            ):
                # extract confidence value from list
                detected.confidence = detected.confidence[0]

                # self.gl keys dont match with API dict from detect(), this fixes that
                lang = [str(l).lower() for l in lang]

                # format for embed response
                detected_language = (f"{self.LANGUAGES[lang[0]]}/"
                                     f"{self.LANGUAGES[lang[1]]}")

            # if NATIVE_LANGUAGE then dont translate
            elif lang == self.LANGCODES[self.NATIVE_LANGUAGE]:
                logger.debug(f"lang == NATIVE_LANGUAGE ({lang}), "
                             f"aborting translation...")  # debug print
                return  # guard clause

            # if within the CONFIDENCE_THRESHOLD of NATIVE_LANGUAGE then dont translate
            elif detected.confidence < self.CONFIDENCE_THRESHOLD:
                logger.debug(
                    f"lang = {lang}\nconfidence < THRESHOLD ({detected.confidence}), aborting translation..."
                )  # debug print
                return  # guard clause


            # preformat
            lang = lang.lower()
            if detected_language is None:
                detected_language = f"{self.LANGUAGES[lang]}"
            detected.confidence *= 100

            # translate message to native language
            logger.debug("translating...")  # debug print
            translation = self.translator.translate(
                message.content
                , src=lang
                , dest=self.LANGCODES[self.NATIVE_LANGUAGE]
            )
            logger.debug(f"translation = {translation}")  # debug print

            # if translation == message, dont translate
            if translation.text.lower() == message.content.lower():
                logger.debug(
                    "translation == message, aborting translation..."
                )  # debug print
                return

            # check similarity between original and translated text, dont translate if too similar
            similarity = self.similarity_check(
                message.content.lower(), translation.text.lower()
            )
            if similarity > self.SIMILARITY_THRESHOLD:
                logger.debug(
                    f"similarity > THRESHOLD"
                    f", aborting translation... ({similarity})"
                )
                return  # guard clause

            # parse pronunciation from extra_data
            pronunciation = self.parse_pronunciation(message.content, translation)
            if pronunciation:
                pronunciation = f"\npronounced: {pronunciation.lower()}"

            await message.channel.send(
                embed=trans_embed(
                    self.NATIVE_LANGUAGE
                    , detected_language
                    , detected.confidence
                    , similarity
                    , message.content
                    , translation.text
                    , pronunciation
                    , self.COLOR
                )
            )

        # if error, send error message to channel that caused it
        except Exception as e:
            logger.debug(e)


def setup(bot):
    bot.add_cog(trans_auto(bot))
