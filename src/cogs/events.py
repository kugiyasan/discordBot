import discord
from discord.ext import commands

import asyncio
from datetime import datetime
import re
import traceback
from typing import List, Set

from cogs.utils.dbms import db


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.diff: Set[discord.Emoji] = set()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name} on {len(self.bot.guilds)} servers")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        ctx = message.channel

        try:
            msgs = await ctx.history(limit=3).flatten()

            msgSet = set(m.content.lower() for m in msgs)
            authors = set(m.author for m in msgs if not m.author.bot)

            if len(msgSet) == 1 and len(authors) == 3:
                await ctx.send(msgs[0].content)
        except discord.Forbidden:
            pass

        if re.match("^(?:great|good|nice) bot", message.content.lower()):
            await ctx.send("Aww :flushed:, thank you~~! :kissing_heart:")

        # TODO check in the db if the server enabled those features

        # dabs = ("dab", "DAB", "<0/", r"\0>", "<0/   <0/   <0/")
        # if re.search("|".join(dabs), message.content.lower()):
        #     style = "*" * random.randint(0, 3)
        #     await ctx.send(style + random.choice(dabs) + style)

        # if message.guild:
        #     dash = message.guild.get_member(399705801717186571)
        #     if ("rekt" in message.content.lower()
        #         and not message.author.bot
        #             and (not dash or dash.status != discord.Status.online)):
        #         await ctx.send("Yeah get rekt, son!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        errors = (
            asyncio.TimeoutError,
            commands.errors.NotOwner,
        )
        if ctx.command is None or isinstance(exception, errors):
            return

        errors = (
            commands.errors.MissingRequiredArgument,
            commands.errors.BadArgument,
        )
        if isinstance(exception, errors):
            await ctx.send(exception)
            await ctx.send_help(ctx.command)
            return

        errors = (
            commands.errors.NSFWChannelRequired,
            commands.errors.MissingPermissions,
            commands.errors.BotMissingPermissions,
            commands.errors.NoPrivateMessage,
            commands.errors.CommandOnCooldown,
        )
        if isinstance(exception, errors):
            await ctx.send(exception)
            return

        await self.send_report_to_owner(ctx, exception)

    async def send_report_to_owner(self, ctx: commands.Context, exception: Exception):
        print("Ignoring exception in command {}:".format(ctx.command))
        traceback.print_exception(type(exception), exception, exception.__traceback__)

        msg = "There was an unexpected error, I'll inform the bot dev, sorry~~"
        await ctx.send(msg)

        guild = ""
        if ctx.guild:
            guild = f"from {ctx.guild.name} "

        owner = (await self.bot.application_info()).owner
        text = (
            f"{ctx.author} {guild}raised an error with ***{ctx.command}***"
            + f"```{type(exception)}\n{exception}\n"
            + "".join(traceback.format_tb(exception.__traceback__))
            + "```"
        )
        await owner.send(text)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = await self.getGeneralchannel(member.guild.id)
        if channel:
            await channel.send(f"おかえりなのじゃ　Okaeri nanojya {member.mention}!")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = await self.getGeneralchannel(member.guild.id)
        if channel:
            timeInTheGuild = datetime.utcnow() - member.joined_at
            text = (
                f"See you later alligator {member.mention}.\n"
                + f"You stayed in this server for {str(timeInTheGuild)[:-3]}!"
            )
            await channel.send(text)

    @commands.Cog.listener()
    async def on_guild_emojis_update(
        self,
        guild: discord.Guild,
        before: List[discord.Emoji],
        after: List[discord.Emoji],
    ):
        diff = set(after).difference(set(before))
        if not diff:
            return

        # ! Clearly this is going to break
        # ! if two different servers updates their emojis at the same time
        self.diff.update(diff)
        diff = self.diff
        await asyncio.sleep(5)

        if self.diff != diff:
            return

        self.diff = set()

        channel = await self.getGeneralchannel(guild.id)

        await channel.send("**NEW EMOJIS**")
        newemojis = " ".join(str(x) for x in diff)
        await channel.send(newemojis)

    async def getGeneralchannel(self, guildID: int):
        channel = db.get_data("SELECT welcomebye FROM guilds WHERE id=%s", (guildID,))
        return self.bot.get_channel(channel[0][0])


def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))
