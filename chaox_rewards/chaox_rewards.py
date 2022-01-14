import discord
import re
from discord import user
from redbot.core import Config, checks, commands
from discord.ext import tasks
from datetime import datetime as dt
import mysql.connector

from redbot.core.commands.context import Context


class ChaoxRewards(commands.Cog):
    """ Chaox Cog for Rewards System """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot
        self.game_announce.start()
        self.guild = None
        self.config = Config.get_conf(
            self, identifier=56456541165165, force_registration=True
        )

        self.config.register_guild(
            host=None, port=3306, db=None, user=None, password=None, chaos_runner_role=None, baal_runner_role=None)

    def cog_unload(self):
        self.game_announce.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=60, count=1)
    async def game_announce(self):
        if not self.guild:
            self.guild = self.bot.get_guild(772664928627851275)

        await self.update_runners()

    @game_announce.before_loop
    async def before_game_annoucne(self):
        await self.bot.wait_until_ready()

    # Admin Setup Commands
    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin()
    async def chx_rewards(self, ctx: commands.Context):
        """Various ChX Admin Settings."""

    @chx_rewards.command(name="set_chaos_runner_role")
    async def chx_rewards_set_chaos_role(self, ctx: commands.Context, role: discord.Role):
        """Set the chaos leecher role."""
        if role.id != await self.config.guild(ctx.guild).chaos_runner_role():
            await self.config.guild(ctx.guild).chaos_runner_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

    @chx_rewards.command(name="set_baal_runner_role")
    async def chx_rewards_set_baal_role(self, ctx: commands.Context, role: discord.Role):
        """Set the baal leecher role."""
        if role.id != await self.config.guild(ctx.guild).baal_runner_role():
            await self.config.guild(ctx.guild).baal_runner_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

    @chx_rewards.command(name="set_host")
    async def chx_rewards_set_host(self, ctx: commands.Context, host: str):
        """Set Hostname"""
        if self.config.guild(ctx.guild).host != host:
            await self.config.guild(ctx.guild).host.set(host)
            await ctx.send('Host Updated.')
            await ctx.message.delete()
        else:
            await ctx.send('This host is already set!')
            await ctx.message.delete()

    @chx_rewards.command(name="set_port")
    async def chx_rewards_set_port(self, ctx: commands.Context, port: int):
        """Set Database Port"""
        if self.config.guild(ctx.guild).port != port:
            await self.config.guild(ctx.guild).port(port)
            await ctx.send('Port Updated.')
            await ctx.message.delete()
        else:
            await ctx.send(f'Port is already set to {port}.')
            await ctx.message.delete()

    @chx_rewards.command(name="set_db")
    async def chx_rewards_set_db(self, ctx: commands.Context, db: str):
        """Set Database Name"""
        if self.config.guild(ctx.guild).db != db:
            await self.config.guild(ctx.guild).db.set(db)
            await ctx.send('Database Selected.')
            await ctx.message.delete()
        else:
            await ctx.send('This database is already selected.')
            await ctx.message.delete()

    @chx_rewards.command(name="set_user")
    async def chx_rewards_set_user(self, ctx: commands.Context, user: str):
        """Set Database User"""
        if self.config.guild(ctx.guild).user != user:
            await self.config.guild(ctx.guild).user.set(user)
            await ctx.send('Updated Database User.')
            await ctx.message.delete()
        else:
            await ctx.send('This user is already set.')
            await ctx.message.delete()

    @chx_rewards.command(name="set_password")
    async def chx_rewards_set_password(self, ctx: commands.Context, password: str):
        """Set Database Password"""
        await self.config.guild(ctx.guild).password.set(password)
        await ctx.send('Password Updated')
        await ctx.message.delete()

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

    async def update_runners(self):
        # db = await self.connect_sql()
        user = self.guild.get_member(862144674251669525)
        role = self.guild.get_role(877044470888157185)

        print(self.user_has_role(user, role))

    def user_has_role(self, user, role):
        for user_role in user.roles:
            if user_role is role:
                return True

        return False
