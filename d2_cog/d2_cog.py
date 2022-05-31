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
            cursor = db.cursor
            sql = """SELECT * FROM runes WHERE name = %s LIMIT 1;"""
            val = (rune,)
            cursor.execute(sql, val)
            if len(cursor) < 0:
                await ctx.send(f'{rune} was not found.')
                return

            for (id, name, level, attributes, recipe, runewords) in cursor:
                await ctx.send(
                    f"Found {name}(#{id}):\nRequired Level: {level}\nAttributes:{attributes}\nRecipe:{recipe}\nRunewords:{runewords}")

            cursor.close()
            db.close()
        except mysql.connector.ProgrammingError as error:
            await ctx.send(f'Error Number: {error.errno}\nSQL State: {error.sqlstate}\nError Message: {error.msg}')
        except mysql.connector.Error as error:
            await ctx.send(f'There has been an error. Send this to David for help. {error}')
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