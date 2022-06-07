import discord
from redbot.core import Config, commands
from discord.ext import tasks
import mysql.connector


class Diablo2Res(commands.Cog):
    """ Used to access various D2R information """

    __version__ = '1.0.0'

    def __init__(self, bot):
        self.bot = bot

    async def red_delete_data_for_user(self, *, requester, user_id):
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f'{context}\n\nVersion: {self.__version__}'

    # Runes
    @commands.command()
    async def rune(self, ctx: commands.Context, rune: str):
        try:
            db = await self.connect_sql()
            cursor = db.cursor(dictionary=True)
            sql = """SELECT * FROM runes WHERE name like CONCAT('%', %s, '%') LIMIT 1;"""
            cursor.execute(sql, (rune,))
            result = cursor.fetchall()
            if len(result) < 0:
                await ctx.send(f'{rune} was not found.')
                return

            for row in result:
                embed = discord.Embed(color=0xff0000)
                embed.set_author(name=ctx.guild.name,
                                 icon_url=ctx.guild.icon_url)
                embed.title = f"{row['name']} ({row['id']})"
                embed.image(
                    'https://img.rankedboost.com/wp-content/plugins/diablo-2/assets/runes/El.png')
                embed.add_field(
                    name="Info",
                    value=f"Required Level: {row['level']}",
                    inline=False
                )
                embed.add_field(
                    name="Attributes",
                    value=f"{row['attributes']}",
                    inline=False
                )
                embed.add_field(
                    name="Recipe",
                    value=f"{row['recipe']}",
                    inline=False
                )
                embed.add_field(
                    name="Runewords",
                    value=f"{row['runewords']}",
                    inline=False
                )

                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        except mysql.connector.ProgrammingError as error:
            print(
                f'Error Number: {error.errno}\nSQL State: {error.sqlstate}\nError Message: {error.msg}')
        except mysql.connector.Error as error:
            print(
                f'There has been an error. Send this to David for help. {error}')
        except:
            print('Unknown Error!')
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    async def connect_sql(self):
        host = 'localhost'
        user = 'd2r'
        password = 'pWrI4m8k@FEUVaSu'

        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=user
        )
