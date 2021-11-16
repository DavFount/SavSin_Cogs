from redbot.core import Config, commands
import random


class MiscCog(commands.Cog):
    """ Misc Commands for Clan ChX """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=56456541165166, force_registration=True
        )

        # self.config.register_guild(
        #     log_channel=None)

    @commands.command()
    async def roll(self, ctx: commands.Context):
        """ Roll between min and max to compete for items. """
        num = random.randrange(0, 101)
        ctx.reply(f'You rolled {num}')
