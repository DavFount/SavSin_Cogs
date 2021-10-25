import discord
import json
from redbot.core import Config, checks, commands
from datetime import datetime

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

        self.config.register_guild(host=None, port=None, db=None, user=None, password=None)

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
    async def chx_top(self, ctx: commands.Context, count: int):
        """ Displays embed with top runners """
        if count > 25:
            count = 25
        data = json.loads(sample_data)
        embed = discord.Embed(color=0xff0000)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
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

    @chx_admin.command(name="settings")
    async def chx_admin_settings(self, ctx: commands.Context):
        """See current settings."""
        data = await self.config.guild(ctx.guild).all()

        if data["password"]:
            password = 'Set'
        else:
            password = 'Not Set'

        embed = discord.Embed(
            colour=await ctx.embed_colour(), timestamp=datetime.now()
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = '**__Unique Name settings:__**'
        embed.set_footer(text='*required to function properly')

        embed.add_field(name='Hostname*:', value=data["host"])
        embed.add_field(name='Port*:', value=data["port"])
        embed.add_field(name='Database*:', value=data["db"])
        embed.add_field(name='Username*:', value=data["user"])
        embed.add_field(name='Password*:', value=password)

        await ctx.send(embed=embed)
