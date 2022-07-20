import typing
import disnake
from disnake.ext import commands

import utils.utils as utils
import controllers.birthday_calendar as bc


class BirthdaysCommands(commands.Cog):
    """Handling interactions to get, post or delete birthday dates."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command()
    async def birthdays(self, inter: disnake.ApplicationCommandInteraction):
        """Sends back a list of the all birthdays associated to the guild derived by the interaction (context)."""
        """
        Args:
            inter: disnake.ApplicationCommandInteraction object
        """
        df_dates = await bc.get_birthdays(inter.guild.id)
        output = utils.make_output_table(df_dates)
        await inter.send(f"Geburtstage:\n```\n{output}\n```")

    @commands.slash_command()
    async def birthday(self, inter: disnake.ApplicationCommandInteraction, name: str, date: typing.Optional[str] = None):
        """Sends birthday dates for given names or creates new entry if a date is provided."""
        """
        Depending on the input either sends back the birthday associated to the given name in the guild derived by the context
        or stores a new birthday if a date is provided.

        Args:
            inter: disnake.ApplicationCommandInteraction object
            name: name of the person the birthday should be fetched or stored
            date (default: None): date of the birthday that should be stored
        """
        guild_id  = inter.guild.id
        # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) bereits ein Eintrag existiert.
        # Falls nicht, füge diesen hinzu, falls ein Datum angegeben wurde.
        if await bc.exists_entry(name, guild_id):
            # Falls ein Datum angegeben wurde, wird der bestehende Eintrag nicht überschrieben
            if date:
                await inter.send(f"Geburtstag von {name} schon gespeichert.\nZum Löschen verwende `!forgetbirthday {name}`")
            # Falls kein Datum angegeben wurde, sende den gespeicherten Geburtstag zurück
            else:
                df_dates = await bc.get_birthdays(guild_id)
                output = utils.make_output_table_for_name(df_dates, name)
                await inter.send(f"Geburtstag:\n```\n{output}\n```")
        else:
            if date:
                if utils.check_date_format(date):
                    df_dates = await bc.add_entry(name, date, guild_id)
                    output = utils.make_output_table_for_name(df_dates, name)
                    await inter.send(f"Geburtstag gespeichert:\n```\n{output}\n```")
                else:
                    await inter.send(f"Das Datum ist nicht im richtigen Format: TT.MM.YYYY")
            # Falls kein Datum angegeben und kein name gefunden wurde, kann kein Geburtstag zurückgeschickt werden.
            else:
                await inter.send(f"Geburtstag von {name} konnte nicht gefunden werden.")

    @commands.slash_command()
    async def forgetbirthday(ctx, name: str):
        """Removes the entry associated to the given name and guild derived from the context."""
        """
        Args:
            inter: disnake.ApplicationCommandInteraction object
            name: name of the person the birthday should be removed
        """
        guild_id  = ctx.guild.id
        # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) ein Eintrag existiert.
        # Lösche den Eintrag nur, falls das der Fall ist.
        if not await bc.exists_entry(name, guild_id):
            await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")
        else:
            await bc.remove_entry(name, guild_id)
            await ctx.send(f"Geburtstag von {name} wurde gelöscht.")

def setup(bot: commands.Bot):
    bot.add_cog(BirthdaysCommands(bot))