import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle
from config import DATES_FILEPATH
from utils import datetime_tools


class BirthdayNotFoundError(Exception):
    pass


class ResultError(Exception):
    pass


class WriteDaysLeftError(Exception):
    pass


class Birthday:
    def __init__(self, name, date, guild_id):
        self.name = name
        self._date = date
        self.guild_id = guild_id

    @property
    def date(self):
        "The date of the birthday stored as string in format "
        return self._date

    @date.setter
    def date(self, date: str):
        datetime_tools.format_date_string(date)

    @property
    def days_left(self):
        """Number of days until the birthdays."""
        return datetime_tools.days_until(self._date)

    @days_left.setter
    def days_left(self, _value):
        return WriteDaysLeftError("days left is a computed attribute")

    def is_today(self):
        if self.days_left == 0:
            return True
        return False


class BirthdayCalendar:
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def list_birthdays(self):
        """
        Lists all birthday dates associated to the guild with id given to `BirthdayCalendar.guild_id` attribute.

        Returns:
            List of `Birthday` objects.
        """
        df = pd.read_csv(DATES_FILEPATH)

        # Filter for the entries associated to the guild_id
        df = df[df["guild_id"] == self.guild_id]

        df["days_left"] = df["date"].apply(datetime_tools.days_until)
        df = df.sort_values(by=["days_left", "name"]).reset_index(drop=True)

        birthdays = [
            Birthday(row["name"], row["date"], self.guild_id)
            for _, row in df.iterrows()
        ]

        return birthdays

    async def get_todays_birthdays(self):
        """
        Gets all entries that have birthday today and are associated to the guild with id given to
        `BirthdayCalendar.guild_id` attribute.

        Returns:
            List of `Birthday` objects.
        """
        dates = await self.list_birthdays()

        # Filter for entries that have birthday today
        birthdays = list(filter(lambda birthday: birthday.is_today(), dates))

        return birthdays

    async def get_birthday(self, name: str):
        """
        Builds a markdown table as code-block from given dataframe and name.

        Args:
            name: the name to filter the df for to create the output

        Returns:
            One `Birthday` object.
        """
        df = await self._get_all_birthdays_as_df()

        # Suche den Eintrag für den gegebenen Namen
        df = df.iloc[df[df["name"] == name].index[0]]

        birthday = Birthday(df["name"], df["date"], self.guild_id)

        return birthday

    async def exists_entry(self, name: str):
        """
        Checks if an entry with the given name exists.

        Args:
            name: the name of the person as string

        Returns:
            `True` if an entry exists, `False` else.
        """
        list_of_birthdays = await self.list_birthdays()
        list_of_name_checks = [
            birthday.name == name for birthday in list_of_birthdays
        ]

        return any(list_of_name_checks)

    async def add_entry(self, name: str, date: str):
        """
        Adds an entry with given name and date to the repository.

        Args:
            name: the name of the person as string
            date: the birthday date as a string

        Returns:
            The added birthday `Birthday` object.
        """
        birthday = Birthday(name, date, self.guild_id)

        df_new = pd.DataFrame({
            "name": [name],
            "date": [datetime_tools.format_date_string(date)],
            "guild_id": self.guild_id
        })
        df = pd.concat(
            [await self._get_all_birthdays(filter_by_guild_id=False), df_new
             ],  # No filtering to not override the file with missing entries.
            ignore_index=True,
        )

        df.to_csv(DATES_FILEPATH, index=False)

        return birthday


    async def remove_entry(self, name: str):
        """
        Removes an entry with given name from the repository.

        Args:
            name: the name of the person as string
        """
        df = await self._get_all_birthdays_as_df()
        df = df.drop(df[(df["name"] == name)].index)

        df.to_csv(DATES_FILEPATH, index=False)


    async def _get_all_birthdays_as_df(self, filter_by_guild_id=True):
        """Gets all birthday dates.

        Args:
            filter_by_guild_id (default: `True`): Query for all guilds if `filter_by_guild_id = False`
                                                  or for the guild_id of this calendar (default)

        Returns:
            All birthdays as pandas DataFrame with columns `name`, `date`, `guild_id`.
        """
        df = pd.read_csv(DATES_FILEPATH)

        if filter_by_guild_id:
            # Filter for the entries associated to the guild_id
            df = df[df["guild_id"] == self.guild_id]

        df["days_left"] = df["date"].apply(datetime_tools.days_until)
        df = df.sort_values(by=["days_left", "name"]).reset_index(drop=True)
        
        return df


#################################################
# Output styling for birthdays
#################################################


def make_output_table(list_of_birthdays):
    """
    Builds a markdown table as code-block from given list of `Birthday` objects.

    Args:
        list_of_birthdays: list of `Birthday` objects

    Returns:
        output string with markdown table containing name, date and days_left or "Herzlichen Glückwunsch" if days_left is equal to zero.
    """
    body = [[bd.name, bd.date,
             _gratulation_if_zero_days_left(bd.days_left)]
            for bd in list_of_birthdays]

    output = t2a(header=["Name", "Datum", "Verbleibende Tage"],
                 body=body,
                 style=PresetStyle.thin_compact)

    return output


def make_output_table_for_birthday(birthday):
    """
    Builds a markdown table as code-block from given `Birthday` object.

    Args:
        birthday: a `Birthday` object

    Returns:
        output string with markdown table containing name, date and days_left or "Herzlichen Glückwunsch" if days_left is equal to zero.
    """

    # Erstelle Tabelle
    output = t2a(header=["Name", "Datum", "Verbleibende Tage"],
                 body=[[
                     birthday.name, birthday.date,
                     _gratulation_if_zero_days_left(birthday.days_left)
                 ]],
                 style=PresetStyle.thin_compact)

    return output


def _gratulation_if_zero_days_left(days_left):
    if days_left == 0:
        return "Herzlichen Glückwunsch!"
    else:
        return days_left
