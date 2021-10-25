import discord
import json
from redbot.core import commands

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
    """ Chaox Cog for Game Spamming """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def top(self, ctx, count: int):
        """ Displays embed with top runners """
        if count > 25:
            count = 25
        data = json.loads(sample_data)
        embed = discord.Embed(color=0x00ff00)
        embed.title = f"Top {count} Runners"
        message = ''
        count = 1
        for (k,v) in data.items():
            message += f'{count}. {k} (Count: {v["Run Count"]})\n'
            count += 1

        embed.description = message
        await ctx.author.send(embed=embed)

    @commands.command()
    async def mycareer(self, ctx):
        """ Display Embed with Career Stats """
        data = json.loads(sample_data)
        embed = discord.Embed(color=0xff0000)
        embed.title = "Your Career"
        embed.description = f'You have run {data["Steve"]["Run Count"]} games with an average time of {data["Steve"]["Avg Time"]} seconds!'
        await ctx.author.send(embed=embed)