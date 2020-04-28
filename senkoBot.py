# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
# https://github.com/nobodyme/reddit-fetch.git
# https://github.com/runarsf/rufus

#* Stubs (e.g. member: discord.Member) helps autocomplete

import logging

import discord
from discord.ext import commands

try:
    from myToken import token
except:
    from yourToken import token

prefixes = ['XD ', 'Xd ', 'xD ', 'xd ', 'XD', 'Xd', 'xD', 'xd']
description = '''JOACHIM IS THE MASTER OF THE UNIVERSE'''
occupation = discord.Activity(type=discord.ActivityType.playing,
                                name='with Fox Goddess')

bot = commands.Bot(command_prefix=prefixes,
                    description=description,
                    activity=occupation)

extensions = ('cogs.admin',
            'cogs.cancer',
            'cogs.dev',
            'cogs.events',
            'cogs.reddit',
            'cogs.voice')
            

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name} running on {len(bot.guilds)} servers')

    for g in bot.guilds:
        logging.info(g.name + ' member_count: ' + str(g.member_count))
    print()

@bot.command(hidden=True)
@commands.is_owner()
async def reloadExt(ctx: commands.Context):
    '''Reloads the bot extensions without rebooting the entire program'''
    await ctx.message.delete()
    for ext in extensions:
        bot.reload_extension(ext)

    print('\033[94mReloading successfully finished!\033[0m\n')

@bot.command(hidden=True)
@commands.is_owner()
async def logout(ctx: commands.Context):
    await ctx.message.delete()
    logging.info('\nlogging out...')
    await bot.logout()

if __name__ == "__main__":
    logging.basicConfig(filename='logs/example1.log', level=logging.INFO)
    
    for ext in extensions:
        bot.load_extension(ext)

    bot.run(token)