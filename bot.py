import asyncio
import os
import time
import typing
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
import async_scheduling
import utils
import subscriptions
import birthday_calendar as bc
from config import PREFIX, LINK, PUBLISH_BIRTHDAYS_TIME

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()  
intents.members = True

bot = commands.Bot(command_prefix = PREFIX, intents=intents)

# Dictionary to store the jobs per channel id to be able to unsubscribe and therefore cancel the job for the unsubscribing channel
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
    # Only add new subscription if channel is not subscribed yet
    if ctx.channel.id not in scheduled_subscription_jobs:
        await _subscribe_channel(ctx.channel)
    
        await ctx.send(f"Subscription successful.")
    else:
        await ctx.send(f"Already subscribed.")
    

async def _subscribe_channel(channel):
    """
    Schedules a job to be executed at PUBLISH_BIRTHDAYS_TIME from config.py.

    Args:
        channel_id: discord.py channel
    """
    async_scheduling.new_task(channel, publish_daily_birthdays, PUBLISH_BIRTHDAYS_TIME, scheduled_subscription_jobs)

@bot.command()
async def unsubscribe(ctx):
    """
    Removes a job associated with the guild_id derived from the context from the global dictionary `scheduled_subscription_jobs`
    and cancel the job from the scheduler.

    Args:
        ctx: discord.py context
    """
    # Only try to remove subscription if channel is already subscribed
    if ctx.channel.id in scheduled_subscription_jobs:
        async_scheduling.remove_task(ctx.channel, scheduled_subscription_jobs)
        await ctx.send(f"Successfully unsubsribed.")
    else:
        await ctx.send(f"Not subscribed yet.")

@async_scheduling.repeatable_decorator(jobs_dict=scheduled_subscription_jobs, time=PUBLISH_BIRTHDAYS_TIME)
async def publish_daily_birthdays(guild_channel):
    """
    Fetches todays birthdays and publishes it to the given context.
    
    On subscription a task is created and scheduled to execute this coroutine with the correct context
    (e.g. to send the message to the channel, that the subscribe command was called in).

    Args:
        guild_channel: discord.py discord.abc.GuildChannel
    """
    birthdays = await bc.get_todays_birthdays(guild_channel.id)
    output = utils.make_output_table(birthdays)
    await guild_channel.send(f"Heutige Geburtstage:\n```\n{output}\n```")

      
@bot.event
async def on_ready():
    print("----------------------")
    print("Beigetreten als")
    print("Username: %s"%bot.user.name)
    print("ID: %s"%bot.user.id)
    print("Zeit: %s"%datetime.now().time())
    print("----------------------")

    # Load saved subscriptions
    subs_list = subscriptions.load_subscribed_channels()
    channels = [await bot.fetch_channel(channel_id) for channel_id in subs_list]
    await asyncio.gather(*[_subscribe_channel(channel) for channel in channels])

    print("Scheduled subscription jobs")
    print(scheduled_subscription_jobs)
    print("----------------------")

    # Run periodically scheduled tasks
    bot.loop.create_task(async_scheduling.run_scheduled_jobs(sleep=1))
  
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

if __name__ == "__main__":
    bot.run(TOKEN)
