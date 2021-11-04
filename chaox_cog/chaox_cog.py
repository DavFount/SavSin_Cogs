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

    __version__ = '1.1.3'

    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.prev_games = {}
        self.manual_games = {}
        self.game_announce.start()
        self.guild = None
        self.config = Config.get_conf(
            self, identifier=56456541165165, force_registration=True
        )

        self.config.register_guild(
            host=None, port=3306, db=None, user=None, password=None, min_game_time=0, max_game_time=999,
            announce_channel=None, log_channel=None, game_msg=None, inst_msg=None, top_msg=None, chaos_role=None,
            baal_role=None, message_wait_time=15)

    def cog_unload(self):
        self.game_announce.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=10)
    async def game_announce(self):
        if not self.guild:
            self.guild = self.bot.get_guild(772664928627851275)
        curtime = int(time.time())
        for(k, v) in list(self.games.items()):
            duration = curtime - v["timestamp"]
            if duration > 600:
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

    @commands.command()
    async def login(self, ctx: commands.Context, region: str, game_type: str):
        """ Login to start running games. Use $login <americas/europe/asia> <chaos/baal> """
        username = f'{ctx.author.name}#{ctx.author.discriminator}'

        if username in self.manual_games:
            await ctx.reply('You\'re already logged in.')
            return

        regions = ["americas", "europe", "asia"]
        game_types = ["chaos", "baal"]

        if region not in regions:
            await ctx.reply('Invalid Region. [Americas / Europe / Asia]')
            return
        elif game_type not in game_types:
            await ctx.reply('Invalid Type. [Chaos / Baal]')
            return
        else:
            self.manual_games[username] = {
                "region": region,
                "game_type": game_type
            }
            await ctx.reply(f'You are now logged in running {game_type} games in the {region} region.')
            await ctx.reply('What is the game name and password? Format: ***chx chaos-1///1*** will create the game chx chaos-1 with a password of 1')

    @commands.command()
    async def logout(self, ctx: commands.Context):
        username = f'{ctx.author.name}#{ctx.author.discriminator}'
        cur_time = time.time()
        duration = cur_time - self.games[username]["timestamp"]
        if username in self.manual_games:
            await self.persist_data(self.games[username]["game_type"], username, duration)
            await self.send_thankyou_message(username, self.games[username]["game_name"])
            removed = self.games.pop(username)
            removed = self.prev_games.pop(username)
            await self.update_channel(self.guild)

    @commands.command()
    async def whoami(self, ctx: commands.Context):
        await ctx.send(f'Your userid is: {ctx.author.id}')

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
        cursor_chaos.close()
        cursor_baal.close()
        db.close()
        await ctx.send(embed=embed)

    # Admin Setup Commands
    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin()
    async def chx_admin(self, ctx: commands.Context):
        """Various ChX Admin Settings."""

    @chx_admin.command(name="reset")
    async def chx_admin_reset(self, ctx: commands.Context):
        await self.config.guild(ctx.guild).game_msg.set(None)
        await self.config.guild(ctx.guild).inst_msg.set(None)
        await self.config.guild(ctx.guild).top_msg.set(None)

    @chx_admin.command(name="stop")
    async def chx_admin_stop(self, ctx: commands.Context, user: discord.Member):
        removed = self.games.pop(f'{user.name}#{user.discriminator}')
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
        if not channel.id == await self.config.guild(ctx.guild).log_channel():
            await self.config.guild(ctx.guild).log_channel.set(channel.id)
            await ctx.send(
                f'{channel.mention} is now the logging channel!'
            )
        else:
            await ctx.send(
                f'{channel.mention} is already in the list of channels.'
            )

    @chx_admin.command(name="game_announce_ch")
    async def chx_admin_set_game_announce_ch(self, ctx: commands.Context, channel: discord.TextChannel):
        if not channel.id == await self.config.guild(ctx.guild).announce_channel():
            await self.config.guild(ctx.guild).announce_channel.set(channel.id)
            await ctx.send(
                f'{channel.mention} is now the announcement channel!'
            )
        else:
            await ctx.send(
                f'{channel.mention} is already in the list of channels.'
            )

    @chx_admin.command(name="set_chaos_role")
    async def chx_admin_set_chaos_role(self, ctx: commands.Context, role: discord.Role):
        """Set the chaos leecher role."""
        if role.id != await self.config.guild(ctx.guild).chaos_role():
            await self.config.guild(ctx.guild).chaos_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

    @chx_admin.command(name="set_baal_role")
    async def chx_admin_set_baal_role(self, ctx: commands.Context, role: discord.Role):
        """Set the baal leecher role."""
        if role.id != await self.config.guild(ctx.guild).baal_role():
            await self.config.guild(ctx.guild).baal_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

    @chx_admin.command(name="set_message_dur")
    async def chx_message_delay(self, ctx: commands.Context, delay: int):
        """Sets the duration of the message displayed for new games"""
        await self.config.guild(ctx.guild).message_wait_time.set(delay)
        await ctx.send(f'The duration of the new game message is now {delay} seconds')

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
        embed.add_field(name='Game Message Duration*',
                        value=data["message_wait_time"])

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            if "$" in message.content:
                return
            username = f'{message.author.name}#{message.author.discriminator}'
            print(username)
            if username not in self.manual_games:
                print('User not logged in!')
                return
            game_string = message.content.split('/', 1)
            print(f'Game String Length: {len(game_string)}')

            if len(game_string) > 1:
                print('Game and Password set')
                game_name = game_string[0].replace('/', '')
                password = game_string[1].replace('/', '')
            else:
                print('Game Only')
                game_name = message.content
                password = ''
            print('Set Region')
            region = self.manual_games[username]["region"]
            print('Print game_type')
            game_type = self.manual_games[username]["game_type"]
            print('Channel selected')
            channel = self.guild.get_channel(await self.config.guild(self.guild).log_channel())

            if username in self.games:
                print('Send Game Over to clear and count game.')
                await channel.send(f'|{username}|Game Over||{region}|{game_type}|')

            print('Sending Game to Game Log')
            await channel.send(f'|{username}|{game_name}|{password}|{region}|{game_type}|')
            return

        if message.channel.id == await self.config.guild(message.guild).announce_channel() and not message.author.bot:
            await message.delete()
            return

        if not message.channel.id == await self.config.guild(message.guild).log_channel():
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
        cur_time = int(time.time())

        if runner in self.games:
            duration = cur_time - self.games[runner]["timestamp"]
            if game_name.lower() == 'logout':
                await self.persist_data(self.games[runner]["game_type"], runner, duration)
                await self.send_thankyou_message(runner, self.games[runner]["game_name"])
                removed = self.games.pop(runner)
                removed = self.prev_games.pop(runner)
                await self.update_channel(message.guild)
                return
            elif game_name.lower() == 'game over':
                self.prev_games[runner].append(duration)
                if (duration > await self.config.guild(message.guild).min_game_time()
                        and duration < await self.config.guild(message.guild).max_game_time()):
                    await self.persist_data(self.games[runner]["game_type"], runner, duration)
                    removed = self.games.pop(runner)
                    await self.update_channel(message.guild)
                    return

        if game_name.lower() == 'logout':
            return

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
        if runner not in self.prev_games:
            self.prev_games[runner] = []

        channel = message.guild.get_channel(await self.config.guild(message.guild).announce_channel())
        msg_duration = await self.config.guild(self.guild).message_wait_time()
        if password:
            text_password = {password}
        else:
            text_password = 'None'

        if game_type.lower() == 'chaos' and await self.config.guild(message.guild).chaos_role():
            role = message.guild.get_role(await self.config.guild(message.guild).chaos_role())
        elif game_type.lower() == 'baal' and await self.config.guild(message.guild).baal_role():
            role = message.guild.get_role(await self.config.guild(message.guild).baal_role())

        if await self.config.guild(message.guild).chaos_role() or await self.config.guild(message.guild).baal_role():
            await channel.send(f'{role.mention} New Game: {game_name} [Hosted by {runner}] (Password: {text_password})', delete_after=msg_duration)
        else:
            await channel.send('You must first configure your role settings !chx_admin set_chaos_role and set_baal_role!')

        await self.update_channel(message.guild)

    async def update_channel(self, guild: discord.Guild):
        channel = guild.get_channel(await self.config.guild(guild).announce_channel())
        if(not await self.config.guild(guild).inst_msg()):
            message = await channel.send(embed=self.format_instructions())
            await self.config.guild(guild).inst_msg.set(message.id)

        if(not await self.config.guild(guild).top_msg()):
            message = await channel.send(embed=await self.format_top())
            await self.config.guild(guild).top_msg.set(message.id)
        else:
            message = await channel.fetch_message(await self.config.guild(guild).top_msg())
            await message.edit(embed=await self.format_top())

        if(not await self.config.guild(guild).game_msg()):
            message = await channel.send(embed=self.format_games())
            await self.config.guild(guild).game_msg.set(message.id)
        else:
            message = await channel.fetch_message(await self.config.guild(guild).game_msg())
            await message.edit(embed=self.format_games())

    def format_instructions(self):
        embed = discord.Embed(color=0xff0000)
        embed.title = 'Instructions'
        embed.add_field(
            name="1.",
            value="Some future instructions"
        )

        return embed

    async def format_top(self):
        cur_time = time.time()
        db = await self.connect_sql()
        top_count = 5
        cursor_chaos = db.cursor()
        # Chaos
        cursor_chaos.execute(
            f"SELECT * FROM `chaos_tracker` ORDER BY total_runs DESC LIMIT {top_count}")
        result_chaos = cursor_chaos.fetchall()

        # Baal
        cursor_baal = db.cursor()
        cursor_baal.execute(
            f"SELECT * FROM `baal_tracker` ORDER BY total_runs DESC LIMIT {top_count}")
        result_baal = cursor_baal.fetchall()

        embed = discord.Embed(color=0xffffff)
        embed.title = f'Top {top_count} Runners'
        # embed.description = f'Updated <t:{cur_time}:f>'
        count = 1

        top = {"chaos": [], "baal": []}
        for row in result_chaos:
            user = row[1].split('#')[0]
            avg_time = int(row[3] / row[2])
            top["chaos"].append(
                f'{count}. {user} - {row[2]} runs - {avg_time} sec avg'
            )
            count += 1

        count = 1
        for row in result_baal:
            user = row[1].split('#')[0]
            avg_time = int(row[3] / row[2])
            top["baal"].append(
                f'{count}. {user} - {row[2]} runs - {avg_time} sec avg'
            )
            count += 1

        embed.add_field(
            name=f'Chaos',
            value='\n'.join(top["chaos"]) if len(top["chaos"]) else 'No Data',
            inline=True
        )

        embed.add_field(
            name=f'Baal',
            value='\n'.join(top["baal"]) if len(top["baal"]) else 'No Data',
            inline=True
        )
        cursor_baal.close()
        cursor_chaos.close()
        db.close()
        return embed

    def format_games(self):
        cur_games = {"americas": [], "europe": [], "asia": []}
        cur_time = int(time.time())
        for(k, v) in self.games.items():
            if v["password"]:
                password = f'///{v["password"]}'
            else:
                password = ' (No PW)'

            user = self.get_user(k)
            if v["region"].lower() == 'americas':
                cur_games["americas"].append(
                    f'{v["game_name"]}{password} [{user.mention}] <t:{v["timestamp"]}:R>')
            elif v["region"].lower() == 'europe':
                cur_games["europe"].append(
                    f'{v["game_name"]}{password} [{user.mention}] <t:{v["timestamp"]}:R>')
            elif v["region"].lower() == 'asia':
                cur_games["asia"].append(
                    f'{v["game_name"]}{password} [{user.mention}] <t:{v["timestamp"]}:R>')

        embed = discord.Embed(
            color=0x0000ff
        )

        embed.title = 'Current Games'
        # embed.set_footer(text=f'<t:{cur_time}:f>')

        if(not len(cur_games["americas"]) and not len(cur_games["europe"]) and not len(cur_games["asia"])):
            embed.add_field(
                name=f'<t:{cur_time}:f>',
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

    async def send_thankyou_message(self, runner, game_name):
        db = await self.connect_sql()
        cursor = db.cursor()
        cursor.execute(
            f'SELECT SUM(chaos_tracker.total_runs + baal_tracker.total_runs) from chaos_tracker INNER JOIN baal_tracker ON chaos_tracker.username=baal_tracker.username WHERE username=\'{runner}\'')
        result = cursor.fetchall()
        cursor.close()
        db.close()
        channel = self.guild.get_channel(await self.config.guild(self.guild).announce_channel())
        user = self.get_user(runner)
        self.prev_games[runner].sort()

        embed = discord.Embed(color=0xffffff)
        embed.title = f'{user.mention} Stats'
        embed.description(
            f'Thank you for joining {game_name}. These games have come to an end.\n{user.mention} has supported Clan ChX with a total of {result[0]} runs'
        )
        embed.add_field(
            name="Runs",
            value=len(self.prev_games[runner]),
            inline=False
        )
        embed.add_field(
            name="Fastest Time",
            value=self.prev_games[runner][0],
            inline=False
        )
        embed.add_field(
            name="Loggest Time",
            value=self.prev_games[runner][-1],
            inline=False
        )
        await channel.send(embed=embed, delete_after=25)
        removed = self.prev_games[runner].pop()

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

    def get_user(self, name: str):
        return self.guild.get_member_named(name)

    async def persist_data(self, game_type, runner, duration):
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
