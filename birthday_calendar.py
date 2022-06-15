import datetime
import pandas as pd
import utils

FILEPATH = './data/dates.csv'


def get_dates():
    """Get all birthday dates.

    Returns:
        All birthdays as pandas DataFrame with columns `name`, `date` and `dates_left`.
    """
    df = pd.read_csv(FILEPATH)
    df["days_left"] = df["date"].apply(days_left)
    df = df.sort_values(by=["days_left", "name"]).reset_index(drop=True)
    return df


def exists_entry(name: str):
    """Checks if an entry with the given name exists.

    Args:
        name: the name of the person as string

    Returns:
        `True` if an entry exists, `False` else.
    """
    df = get_dates()
    return any(df.name == name)

def add_entry(name, date: str):
    """Adds an entry with given name and date to the repository.

    Args:
        name: the name of the person as string
        date: the birthday date as a string

    Returns:
        The added birthday as pandas DataFrame with columns `name` and `date`.
    """
    df_new = pd.DataFrame({"name": [name], "date": [utils.format_date_string(date)], "days_left": days_left(date)})
    df_dates = pd.concat(
        [get_dates(), df_new],
        ignore_index=True,
    )
    df_csv = df_dates.drop(["days_left"], axis=1)
    df_csv.to_csv(FILEPATH, index=False)

    return df_dates

def remove_entry(name):
    """Removes an entry with given name from the repository.

    Args:
        name: the name of the person as string
    """
    df_dates = get_dates()
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

if __name__ == "__main__":
    # print(days_left("14.06.1994"))
    pass