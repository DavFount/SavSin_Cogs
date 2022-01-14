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

    @tasks.loop(seconds=10, count=1)
    async def game_announce(self):
        if not self.guild:
            self.guild = self.bot.get_guild(772664928627851275)

    @game_announce.before_loop
    async def before_game_annoucne(self):
        await self.bot.wait_until_ready()

    # Admin Setup Commands
    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin()
    async def chx_admin(self, ctx: commands.Context):
        """Various ChX Admin Settings."""

    @chx_admin.command(name="set_chaos_runner_role")
    async def chx_admin_set_chaos_role(self, ctx: commands.Context, role: discord.Role):
        """Set the chaos leecher role."""
        if role.id != await self.config.guild(ctx.guild).chaos_runner_role():
            await self.config.guild(ctx.guild).chaos_runner_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

    @chx_admin.command(name="set_baal_runner_role")
    async def chx_admin_set_baal_role(self, ctx: commands.Context, role: discord.Role):
        """Set the baal leecher role."""
        if role.id != await self.config.guild(ctx.guild).baal_runner_role():
            await self.config.guild(ctx.guild).baal_runner_role.set(role.id)
            await ctx.send(f'{role.mention} has been set!')
        else:
            await ctx.send(
                f'{role.mention} is already the current role.'
            )

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
