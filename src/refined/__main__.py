"""
TO INSTALL:

pip install py-cord

"""

import os, sys, discord, logging
from discord.ext import commands
from refined.utilities.logging_utils import setup_logger
from refined.cogs.core.server_settings import Settings
from refined.cogs.bug_report import bug_report as br
from refined.cogs.radio_transmission import radio_transmission as rt

COGS_ROOT_PATH = os.path.join(os.path.dirname(__file__), "cogs")

logger = logging.getLogger(__name__)
prefix = "~"
intents = discord.Intents.all()

# This sets the prefix to use for commands.
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), intents=intents)


# In this function, we load all the files from the Cogs folder.
# Cogs are just files that hold our commands.
def load_cogs():
    """
    Loads the directories under the /cogs/ folder,
    then digs through those directories and loads the cogs.
    """
    logger.info("Loading Cogs...")
    failed_to_load = []
    # for directory in os.listdir(COGS_ROOT_PATH):
    #     if directory.startswith("_"):
    #         logger.debug(f"Skipping {directory} as it is a hidden directory.")
    #         continue
    #     if directory.startswith("debug") and not logger.level == logging.DEBUG:
    #         logger.debug(f"Skipping {directory} as it is not the debug cog.")
    #         continue

    # cog_subdir_path = os.path.join(COGS_ROOT_PATH, directory)
    for file in os.listdir(COGS_ROOT_PATH):
        if file.endswith(".py") and not file.startswith("_"):
            # try:
            cog_path = os.path.join(COGS_ROOT_PATH, file)
            # logger.debug(f"Loading Cog: {cog_path}")
            try:
                if len(sys.argv) > 1:
                    bot.load_extension(f"cogs.{file[:-3]}")
                else:
                    bot.load_extension(f"refined.cogs.{file[:-3]}")
                logger.info(f"Loaded Cog: {cog_path}")
            except Exception as e:
                logger.warning(
                    "Failed to load: {%s}.{%s}, {%s}", COGS_ROOT_PATH, file, e
                )
                failed_to_load.append(f"{file[:-3]}")
    if failed_to_load:
        logger.warning(
            f"Cog loading finished. Failed to load the following cogs: {', '.join(failed_to_load)}"
        )
    else:
        logger.info("Loaded all cogs successfully.")


# In this function, we use an argument or env file to load the Bot-Token.
def load_token_and_run():
    server_settings_path = "./resources"
    if server_settings_path:
        bot.server_settings = Settings(server_settings_path)  # type: ignore
    if len(sys.argv) > 1:
        TOKEN = sys.argv[1]
        bot.run(TOKEN)
    else:
        bot.run(os.getenv("DISCORD_TOKEN"))


@bot.event
async def on_ready():
    logger.info(f"{bot.user} [{bot.user.id}] is connected to the following guilds:")
    for guild in bot.guilds:
        logger.info(f"\t- {guild.name}(id: {guild.id})")

    # purge all user messages in bug-report and radio-transmission at startup
    await br.initial_purge(bot)
    await rt.initial_purge(bot)


def main():
    setup_logger(
        level=int(os.getenv("LOGGING_LEVEL", 20)),
        stream_logs=bool(os.getenv("STREAM_LOGS", False)),
    )
    load_cogs()
    load_token_and_run()


if __name__ == "__main__":
    main()
