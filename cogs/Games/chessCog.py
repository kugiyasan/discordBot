import discord
from discord.ext import commands

from cogs.Games.chess.board import Board, GameError
import asyncio

class ChessCog(commands.Cog, name='Chess'):
    def __init__(self, bot):
        self.bot = bot
        self.playingUsers = set()

    @commands.command(hidden=True)
    async def nerds(self, ctx):
        if not self.playingUsers:
            await ctx.send('Nobody is playing chess')
            return
            
        players = ', '.join(p.name for p in self.playingUsers)
        await ctx.send('Here is/are the player(s) currently playing chess: ' + players)

    @commands.command()
    async def chess(self, ctx, adversary: discord.Member, mode='full'):
        """Play chess with someone mode='full' or 'pawn'"""
        if adversary.bot:
            await ctx.send("You can't play versus a bot, at least for now")
            return

        if ctx.author in self.playingUsers or adversary in self.playingUsers:
            await ctx.send("You've already started a game, please stop it first!")
            return
        self.playingUsers.update((ctx.author, adversary))
        
        turn = 0
        if mode == 'full':
            game = Board()
        elif mode == 'pawn':
            game = Board(onlyPawn=True)
        else:
            await ctx.send('Unknown game mode')
            return

        board = await ctx.send(str(game))

        def checkresponse(m):
            if turn == 1:
                return (m.author == ctx.author
                    and m.channel == ctx.channel)
            return (m.author == adversary
                and m.channel == ctx.channel)
        
        # MAIN LOOP
        while 1: # NOT CHECKMATE
            try:
                m = await self.bot.wait_for(
                    'message',
                    timeout=60.0,
                    check=checkresponse
                )
            except asyncio.TimeoutError:
                await ctx.send('Stopping chess, timeout expired')
                await self.endGame(ctx, adversary, (turn, str(game)))
                return

            if m.content.lower() == 'stop':
                await self.endGame(ctx, adversary, (turn, str(game)))
                return

            msg = m.content.split()
            if len(msg) != 2:
                await ctx.send('There should be 2 arguments!', delete_after=10.0)
                continue

            try:
                gameState = game.movePiece(*msg)
            except GameError as errorMsg:
                await ctx.send(str(errorMsg), delete_after=10.0)
                continue
            except:
                await ctx.send('Unknown error\n' + str(errorMsg))
                continue
            
            if gameState:
                await self.endGame(ctx, adversary, gameState)
                return

            await board.delete()
            player = (ctx.author, adversary)[turn]
            board = await ctx.send(str(game) + f"\nit's {player.name}'s turn!")
            turn = (turn + 1) % 2
        
    async def endGame(self, ctx, adversary, gameState):
        winner = (ctx.author.name, adversary)[gameState[0]]
        # await ctx.send(gameState[1] + f'\n{winner} wins!')
        await ctx.send(f'\n{winner} wins!')
        self.playingUsers -= {ctx.author, adversary}


def setup(bot):
    bot.add_cog(ChessCog(bot))