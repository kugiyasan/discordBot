import discord
from discord.ext import commands

from functools import lru_cache
import os
from typing import Optional

from cogs.utils.dbms import db

PREFIX = os.environ["DEFAULT_COMMAND_PREFIX"]


@lru_cache
def get_guild_prefix(guildID: int) -> Optional[str]:
    query = "SELECT command_prefix FROM guilds WHERE id = %s"
    result = db.get_data(query, (guildID,))
    return result[0][0]


def get_prefixes(bot: commands.Bot, message: discord.Message):
    prefix = PREFIX
    if message.guild is not None:
        prefix = get_guild_prefix(message.guild.id) or prefix

    return commands.when_mentioned_or(prefix + " ", prefix)(bot, message)
