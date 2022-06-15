# BirthdayGratulationBot
Discord bot to celebrate assigned birthdays.

## Setup
Follow the steps to create an account (if you don't have one yet), application and bot from [RealPython](https://realpython.com/how-to-make-a-discord-bot-python/). Also follow the steps to add the bot to add

Create a `.env` file with the entry

```console
DISCORD_TOKEN = "YOUR_TOKEN_GOES_HERE"
```

## Commands
- `!birthdays`
- `!birthday name [date]`
 - `name` can be one name without whitespace or more names (like first and last name) within quotation marks: `!addbirthday "first last" date`
 - `date` is optional. If it is passed, the command tries to add a new entry with the given `name` and `date`, but will not go on, if an entry for the given name exists. If `date` is left blank then the command tries to fetch the stored birthday for the given `name`.
- `!forgetbirthday name`
 - the same rules for `name` as in `!addbirthday` apply here.

## License
MIT License. Copyright (c) 2022 David Baldauf.

# TODO
- Sort list from `!birthdays` alphabetically or by birthday (maybe always from current date)
- Calculate days until the birthday for `!birthday name`
- Gratulation on birthday (on a given time automatically and if someone asks for the name)
- Refactor: Business-Logic in a seperate file => rename main.py in bot.py. Here only the discord.py stuff is happening and the rest is handed over to handler functions.
- Regex check for valid `date` parameter in `!birthday name date`