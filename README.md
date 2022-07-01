# Birthday Gratulation Bot
Discord bot to celebrate assigned birthdays.

## Setup
Follow the steps to create an account (if you don't have one yet), application and bot from [RealPython](https://realpython.com/how-to-make-a-discord-bot-python/). Also follow the steps to add the bot to add

Create a `.env` file with the entry

```console
DISCORD_TOKEN = "YOUR_TOKEN_GOES_HERE"
```

Set the Command `PREFIX` (currently `!`), the invitation `LINK` you get following the RealPython tutorial.
You can also edit the `DATE_FORMAT` (currently `'%d.%m.%Y'`) and time when birthdays are published each day (`PUBLISH_BIRTHDAYS_TIME`).

## Commands
- `!birthdays`
- `!birthday name [date]`
 - `name` can be one name without whitespace or more names (like first and last name) within quotation marks: `!addbirthday "first last" date`
 - `date` is optional. If it is passed, the command tries to add a new entry with the given `name` and `date`, but will not go on, if an entry for the given name exists. If `date` is left blank then the command tries to fetch the stored birthday for the given `name`.
- `!forgetbirthday name`
 - the same rules for `name` as in `!addbirthday` apply here.
- `!subscribe`
- `!unsubscribe`

## License
MIT License. Copyright (c) 2022 David Baldauf.