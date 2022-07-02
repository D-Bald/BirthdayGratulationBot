import os
import time
import discord
import typing
from discord.ext import commands
from dotenv import load_dotenv
from config import PREFIX, LINK, PUBLISH_BIRTHDAYS_TIME
import birthday_calendar as bc
import utils

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()  
intents.members = True

bot = commands.Bot(command_prefix = PREFIX, intents=intents)

# Dictionary to store the jobs per guild to be able to unsubscribe and therefore cancel the job for the unsubscribing guild
scheduled_subscription_jobs = {}

@bot.command()
async def birthdays(ctx):
    """
    Sends back a list of the all birthdays associated to the guild derived by the context.

    Args:
        ctx: discord.py context
    """
    df_dates = await bc.get_birthdays(ctx.guild.id)
    output = utils.make_output_table(df_dates)
    await ctx.send(f"Geburtstage:\n```\n{output}\n```")

@bot.command()
async def birthday(ctx, name: str, date: typing.Optional[str] = None):
    """
    Depending on the input either sends back the birthday associated to the given name in the guild derived by the context
    or stores a new birthday if a date is provided.

    Args:
        ctx: discord.py context
        name: name of the person the birthday should be fetched or stored
        date (default: None): date of the birthday that should be stored
    """
    guild_id  = ctx.guild.id
    # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) bereits ein Eintrag existiert.
    # Falls nicht, füge diesen hinzu, falls ein Datum angegeben wurde.
    if await bc.exists_entry(name, guild_id):
        # Falls ein Datum angegeben wurde, wird der bestehende Eintrag nicht überschrieben
        if date:
            await ctx.send(f"Geburtstag von {name} schon gespeichert.\nZum Löschen verwende `!forgetbirthday {name}`")
        # Falls kein Datum angegeben wurde, sende den gespeicherten Geburtstag zurück
        else:
            df_dates = await bc.get_birthdays(guild_id)
            output = utils.make_output_table_for_name(df_dates, name)
            await ctx.send(f"Geburtstag:\n```\n{output}\n```")
    else:
        if date:
            if utils.check_date_format(date):
                df_dates = await bc.add_entry(name, date, guild_id)
                output = utils.make_output_table_for_name(df_dates, name)
                await ctx.send(f"Geburtstag gespeichert:\n```\n{output}\n```")
            else:
                await ctx.send(f"Das Datum ist nicht im richtigen Format: TT.MM.YYY")
        # Falls kein Datum angegeben und kein name gefunden wurde, kann kein Geburtstag zurückgeschickt werden.
        else:
            await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")

@bot.command()
async def forgetbirthday(ctx, name: str):
    """
    Removes the entry associated to the given name and guild derived from the context.

    Args:
        ctx: discord.py context
        name: name of the person the birthday should be removed
    """
    guild_id  = ctx.guild.id
    # Checke ob zum gegebenen Namen auf dem aktuellen Server (`guild_id`) ein Eintrag existiert.
    # Lösche den Eintrag nur, falls das der Fall ist.
    if not await bc.exists_entry(name, guild_id):
        await ctx.send(f"Geburtstag von {name} konnte nicht gefunden werden.")
    else:
        await bc.remove_entry(name, guild_id)
        await ctx.send(f"Geburtstag von {name} wurde gelöscht.")

@bot.command()
async def subscribe(ctx):
    """
    Schedules a job to be executed at PUBLISH_BIRTHDAYS_TIME from config.py.

    Args:
        ctx: discord.py context
    """
    # Only add new subscription if guild is not subscribed yet
    if ctx.guild.id in scheduled_subscription_jobs:
        utils.schedule_task(ctx, publish_daily_birthdays, PUBLISH_BIRTHDAYS_TIME, scheduled_subscription_jobs)
    
        await ctx.send(f"Subscription successful.")
    else:
        await ctx.send(f"Already subscribed.")

@bot.command()
async def unsubscribe(ctx):
    """
    Removes a job associated with the guild_id derived from the context from the global dictionary `scheduled_subscription_jobs`
    and cancel the job from the scheduler.

    Args:
        ctx: discord.py context
    """
    utils.remove_task(ctx, scheduled_subscription_jobs)
    
    await ctx.send(f"Successfully unsubsribed.")

async def publish_daily_birthdays(ctx):
    """
    Fetches todays birthdays and publishes it to the given context.
    
    On subscription a task is created and scheduled to execute this coroutine with the correct context
    (e.g. to send the message to the channel, that the subscribe command was called in).

    Args:
        ctx: discord.py context
    """
    birthdays = await bc.get_todays_birthdays(ctx.guild.id)
    output = utils.make_output_table(birthdays)
    await ctx.send(f"Heutige Geburtstage:\n```\n{output}\n```")

    # This is an ugly bugfix to work around the exception:
    #    RuntimeError('cannot reuse already awaited coroutine')
    # Remove and cancel old Job
    utils.remove_task(ctx,scheduled_subscription_jobs)
    # Schedule new Job
    utils.schedule_task(ctx, publish_daily_birthdays, PUBLISH_BIRTHDAYS_TIME, scheduled_subscription_jobs)



      
@bot.event
async def on_ready():
    print("----------------------")
    print("Beigetreten als")
    print("Username: %s"%bot.user.name)
    print("ID: %s"%bot.user.id)
    print("----------------------")

    # Run periodically scheduled tasks
    bot.loop.create_task(utils.run_scheduled_jobs(sleep=1))
  
### Events and commands unrelated to birthday-gratulation-bot ###
  
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

    # Just in case there are too many roles...
    if role_length > 50:
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