import datetime
import pandas as pd
import utils

FILEPATH = './data/dates.csv'

def _get_all_birthdays():
    """Get all birthday dates for all guilds.

    Returns:
        All birthdays as pandas DataFrame with columns `name`, `date`, `guild_id` and `dates_left`.
    """
    df = pd.read_csv(FILEPATH)

    df["days_left"] = df["date"].apply(days_left)
    df = df.sort_values(by=["days_left", "name"]).reset_index(drop=True)
    return df
    
def get_birthdays(guild_id: int):
    """Get all birthday dates for a given guild.

    Args:
        guild_id: the id of the guild that the query is run for.

    Returns:
        All birthdays as pandas DataFrame with columns `name`, `date`, `guild_id` and `dates_left`.
    """
    df = pd.read_csv(FILEPATH)

    # Filter for the entrys associated to the given guild_id
    df = df[df["guild_id"] == guild_id]
    df["days_left"] = df["date"].apply(days_left)
    df = df.sort_values(by=["days_left", "name"]).reset_index(drop=True)
    return df

def get_todays_birthdays(guild_id: int):
    df = get_birthdays(guild_id)
    birthdays = df[df["date"].apply(_has_birthday_today)]
    return birthdays
    

def exists_entry(name: str, guild_id: int):
    """Checks if an entry with the given name exists.

    Args:
        name: the name of the person as string

    Returns:
        `True` if an entry exists, `False` else.
    """
    df = get_birthdays(guild_id)
    return any(df.name == name)

def add_entry(name, date: str, guild_id: int):
    """Adds an entry with given name and date to the repository.

    Args:
        name: the name of the person as string
        date: the birthday date as a string

    Returns:
        The added birthday as pandas DataFrame with columns `name` and `date`.
    """
    df_new = pd.DataFrame({"name": [name], "date": [utils.format_date_string(date)], "guild_id": guild_id, "days_left": days_left(date)})
    df_dates = pd.concat(
        [_get_all_birthdays(), df_new],
        ignore_index=True,
    )
    df_csv = df_dates.drop(["days_left"], axis=1)
    df_csv.to_csv(FILEPATH, index=False)

    return df_dates

def remove_entry(name: str, guild_id: int):
    """Removes an entry with given name from the repository.

    Args:
        name: the name of the person as string
    """
    df_dates = get_birthdays(guild_id)
    df_dates = df_dates.drop(df_dates[df_dates['name'] == name].index)

    df_csv = df_dates.drop(["days_left"], axis=1)
    df_csv.to_csv(FILEPATH, index=False)

def days_left(date_str: str):
    """Calculates the number of days until the next birthday.

    Args:
        date_str: the date as string
    
    Returns:
        Days until the next birthday as integer.
    """
    # parse from string
    date = utils.string_to_datetime(date_str)
    # set year to current year
    today = datetime.datetime.today().date()
    date = datetime.datetime(today.year,date.month,date.day).date()

    # check if birthday is this year or next year
    # adjust year accordingly
    if (date - today).days < 0:
        date = datetime.datetime(today.year + 1,date.month,date.day).date()
    
    return (date - today).days

def _has_birthday_today(date_str: str):
    """Checks if the given date matches todays month and day.

    Args:
        date_str: the date as string
    
    Returns:
        `True` if the date indicates a birthday today; `False` else.
    """
    # parse from string
    date = utils.string_to_datetime(date_str)

    today = datetime.datetime.today()
    if (date.month == today.month) and (date.day == today.day):
        return True
    return False

if __name__ == "__main__":
    # print(get_todays_birthdays(949743231594266654))
    pass