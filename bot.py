import os
import time
import discord
from discord.ext import commands
import typing
from dotenv import load_dotenv
from config import PREFIX, LINK
import birthday_calendar as bc
import utils


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()  
intents.members = True

bot = commands.Bot(command_prefix = PREFIX, intents=intents)

@bot.command()
async def birthdays(ctx):
    df_dates = bc.get_birthdays(ctx.guild.id)
    output = utils.make_output_table(df_dates)
    await ctx.send(f"Geburtstage:\n```\n{output}\n```")

@bot.command()
async def birthday(ctx, name: str, date: typing.Optional[str] = None):
    guild_id  = ctx.guild.id
    # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) bereits ein Eintrag existiert.
    # Falls nicht, füge diesen hinzu, falls ein Datum angegeben wurde.
    if bc.exists_entry(name, guild_id):
        # Falls ein Datum angegeben wurde, wird der bestehende Eintrag nicht überschrieben
        if date:
            await ctx.send(f"Geburtstag von {name} schon gespeichert.\nZum Löschen verwende `!forgetbirthday {name}`")
        # Falls kein Datum angegeben wurde, sende den gespeicherten Geburtstag zurück
        else:
            df_dates = bc.get_birthdays(guild_id)
            output = utils.make_output_table_for_name(df_dates, name)
            await ctx.send(f"Geburtstag:\n```\n{output}\n```")
    else:
        if date:
            if utils.check_date_format(date):
                df_dates = bc.add_entry(name, date, guild_id)
                output = utils.make_output_table_for_name(df_dates, name)
                await ctx.send(f"Geburtstag gespeichert:\n```\n{output}\n```")
            else:
                await ctx.send(f"Das Datum ist nicht im richtigen Format: TT.MM.YYY")
        # Falls kein Datum angegeben und kein name gefunden wurde, kann kein Geburtstag zurückgeschickt werden.
        else:
            await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")

@bot.command()
async def forgetbirthday(ctx, name: str):
    guild_id  = ctx.guild.id
    # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) ein Eintrag existiert.
    # Lösche den Eintrag nur, falls das der Fall ist.
    if not bc.exists_entry(name, guild_id):
        await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")
    else:
        bc.remove_entry(name, guild_id)
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