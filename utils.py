import datetime
import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle

def make_output_table(df):
    body = []
    for i in df.index:
        entry = [df["name"].iloc[i], df["date"].iloc[i], df["days_left"].apply(_gratulation_if_zero_days_left).iloc[i]]
        body.append(entry)

    output = t2a(
        header=["Name", "Datum", "Verbleibende Tage"],
        body=body,
        style=PresetStyle.thin_compact
    )

    return output

def make_output_table_for_name(df: pd.DataFrame, name: str):
    # Suche den Eintrag für den gegebenen Namen
    birthday = df.iloc[df[df["name"] == name].index[0]]

    # Erstelle Tabelle
    output = t2a(
        header=["Name", "Datum", "Verbleibende Tage"],
        body=[[birthday["name"], birthday["date"], _gratulation_if_zero_days_left(birthday["days_left"])]],
        style=PresetStyle.thin_compact
    )

    return output

def check_date_format(date: str):
    """Checks if the given date hase the date format `"%d.%m.%Y"`.

    Args:
        date: the date as string

    Returns:
        `True` if the date is in the correct format, `False` else.
    """
    res = True
    try:
        res = bool(datetime.datetime.strptime(date, "%d.%m.%Y"))
    except ValueError:
        res = False
    return res

def string_to_datetime(date_str: str):
    """Parses a date string to datetime format.

    Args:
        date_str: the date as string with format `"%d.%m.%Y"`
    
    Returns:
        Datetime object with given date and time "00:00:00"
    """
    date = datetime.datetime.strptime(date_str, "%d.%m.%Y")
    return date

def format_date_string(date_str: str):
    """parses a date string to string with format "dd.mm.yyy".

    Args:
        date_str: the date as string with format `"%d.%m.%Y"`
    
    Returns:
        Given date as string in format "dd.mm.yyy"
    """
    date = string_to_datetime(date_str)
    return datetime.datetime.strftime(date, "%d.%m.%Y")

def _gratulation_if_zero_days_left(days_left):
    if days_left == 0:
        return "Herzlichen Glückwunsch!"
    else:
        return days_left