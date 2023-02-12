import os
import time
import logging
import asyncio
from datetime import datetime

import discord
import colorlog
from pytz import timezone
from discord.ext import commands

from constants.snowflakes import GuildID

import dotenv
dotenv.load_dotenv()


class OlzMotorsports(commands.Bot):
    def __init__(self):

        self.embed_color: discord.Color = None
        self.main_guild: discord.Guild = None

        super().__init__(
            status=discord.Status.online,
            command_prefix="m!",
            help_command=None,
            case_insensitive=False,
            intents=discord.Intents.all(),
            application_id=1069673847273574441,
        )

    async def close(self) -> None:
        logging.warning('Preparing to shut down the bot...')
        await super().close()
        logging.warning('Bot shut down!')

    async def setup_hook(self) -> None:

        # Loading up the cogs!
        cogs_to_load = [
            'cogs.roster'
        ]
        start_time = time.perf_counter()
        for cog in cogs_to_load:
            await self.load_extension(cog)
        end_time = time.perf_counter()
        print(f'Loaded {len(cogs_to_load)} cogs in {round(end_time - start_time, 2)} seconds.')

        # Starting the startup tasks
        self.loop.create_task(self.startup_tasks())

    async def startup_tasks(self) -> None:
        await self.wait_until_ready()

        # Setting up the Main Guild
        self.main_guild = self.get_guild(GuildID.MAIN.value)

        # Setting up the Embed Color
        self.embed_color = self.main_guild.get_member(self.user.id).color


bot = OlzMotorsports()


async def main():
    async with bot:
        await bot.start(os.getenv('BOT_TOKEN'))


class CustomFormatter(colorlog.ColoredFormatter):
    """override colorlog.ColoredFormatter to use an aware datetime object"""

    @staticmethod
    def converter(timestamp) -> datetime:
        dt = datetime.fromtimestamp(timestamp)
        ist_tz = timezone('Asia/Kolkata')
        return dt.astimezone(tz=ist_tz)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = ...) -> str:
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = CustomFormatter(
    '%(log_color)s%(asctime)s - %(filename)s (%(funcName)s) - %(levelname)s - %(message)s',
    datefmt='%d/%m/%y %I:%M:%S %p %Z',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'purple',
    }
)

handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    logging.critical('Keyboard interrupt detected. Bot shut down.')
