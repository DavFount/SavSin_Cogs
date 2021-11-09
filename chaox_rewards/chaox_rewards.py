import discord
import re
from discord import user
from redbot.core import Config, checks, commands
from discord.ext import tasks
from datetime import datetime as dt
import mysql.connector

from redbot.core.commands.context import Context


class ChaoxCog(commands.Cog):
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
            host=None, port=3306, db=None, user=None, password=None)

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
