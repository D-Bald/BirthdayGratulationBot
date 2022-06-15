import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle

def create_output_table(df):
    body = []
    for i in df.index:
        body.append([df["name"].iloc[i], df["date"].iloc[i]])

    output = t2a(
        header=["Name", "Datum"],
        body=body,
        style=PresetStyle.thin_compact
    )

    return output


def create_output_table_for_name(df: pd.DataFrame, name: str):
    # Suche den Eintrag für den gegebenen Namen
    birthday = df.iloc[df[df["name"] == name].index[0]]

    # Erstelle Tabelle
    output = t2a(
        header=["Name", "Datum"],
        body=[[birthday["name"], birthday["date"]]],
        style=PresetStyle.thin_compact
    )

    return output