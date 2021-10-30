import discord
import time
import re
from redbot.core import Config, checks, commands
from discord.ext import tasks
from datetime import datetime as dt
import mysql.connector

from redbot.core.commands.context import Context


class ChaoxCog(commands.Cog):
    """ Chaox Cog for Game Spamming, career stats and top runners """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.game_announce.start()
        self.config = Config.get_conf(
            self, identifier=56456541165165, force_registration=True
        )

        self.config.register_guild(
            host=None, port=3306, db=None, user=None, password=None, min_game_time=0, max_game_time=999,
            annouce_channel=None, log_channels=[], game_msg=None, leader_msg=None, chaos_role=None, baal_role=None)

    def cog_unload(self):
        self.game_announce.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=10)
    async def game_announce(self):
        self.guild = self.bot.get_guild(901951195667644477)
        curtime = int(time.time())
        for(k, v) in self.games.items():
            if curtime - v["timestamp"] > 600:
                remove = self.games.pop(k)

        await self.update_channel(self.guild)

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
        if not await self.is_db_configured():
            return
        db = await self.connect_sql()

        if count > 5:
            count = 5
        cursor_chaos = db.cursor()
        # Chaos
        cursor_chaos.execute(
            f"SELECT * FROM `chaos_tracker` ORDER BY total_runs DESC LIMIT {count}")
        result_chaos = cursor_chaos.fetchall()

        # Baal
        cursor_baal = db.cursor()
        cursor_baal.execute(
            f"SELECT * FROM `baal_tracker` ORDER BY total_runs DESC LIMIT {count}")
        result_baal = cursor_baal.fetchall()

        embed = discord.Embed(color=0xff0000)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = f'Top {count} Runners'
        count = 1

        top = {"chaos": [], "baal": []}
        for row in result_chaos:
            user = row[1].split('#')[0]
            top["chaos"].append(
                f'{count}. {user} - Total Runs: {row[2]}'
            )
            count += 1

        count = 1
        for row in result_baal:
            user = row[1].split('#')[0]
            top["baal"].append(
                f'{count}. {user} - Total Runs: {row[2]}'
            )
            count += 1

        if(len(top["chaos"])):
            embed.add_field(
                name=f'Chaos',
                value='\n'.join(top["chaos"]),
                inline=True
            )

        if(len(top["baal"])):
            embed.add_field(
                name=f'Baal',
                value='\n'.join(top["baal"]),
                inline=True
            )
        db.close()
        await ctx.send(embed=embed)

    @chx.command(name="career")
    async def chx_career(self, ctx: commands.Context, user: discord.Member = None):
        """ Display Embed with Career Stats """
        if not await self.is_db_configured():
            return

        if not user:
            user = ctx.author

        username = user.name + '#' + user.discriminator
        db = await self.connect_sql()
        career = {"chaos": [], "baal": []}

        cursor_chaos = db.cursor()
        cursor_chaos.execute(
            f"SELECT * FROM `chaos_tracker` WHERE `username`='{username}' LIMIT 1")
        result_chaos = cursor_chaos.fetchall()
        for row in result_chaos:
            career["chaos"] = row

        cursor_baal = db.cursor()
        cursor_baal.execute(
            f"SELECT * FROM `baal_tracker` WHERE `username`='{username}' LIMIT 1")
        result_baal = cursor_baal.fetchall()
        for row in result_baal:
            career["baal"] = row

        embed = discord.Embed(color=0xff0000)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = f'{user.name}\'s Career'

        if not len(result_chaos):
            embed.add_field(
                name='No Runs Recorded!',
                value='Check out our links section to become a runner!'
            )

        if len(career["chaos"]):
            avg_time = int(career["chaos"][3] / career["chaos"][2])
            embed.add_field(
                name='Chaos',
                value=f'Total Runs: {career["chaos"][2]} [Average Time: {avg_time}s]'
            )

        if len(career["baal"]):
            avg_time = int(career["baal"][3] / career["baal"][2])
            embed.add_field(
                name='Baal',
                value=f'Total Runs: {career["baal"][2]} [Average Time: {avg_time}s]'
            )

        db.close()
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
            if await self.is_db_configured():
                await self.setup_sql()
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
            if await self.is_db_configured():
                await self.setup_sql()
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
            if await self.is_db_configured():
                await self.setup_sql()
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
            if await self.is_db_configured():
                await self.setup_sql()
        else:
            await ctx.send('This user is already set.')
            await ctx.message.delete()

    @chx_admin.command(name="set_password")
    async def chx_admin_set_password(self, ctx: commands.Context, password: str):
        """Set Database Password"""
        await self.config.guild(ctx.guild).password.set(password)
        await ctx.send('Password Updated')
        await ctx.message.delete()
        if await self.is_db_configured():
            await self.setup_sql()

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

    @chx_admin.command(name="set_chaos_role")
    async def chx_admin_set_chaos_role(self, ctx: commands.Context, role: discord.Role):
        if role.id != await self.config.guild(ctx.guild).chaos_role():
            await self.config.guild(ctx.guild).chaos_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

    @chx_admin.command(name="set_baal_role")
    async def chx_admin_set_baal_role(self, ctx: commands.Context, role: discord.Role):
        if role.id != await self.config.guild(ctx.guild).baal_role():
            await self.config.guild(ctx.guild).baal_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
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

        run_data = re.search(
            r"(?i)\|(.*\#.*)\|([a-zA-Z-= 0-9]{1,15})\|([a-zA-Z0-9]{0,15})\|(Americas|Europe|Asia)\|(Baal|Chaos)\|", message.content)

        if not run_data:
            await message.delete()
            return

        runner = run_data.group(1)
        game_name = run_data.group(2)
        password = run_data.group(3)
        region = run_data.group(4)
        game_type = run_data.group(5).lower()

        # await message.delete()

        last_game = None
        cur_time = int(time.time())

        duration = 0
        if runner in self.games:
            last_game = self.games[runner]["timestamp"]
            duration = cur_time - last_game

        # Game Counts add to DB
        if last_game and (duration > await self.config.guild(message.guild).min_game_time()
                          and duration < await self.config.guild(message.guild).max_game_time()):
            db = await self.connect_sql()
            if game_type == 'chaos':
                cursor = db.cursor()
                cursor.execute(
                    f"SELECT * FROM `chaos_tracker` WHERE `username`='{runner}' LIMIT 1;")
                result = cursor.fetchall()
                if len(result):
                    update_runs = result[0][2] + 1
                    update_time = result[0][3] + (duration)
                    cursor.execute(
                        f"UPDATE `chaos_tracker` SET total_runs={update_runs}, total_time={update_time} WHERE `username`='{runner}' LIMIT 1;")
                    db.commit()
                else:
                    run_time = duration
                    sql = "INSERT INTO chaos_tracker (`username`,`total_runs`,`total_time`) VALUES (%s, %s, %s);"
                    val = (runner, 1, run_time)
                    cursor.execute(sql, val)
                    db.commit()
                cursor.close()
            elif game_type == 'baal':
                cursor = db.cursor()
                cursor.execute(
                    f"SELECT * FROM `baal_tracker` WHERE `username`='{runner}' LIMIT 1;")
                result = cursor.fetchall()
                if len(result):
                    update_runs = result[0][2] + 1
                    update_time = result[0][3] + (duration)
                    cursor.execute(
                        f"UPDATE `baal_tracker` SET total_runs={update_runs}, total_time={update_time} WHERE `username`='{runner}' LIMIT 1;")
                    db.commit()
                else:
                    run_time = duration
                    sql = "INSERT INTO baal_tracker (`username`,`total_runs`,`total_time`) VALUES (%s, %s, %s);"
                    val = (runner, 1, run_time)
                    cursor.execute(sql, val)
                    db.commit()
                cursor.close()
            db.close()

        if game_name.lower() == 'logout':
            if runner in self.games:
                removed = self.games.pop(runner)
                await self.update_channel(message.guild)
            return

        if runner in self.games:
            removed = self.games.pop(runner)

        game = {
            runner: {
                "game_name": game_name,
                "timestamp": cur_time,
                "password": password,
                "region": region,
                "game_type": game_type
            }
        }

        self.games.update(game)
        channel = message.guild.get_channel(await self.config.guild(message.guild).annouce_channel())
        if password:
            text_password = f' (Password: {password})'
        else:
            text_password = ''

        if game_type == 'chaos' and await self.config.guild(message.guild).chaos_role():
            role = message.guild.get_role(await self.config.guild(message.guild).chaos_role())
        elif game_type == 'baal' and await self.config.guild(message.guild).baal_role():
            role = message.guild.get_role(await self.config.guild(message.guild).baal_role())

        if await self.config.guild(message.guild).chaos_role() or await self.config.guild(message.guild).baal_role():
            await channel.send(f'{role.mention} New Game: {game_name} [Hosted by {runner}] (Password: {text_password})', delete_after=15)
        else:
            await channel.send('You must first configure your role settings !chx_admin set_chaos_role and set_baal_role!')

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
        # cur_time = int(time.time())
        for(k, v) in self.games.items():
            password = ''
            if v["password"]:
                password = f' (Password: {v["password"]})'

            if v["region"] == 'Americas':
                cur_games["americas"].append(
                    f'{v["game_name"]} [{k}]{password} <t:{v["timestamp"]}:R>')
            elif v["region"] == 'Europe':
                cur_games["europe"].append(
                    f'{v["game_name"]} [{k}]{password} <t:{v["timestamp"]}:R>')
            elif v["region"] == 'Asia':
                cur_games["asia"].append(
                    f'{v["game_name"]} [{k}]{password} <t:{v["timestamp"]}:R>')

        embed = discord.Embed(
            color=0xff0000, timestamp=dt.now()
        )

        embed.title = 'Current Games'
        embed.set_footer(text='')

        if(not len(cur_games["americas"]) and not len(cur_games["europe"]) and not len(cur_games["asia"])):
            embed.add_field(
                name='Status',
                value='Currently there are no games going!',
                inline=False
            )

        if (len(cur_games["americas"])):
            embed.add_field(
                name='Americas:',
                value='\n\n'.join(cur_games["americas"]),
                inline=False
            )

        if (len(cur_games["europe"])):
            embed.add_field(
                name='Europe:',
                value='\n\n'.join(cur_games["europe"]),
                inline=False
            )

        if (len(cur_games["asia"])):
            embed.add_field(
                name='Asia:',
                value='\n\n'.join(cur_games["asia"]),
                inline=False
            )

        return embed

    async def is_db_configured(self):
        host = await self.config.guild(self.guild).host()
        user = await self.config.guild(self.guild).user()
        password = await self.config.guild(self.guild).password()
        port = await self.config.guild(self.guild).port()
        db = await self.config.guild(self.guild).db()

        if host and user and password and port and db:
            return True
        else:
            return False

    async def connect_sql(self):
        host = await self.config.guild(self.guild).host()
        user = await self.config.guild(self.guild).user()
        password = await self.config.guild(self.guild).password()
        database = await self.config.guild(self.guild).db()

        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )