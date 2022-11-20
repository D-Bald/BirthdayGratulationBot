# Birthday Gratulation Bot
Discord bot to celebrate assigned birthdays.

## Usage

Add the bot to your server by clicking [here](https://discord.com/api/oauth2/authorize?client_id=952656778007552090&permissions=380104763456&scope=bot)


## Slash Commands
- `/birthdays` - sends back a list of the all birthdays associated to the guild derived by the context.
- `/birthday name [date]` - either sends back the birthday associated to the given name in the guild derived by the context or stores a new birthday if a date is provided, depending on the input.
  - `name` can be one name without whitespace or more names (like first and last name) within quotation marks: `/birthday "first last" date`
  - `date` is optional. If it is passed, the command tries to add a new entry with the given `name` and `date`, but will not go on, if an entry for the given name exists. If `date` is left blank then the command tries to fetch the stored birthday for the given `name`.
- `/forgetbirthday name` - removes the entry associated to the given name and guild derived from the context.
  - the same rules for `name` as in `/birthday` apply here.
- `/subscribe` - to daily gratulation of todays birthdays.
- `/unsubscribe` - of daily gratulation.

## License
MIT License. Copyright (c) 2022 David Potschka.