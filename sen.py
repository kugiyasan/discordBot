# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
# https://github.com/runarsf/rufus

import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

from cogs.utils.deleteMessage import deleteMessage
from cogs.utils.dbms import conn, cursor

load_dotenv()


async def prefixes(bot: commands.Bot, message: discord.Message):
    prefix = os.environ["DEFAULT_COMMAND_PREFIX"]
    if message.guild != None:
        try:
            with conn:
                cursor.execute(
                    "SELECT command_prefix FROM guilds WHERE id = %s", (message.guild.id,))
                temp = cursor.fetchone()
                if temp and temp[0]:
                    prefix = temp[0]
        except:
            print("Wasn't able to communicate with the database")

    return commands.when_mentioned_or(prefix + " ", prefix)(bot, message)

prefix = os.environ["DEFAULT_COMMAND_PREFIX"]
bot = commands.Bot(command_prefix=prefixes,
                   activity=discord.Game(name=f"{prefix} help | {prefix} about"))


def getExtensions():
    for path in ("cogs", "cogs/Games"):
        for f in os.listdir(path):
            if f[-2:] != "py":
                continue
            pathname = os.path.join(path, f)
            if os.path.isfile(pathname):
                yield pathname[:-3].replace("/", ".").replace("\\", ".")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} on {len(bot.guilds)} servers")


@bot.command(hidden=True, aliases=["rl"])
@commands.is_owner()
async def reload(ctx: commands.Context):
    """Reloads the bot extensions without rebooting the entire program"""
    try:
        for ext in getExtensions():
            try:
                bot.reload_extension(ext)
            except commands.errors.ExtensionNotLoaded:
                bot.load_extension(ext)
    except:
        await ctx.send("Reloading failed")
        raise

    await ctx.message.add_reaction("✅")
    print("\033[94mReloading successfully finished!\033[0m\n")


@bot.command(hidden=True)
@commands.is_owner()
async def logout(ctx: commands.Context):
    await ctx.message.add_reaction("✅")
    await bot.logout()


if __name__ == "__main__":
    for ext in getExtensions():
        bot.load_extension(ext)

    bot.run(os.environ["DISCORD_TOKEN"])
