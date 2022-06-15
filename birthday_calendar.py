import pandas as pd

FILEPATH = './data/dates.csv'


def get_dates():
    """Get all birthday dates.

    Returns:
        All birthdays as pandas DataFrame with columns `name` and `date`.
    """
    df = pd.read_csv(FILEPATH)
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
    df_new = pd.DataFrame({"name": [name], "date": [date]})
    df_dates = pd.concat(
        [get_dates(), df_new],
        ignore_index=True,
    )
  
    df_dates.to_csv(FILEPATH, index=False)

    return df_dates

def remove_entry(name):
    """Removes an entry with given name from the repository.

    Args:
        name: the name of the person as string
    """
    df_dates = get_dates()
    df_dates = df_dates.drop(df_dates[df_dates['name'] == name].index)
    df_dates.to_csv(FILEPATH, index=False)