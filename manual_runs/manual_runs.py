import discord
import re
from discord.ext import tasks
from redbot.core import Config, checks, commands

from redbot.core.commands.context import Context


class ManualRuns(commands.Cog):
    """ Chaox Cog for Manual Runs """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.runners = {}
        self.set_guild.start()
        self.config = Config.get_conf(
            self, identifier=56456541165166, force_registration=True
        )

        self.config.register_guild(
            log_channel=None)

    def cog_unload(self):
        self.set_guild.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=10, count=1)
    async def set_guild(self):
        if not self.guild:
            self.guild = self.bot.get_guild(772664928627851275)

    # Admin Setup Commands
    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin()
    async def chx_manual(self, ctx: commands.Context):
        """Various ChX Admin Settings."""

    @chx_manual.command()
    async def set_log_ch(self, ctx: commands.Context, ch: discord.TextChannel):
        await self.config.guild(ctx.guild).log_channel.set(ch.id)
        await ctx.reply(f'{ch.mention} has been set as your log channel!')

    @commands.command()
    async def login(self, ctx: commands.Context, region: str):
        """ Login to start running games. Use $login <americas/europe/asia> """

        if ctx.guild:
            await ctx.reply('$login and $logout must be used in DM\'s only')
            return

        user = str(ctx.author.id)

        if user in self.runners:
            await ctx.reply('You\'re already logged in.')
            return

        regions = ["americas", "europe", "asia"]

        if region.lower() not in regions:
            await ctx.reply('Invalid Region. [Americas / Europe / Asia]')
            return
        else:
            self.runners[user] = {
                "region": region,
                "game_count": 0
            }

            embed = discord.Embed(color=0xff0000)
            embed.title = f'You are now logged in! Region: {region}'
            embed.add_field(
                name='1.',
                value='Make a game and send it to me. See below for examples.',
                inline=False
            )
            embed.add_field(
                name='a.',
                value='For Private Games: ***priv chaos-1///1***',
                inline=False
            )
            embed.add_field(
                name='b.',
                value='For Public Games: ***pub chaos-1***',
                inline=False
            )
            embed.add_field(
                name='2.',
                value='Make sure to send each new game to trigger the next game alert.',
                inline=False
            )
            embed.add_field(
                name='3.',
                value='When you\'re done make sure to $logout.',
                inline=False
            )
            await ctx.reply(embed=embed)

    @commands.command()
    async def logout(self, ctx: commands.Context):
        """ Updates your run count with your last run. """
        if ctx.guild:
            await ctx.reply('$login and $logout must be used in DM\'s only')
            return
        user = str(ctx.author.id)
        if user in self.runners:
            channel = self.guild.get_channel(await self.config.guild(self.guild).log_channel())
            await channel.send(f'|{user}|Game Over||Americas|Baal|')
            await channel.send(f'|{user}|Logout||Americas|Baal|')
            removed = self.runners.pop(user)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            if "$" in message.content:
                return

            if not message.author.bot:
                print(f'{message.author.name}: {message.content}')

            user = str(message.author.id)
            if user not in self.runners:
                return

            manual_run_data = re.search(
                r"(?i)([a-zA-Z-= 0-9]{1,15})\/*([a-zA-Z0-9]{0,15})", message.content)

            if not manual_run_data:
                await message.reply('Invalid Game and Password format!')
                return

            game_name = manual_run_data.group(1)
            password = manual_run_data.group(2)

            regex_chaos = "(?i)(chaos|cbaal|cs)"
            regex_baal = "(?i)(baal)"

            game_type_check = re.search(regex_chaos, game_name)
            if game_type_check:
                game_type = 'Chaos'
            else:
                game_type_check = re.search(regex_baal, game_name)
                if game_type_check:
                    game_type = 'Baal'
                else:
                    await message.reply('Invalid game name. Your game name must include Chaos or Baal')
                    return

            await message.reply('Received. Send me your new game (and password) when game is over. Or $logout')
            if not password:
                password = ''

            region = self.runners[user]["region"]
            game_type = 'Chaos' if 'chaos' in game_name.lower() else 'Baal'

            channel = self.guild.get_channel(await self.config.guild(self.guild).log_channel())

            if self.runners[user]["game_count"] > 0:
                await channel.send(f'|{user}|Game Over||{region}|{game_type}|')

            self.runners[user]["game_count"] += 1

            await channel.send(f'|{user}|{game_name}|{password}|{region}|{game_type}|')
            return
