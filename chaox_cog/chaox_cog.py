import discord
import json
import time
from redbot.core import Config, checks, commands
from discord.ext import tasks
from datetime import datetime as dt

from redbot.core.commands.context import Context


class ChaoxCog(commands.Cog):
    """ Chaox Cog for Game Spamming, career stats and top runners """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot
        self.game_announce.start()
        self.games = {}
        self.config = Config.get_conf(
            self, identifier=56456541165165, force_registration=True
        )

        self.config.register_guild(
            host=None, port=3307, db=None, user=None, password=None, min_game_time=0, max_game_time=999,
            annouce_channel=None, log_channels=[], game_msg=None)

    def cog_unload(self):
        self.game_announce.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=10)
    async def game_announce(self):
        await self.update_channel(self.bot.guilds[1])

    @game_announce.before_loop
    async def before_game_annoucne(self):
        await self.bot.wait_until_ready()

    async def red_delete_data_for_user(self, *, requester, user_id):
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f'{context}\n\nVersion: {self.__version__}'

    @commands.group(autohelp=True)
    @commands.guild_only()
    async def chx(self, ctx: commands.Context):
        """Various ChX Commands."""

    @chx.command(name="top")
    async def chx_top(self, ctx: commands.Context, count: int = 5):
        """ Displays embed with top runners """
        if count > 5:
            count = 5
        data = json.loads(sample_data)
        embed = discord.Embed(color=0xff0000)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = f'Top {count} Runners'
        count = 1
        for (k, v) in data.items():
            embed.add_field(
                name=f'{count}. {k}',
                value=f'Total Runs: {v["Run Count"]} \n Avg Time: {v["Avg Time"]} seconds',
                inline=False
            )
            count += 1

        await ctx.send(embed=embed)

    @chx.command(name="career")
    async def chx_career(self, ctx: commands.Context):
        """ Display Embed with Career Stats """
        data = json.loads(sample_data)
        embed = discord.Embed(color=0xff0000)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = 'Your Career'
        embed.description = f'You have run {data["Steve"]["Run Count"]} games with an average time of {data["Steve"]["Avg Time"]} seconds!'
        await ctx.send(embed=embed)

    # Admin Setup Commands
    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin()
    async def chx_admin(self, ctx: commands.Context):
        """Various ChX Admin Settings."""

    @chx_admin.command(name="stop")
    async def chx_admin_stop(self, ctx: commands.Context, user: discord.Member):
        self.games.pop(f'{user.name}#{user.discriminator}')
        await self.update_channel(ctx.guild)

    @chx_admin.command(name="set_host")
    async def chx_admin_set_host(self, ctx: commands.Context, host: str):
        """Set Hostname"""
        if self.config.guild(ctx.guild).host != host:
            await self.config.guild(ctx.guild).host.set(host)
            await ctx.send('Host Updated.')
            await ctx.message.delete()
        else:
            await ctx.send('This host is already set!')
            await ctx.message.delete()

    @chx_admin.command(name="set_port")
    async def chx_admin_set_port(self, ctx: commands.Context, port: int):
        """Set Database Port"""
        if self.config.guild(ctx.guild).port != port:
            await self.config.guild(ctx.guild).port(port)
            await ctx.send('Port Updated.')
            await ctx.message.delete()
        else:
            await ctx.send(f'Port is already set to {port}.')
            await ctx.message.delete()

    @chx_admin.command(name="set_db")
    async def chx_admin_set_db(self, ctx: commands.Context, db: str):
        """Set Database Name"""
        if self.config.guild(ctx.guild).db != db:
            await self.config.guild(ctx.guild).db.set(db)
            await ctx.send('Database Selected.')
            await ctx.message.delete()
        else:
            await ctx.send('This database is already selected.')
            await ctx.message.delete()

    @chx_admin.command(name="set_user")
    async def chx_admin_set_user(self, ctx: commands.Context, user: str):
        """Set Database User"""
        if self.config.guild(ctx.guild).user != user:
            await self.config.guild(ctx.guild).user.set(user)
            await ctx.send('Updated Database User.')
            await ctx.message.delete()
        else:
            await ctx.send('This user is already set.')
            await ctx.message.delete()

    @chx_admin.command(name="set_password")
    async def chx_admin_set_password(self, ctx: commands.Context, password: str):
        """Set Database Password"""
        await self.config.guild(ctx.guild).password.set(password)
        await ctx.send('Password Updated')
        await ctx.message.delete()

    @chx_admin.command(name="set_min_game_time")
    async def chx_admin_set_min_game_time(self, ctx: commands.Context, min: int):
        """Set Minimum Game Time"""
        await self.config.guild(ctx.guild).min_game_time.set(min)
        await ctx.send(f'Minimum time set to {min} seconds.')
        await ctx.message.delete()

    @chx_admin.command(name="set_max_game_time")
    async def chx_admin_set_max_game_time(self, ctx: commands.Context, max: int):
        """Set Maximum Game Time"""
        await self.config.guild(ctx.guild).max_game_time.set(max)
        await ctx.send(f'Maximum time set to {max} seconds.')
        await ctx.message.delete()

    @chx_admin.command(name="game_log_ch")
    async def chx_admin_set_game_log_ch(self, ctx: commands.Context, channel: discord.TextChannel):
        if channel.id not in await self.config.guild(ctx.guild).log_channels():
            async with self.config.guild(ctx.guild).log_channels() as channels:
                channels.append(channel.id)
            await ctx.send(
                f'{channel.mention} has been added!'
            )
        else:
            await ctx.send(
                f'{channel.mention} is already in the list of channels.'
            )

    @chx_admin.command(name="game_announce_ch")
    async def chx_admin_set_game_announce_ch(self, ctx: commands.Context, channel: discord.TextChannel):
        if channel.id != await self.config.guild(ctx.guild).annouce_channel():
            await self.config.guild(ctx.guild).annouce_channel.set(channel.id)
            await ctx.send(
                f'{channel.mention} has been added!'
            )
        else:
            await ctx.send(
                f'{channel.mention} is already in the list of channels.'
            )

    @chx_admin.command(name="settings")
    async def chx_admin_settings(self, ctx: commands.Context):
        """See current settings."""
        data = await self.config.guild(ctx.guild).all()

        if data["password"]:
            password = 'Set'
        else:
            password = 'Not Set'

        embed = discord.Embed(
            colour=await ctx.embed_colour(), timestamp=dt.now()
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = '**__Unique Name settings:__**'
        embed.set_footer(text='*required to function properly')

        embed.add_field(name='Hostname*:', value=data["host"])
        embed.add_field(name='Port*:', value=data["port"])
        embed.add_field(name='Database*:', value=data["db"])
        embed.add_field(name='Username*:', value=data["user"])
        embed.add_field(name='Password*:', value=password)

        embed.add_field(name='Min Game Time*:', value=data["min_game_time"])
        embed.add_field(name='Max Game Time*:', value=data["max_game_time"])

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        if message.channel.id not in await self.config.guild(message.guild).log_channels():
            return

        parsed_message = message.content.split('|')
        runner = parsed_message[0]
        game_name = parsed_message[1]
        password = parsed_message[2]
        region = parsed_message[3]

        last_game = None
        cur_time = int(time.time())

        duration = 0
        if runner in self.games:
            last_game = self.games[runner]["timestamp"]
            duration = cur_time - last_game

        # Game Counts add to DB
        # if last_game and (cur_time - last_game > 90
        #                   and cur_time - last_game < 240):
        #     # Count the run and write to DB
        #     pass

        if runner in self.games:
            removed = self.games.pop(runner)

        game = {
            runner: {
                "game_name": game_name,
                "timestamp": cur_time,
                "password": password,
                "region": region
            }
        }

        self.games.update(game)
        await self.update_channel(message.guild)

    async def update_channel(self, guild: discord.Guild):
        channel = guild.get_channel(await self.config.guild(guild).annouce_channel())
        if(not await self.config.guild(guild).game_msg()):
            message = await channel.send(embed=self.format_games())
            await self.config.guild(guild).game_msg.set(message.id)
        else:
            message = await channel.fetch_message(await self.config.guild(guild).game_msg())
            await message.edit(embed=self.format_games())

    def format_games(self):
        cur_games = {"americas": [], "europe": [], "asia": []}
        for(k, v) in self.games.items():
            password = ''
            if v["password"]:
                password = f' (Password: {v["password"]})'

            if v["region"] == 'Americas':
                cur_games["americas"].append(
                    f'{v["game_name"]} [Hosted by {k}]{password}')
            elif v["region"] == 'Europe':
                cur_games["europe"].append(
                    f'{v["game_name"]} [Hosted by {k}]{password}')
            elif v["region"] == 'Asia':
                cur_games["asia"].append(
                    f'{v["game_name"]} [Hosted by {k}]{password}')

        embed = discord.Embed(
            color=0xff0000, timestamp=dt.now()
        )
        # embed.set_author(name=guild.name, icon_url=guild.icon_url)
        embed.title = 'Current Games'
        embed.set_footer(
            text='Want to run your own games? Ask Today!')

        if(not len(cur_games["americas"]) and not len(cur_games["europe"]) and not len(cur_games["asia"])):
            embed.add_field(
                name='Status',
                value='Currently there are no games going!',
                inline=False
            )

        if (len(cur_games["americas"])):
            embed.add_field(
                name='Americas:',
                value='\n'.join(cur_games["americas"]),
                inline=False
            )

        if (len(cur_games["europe"])):
            embed.add_field(
                name='Europe:',
                value='\n'.join(cur_games["europe"]),
                inline=False
            )

        if (len(cur_games["asia"])):
            embed.add_field(
                name='Asia:',
                value='\n'.join(cur_games["asia"]),
                inline=False
            )

        return embed
