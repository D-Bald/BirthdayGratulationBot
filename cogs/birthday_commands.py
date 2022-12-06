import disnake
from disnake.ext import commands

from utils import datetime_tools
import daos.birthday_calendar as bc


class BirthdayCommands(commands.Cog):
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
        date_list = await bc.BirthdayCalendar(inter.guild.id).list_birthdays()

        output = bc.make_output_table(date_list)
        await inter.send(f"Geburtstage:\n```\n{output}\n```")

    @commands.slash_command()
    async def birthday(self,
                       inter: disnake.ApplicationCommandInteraction,
                       name: str,
                       date: str = commands.Param(default="")
                       ):
        """Sends birthday date for given name or creates new entry if a date is passed."""
        """
        Depending on the input either sends back the birthday associated to the given name in the guild derived by the context
        or stores a new birthday if a date is passed.

        Args:
            inter: disnake.ApplicationCommandInteraction object
            name: name of the person the birthday should be fetched or stored
            date (default: None): date of the birthday that should be stored
        """
        # Erstelle Instanz eines Kalenders für die gegebene guild_id
        cal = bc.BirthdayCalendar(inter.guild.id)

        # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) bereits ein Eintrag existiert.
        # Falls nicht, füge diesen hinzu, falls ein Datum angegeben wurde.
        if await cal.exists_entry(name):
            # Falls ein Datum angegeben wurde, wird der bestehende Eintrag nicht überschrieben
            if date: # Empty string `""` is treated as `False`
                await inter.send(
                    f"Geburtstag von {name} schon gespeichert.\nZum Löschen verwende `/forgetbirthday {name}`"
                )
            # Falls kein Datum angegeben wurde, sende den gespeicherten Geburtstag zurück
            else:
                birthday = await cal.get_birthday(name)
                output = bc.make_output_table_for_birthday(birthday)
                await inter.send(f"Geburtstag:\n```\n{output}\n```")
        else:
            if date:
                if datetime_tools.check_date_format(date):
                    birthday = await cal.add_entry(name, date)
                    output = bc.make_output_table_for_birthday(birthday)
                    await inter.send(
                        f"Geburtstag gespeichert:\n```\n{output}\n```")
                else:
                    await inter.send(
                        f"Das Datum ist nicht im richtigen Format: TT.MM.YYYY")
            # Falls kein Datum angegeben und kein name gefunden wurde, kann kein Geburtstag zurückgeschickt werden.
            else:
                await inter.send(
                    f"Geburtstag von {name} konnte nicht gefunden werden.")

    @commands.slash_command()
    async def forgetbirthday(inter: disnake.ApplicationCommandInteraction,
                             name: str):
        """Removes the entry associated to the given name and guild derived from the interaction."""
        """
        Args:
            inter: disnake.ApplicationCommandInteraction object
            name: name of the person the birthday should be removed
        """
        # Erstelle Instanz eines Kalenders für die gegebene guild_id
        cal = bc.BirthdayCalendar(inter.guild.id)

        # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) ein Eintrag existiert.
        # Lösche den Eintrag nur, falls das der Fall ist.
        if not await cal.exists_entry(name):
            await inter.send(
                f"Geburtstag von {name} konnte nicht gefunden werden.")
        else:
            await cal.remove_entry(name)
            await inter.send(f"Geburtstag von {name} wurde gelöscht.")


def setup(bot: commands.Bot):
    bot.add_cog(BirthdayCommands(bot))
