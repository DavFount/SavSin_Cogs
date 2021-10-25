import discord
import json
from redbot.core import Config, checks, commands

sample_data = """
{
    "Steve": {
        "Run Count": 25,
        "Avg Time": 90
    },
    "Jamie": {
        "Run Count": 23,
        "Avg Time": 98
    },
    "Kyle": {
        "Run Count": 20,
        "Avg Time": 110
    },
    "Andy": {
        "Run Count": 10,
        "Avg Time": 90
    },
    "Billeh": {
        "Run Count": 3,
        "Avg Time": 90
    }
}
"""

class ChaoxCog(commands.Cog):
    """ Chaox Cog for Game Spamming, career stats and top runners """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=56456541165165, force_registration=True
            )

        self.config.register_guild(moderator=None, everyone=True, ignore=[])

    async def red_delete_data_for_user(self, *, requester, user_id):
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f'{context}\n\nVersion: {self.__version__}'

    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin()
    async def chx(self, ctx: commands.Context):
        """Various ChX Commands."""
    
    @chx.command(name="top")
    async def chx_top(self, ctx, count: int):
        """ Displays embed with top runners """
        if count > 25:
            count = 25
        data = json.loads(sample_data)
        embed = discord.Embed(color=0x00ff00)
        embed.title = f'Top {count} Runners'
        count = 1
        for (k,v) in data.items():
            embed.add_field(
                name = f'{count}. {k}',
                value = f'Total Runs: {v["Run Count"]} \n Avg Time: {v["Avg Time"]} seconds',
                inline=False
            )
            count += 1

        await ctx.send(embed=embed)

    @chx.command(name="career")
    async def chx_career(self, ctx):
        """ Display Embed with Career Stats """
        data = json.loads(sample_data)
        embed = discord.Embed(color=0xff0000)
        embed.title = 'Your Career'
        embed.description = f'You have run {data["Steve"]["Run Count"]} games with an average time of {data["Steve"]["Avg Time"]} seconds!'
        await ctx.send(embed=embed)