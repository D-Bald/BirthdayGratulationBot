import os
import time
import discord
from discord.ext import commands
import typing
import pandas as pd
from dotenv import load_dotenv
from config import PREFIX, LINK
import utils


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
FILEPATH = './data/dates.csv'

intents = discord.Intents.default()  
intents.members = True

bot = commands.Bot(command_prefix = PREFIX, intents=intents)

@bot.command()
async def birthdays(ctx):
    df_dates = pd.read_csv(FILEPATH)
    output = utils.create_output_table(df_dates)
    await ctx.send(f"Geburtstage:\n```\n{output}\n```")

@bot.command()
async def birthday(ctx, name: str, date: typing.Optional[str] = None):
    df_dates = pd.read_csv(FILEPATH)

    # Checke ob zum gegebenen Namen bereits ein Eintrag existiert.
    # Falls nicht, füge diesen hinzu, falls ein Datum angegeben wurde.
    if any(df_dates.name == name):
        # Falls ein Datum angegeben wurde, wird der bestehende Eintrag nicht überschrieben
        if date:
            await ctx.send(f"Geburtstag von {name} schon gespeichert.\nZum Löschen verwende `!forgetbirthday {name}`")
        # Falls kein Datum angegeben wurde, sende den gespeicherten Geburtstag zurück
        else:
            output = utils.create_output_table_for_name(df_dates, name)
            await ctx.send(f"Geburtstag:\n```\n{output}\n```")
    else:
        if date:
            df_new = pd.DataFrame({"name": [name], "date": [date]})
            df_dates = pd.concat([df_dates, df_new],
                        ignore_index=True,
                    )
            df_dates.to_csv(FILEPATH, index=False)

            output = utils.create_output_table_for_name(df_dates, name)
            await ctx.send(f"Geburtstag gespeichert:\n```\n{output}\n```")
        # Falls kein Datum angegeben und kein name gefunden wurde, kann kein Geburtstag zurückgeschickt werden.
        else:
            await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")

@bot.command()
async def forgetbirthday(ctx, name: str):
    df_dates = pd.read_csv(FILEPATH)
    # Checke ob zum gegebenen Namen ein Eintrag existiert.
    # Lösche den Eintrag nur, falls das der Fall ist.
    if not any(df_dates.name == name):
        await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")
    else:
        df_dates = df_dates.drop(df_dates[df_dates['name'] == name].index)
        df_dates.to_csv(FILEPATH, index=False)
        await ctx.send(f"Geburtstag von {name} wurde gelöscht.")

### Events and commands unrelated to birthday-gratulation-bot ###

@bot.event
async def on_ready():
    print("----------------------")
    print("Beigetreten als")
    print("Username: %s"%bot.user.name)
    print("ID: %s"%bot.user.id)
    print("----------------------")

@bot.command()
async def ping(ctx):
    '''See if The Bot is Working'''
    ping = time.time()
    pingmsg = await ctx.send("Pinging...")
    pingtime = time.time() - ping
    await pingmsg.edit(content = ":ping_pong:  time is `%.01f seconds`" % pingtime)
    
@bot.command()
async def botinvite(ctx, recipient: discord.Member = None):
    '''A Link To Invite This Bot To Your Server!'''
    await ctx.send("Check Your Dm's :wink:")
    message = f"Add me to Your Server: {LINK}"
    if recipient:
        await recipient.send(message)
    else:
        await ctx.author.send(message)

@bot.command()
async def serverinfo(ctx):
    '''Displays Info About The Server!'''

    guild = ctx.guild
    roles = [x.name for x in guild.roles]
    role_length = len(roles)

    if role_length > 50: #Just in case there are too many roles...
        roles = roles[:50]
        roles.append('>>>> Displaying[50/%s] Roles'%len(roles))

    roles = ', '.join(roles)
    channels = len(guild.channels)
    time = str(guild.created_at); time = time.split(' '); time= time[0]

    join = discord.Embed(description= '%s '%(str(guild)),title = 'Server Info', colour = 0xFFFF)
    join.set_thumbnail(url = guild.icon_url)
    join.add_field(name = '__Owner__', value = str(guild.owner) + '\n' + str(guild.owner_id))
    join.add_field(name = '__ID__', value = str(guild.id))
    join.add_field(name = '__Member Count__', value = str(guild.member_count))
    join.add_field(name = '__Text/Voice Channels__', value = str(channels))
    join.add_field(name = '__Roles (%s)__'%str(role_length), value = roles)
    join.set_footer(text ='Created: %s'%time)

    await ctx.send(embed = join)


bot.run(TOKEN)