from table2ascii import table2ascii as t2a, PresetStyle
import pandas as pd

FILEPATH = './data/dates.csv'
df_dates = pd.read_csv(FILEPATH)
body = []
for i in df_dates.index:
    print(i)
    body.append([df_dates["name"].iloc[i], df_dates["date"].iloc[i]])

output = t2a(
    header=["Name", "Datum"],
    body=body,
    style=PresetStyle.thin_compact
)

print(output)