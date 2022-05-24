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
            sql = "SELECT * FROM runes WHERE name like CONCAT('%', %s, '%') LIMIT 1;"
            cursor.execute(sql, (rune,))
            if len(cursor) < 0:
                ctx.send(f'{rune} was not found.')
                return

            for (id, name, level, attributes, recipe, runewords) in cursor:
                print(
                    f"Found {name}(#{id}):\nRequired Level: {level}\nAttributes:{attributes}\nRecipe:{recipe}\nRunewords:{runewords}")

            cursor.close()
            db.close()
        except:
            ctx.send('There has been an error. Contact David for support!')

    async def connect_sql(self):
        return mysql.connector.connect(
            host='localhost',
            user='d2r',
            password='ib@R-ONQYv7OmmPq',
            database='d2r'
        )
