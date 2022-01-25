from redbot.core import Config, commands
from discord.ext import tasks
import random


class MiscCog(commands.Cog):
    """ Misc Commands for Clan ChX """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot
        self.twenty_four_hour_loop.start()
        self.guild = None

        self.config = Config.get_conf(
            self, identifier=56456541165166, force_registration=True
        )

        # self.config.register_guild(
        #     log_channel=None)

    def cog_unload(self):
        self.twenty_four_hour_loop.cancel()
        return super().cog_unload()

    @tasks.loop(hours=24)
    async def twenty_four_hour_loop(self):
        if not self.guild:
            self.guild = self.bot.get_guild(772664928627851275)

        await self.message_jamie()

    @twenty_four_hour_loop.before_loop
    async def before_24_hour_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def roll(self, ctx: commands.Context):
        """ Roll between min and max to compete for items. """
        num = random.randrange(0, 101)
        await ctx.reply(f'{ctx.author.mention} rolled {num}')

    async def message_jamie(self):
        ch = self.guild.get_channel(826471868663988224)
        usr = self.guild.get_member(456838972157460535)
        await ch.send(f'{usr.mention}, Don\'t forget to workout noob you need to get in shape.')
