import asyncio
import functools
import schedule

from disnake.abc import GuildChannel

from datetime import datetime
from pprint import pprint
from daos.subscriptions import Subscriptions


# Dictionary to store the jobs per channel id to be able to unsubscribe and therefore cancel the job for the unsubscribing channel
_scheduled_subscription_jobs = {}


# Following the recipe from https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
def run_daily_at(time=datetime.now().time().strftime("%H:%M:00")):
    """
    Removes and reschedules a function using the scheduler package.

    This is an ugly bugfix to work around the exception:
        RuntimeError('cannot reuse already awaited coroutine')
    
    Args:
        time: time to that the function should be rescheduled. Defaults to the current time when decorator is invoked.

    Returns:
        A decorator function that expects the wrapped function to pass a discord.py GuildChannel as first positional argument.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(guild_channel: GuildChannel, *args, **kwargs):
            value = await func(guild_channel, *args, **kwargs)
            # Remove and cancel old job
            _cancel_task(guild_channel)
            # Schedule new job
            _schedule_task(guild_channel, decorator(func), time)

            return value

        return wrapper

    return decorator


def is_scheduled(channel_id: int) -> bool:
    """
    Checks if a job exists that is associated to the given `guild_channel`.

    This is an ugly bugfix to work around the exception:
        RuntimeError('cannot reuse already awaited coroutine')
    
    Args:
        channel_id: The id of the channel to look up in the dictionary of scheduled jobs

    Returns:
        `True` if the entry exists; `False` else
    """
    return channel_id in _scheduled_subscription_jobs


def new_task(guild_channel: GuildChannel, func, time: str):
    """
    Creates new job and stores is it to be remembered on restart.
    
    Calls subscription repo to save the entry persistently.
    Prints out the resulting list of current scheduled jobs.

    Args:
        guild_channel: disnake.abc.GuildChannel to be passed to func
        func: the function that is scheduled as asynchronous task
        time: time in string format that the scheduler uses to schedule the task
    """
    _schedule_task(guild_channel, func, time)

    Subscriptions.save(guild_channel)

    print("----------------------")
    print("Current jobs (channel_id: job_details):\n")
    pprint(_scheduled_subscription_jobs)
    print("----------------------")


def remove_task(guild_channel: GuildChannel):
    """
    Removes the task associated to the given guild_channel.

    Calls subscription repo to delete the entry.
    Prints out the resulting list of current scheduled jobs.

    Args:
        guild_channel: disnake.abc.GuildChannel
    """
    _cancel_task(guild_channel)

    Subscriptions.delete(guild_channel)

    print("----------------------")
    print("Current jobs (channel_id: job_details):\n")
    pprint(_scheduled_subscription_jobs)
    print("----------------------")


async def run_scheduled_jobs(sleep=1):
    """
    Loop to run jobs as soon as the scheduler marks them as pending.
    
    This is executed as task in the handler for the 'on_ready' bot event.

    Args:
        sleep: number of seconds to wait between retries to run pending jobs.
    """
    while True:
        schedule.run_pending()
        await asyncio.sleep(sleep)


def _schedule_task(guild_channel: GuildChannel, func, time: str):
    """
    Schedules new job for the given func that is executed with `guild_channel` as parameter at the given time.
    
    Stores channel_id and job-instance as key-value pair in a global dictionary `scheduled_subscription_jobs` for later cancelation.
    Prints out the resulting list of current scheduled jobs.
    The func is scheduled as asynchronous task so it has to be awaited or run as task itself!

    Args:
        guild_channel: disnake.abc.GuildChannel to be passed to func
        func: the function that is scheduled as asynchronous task
        time: time in string format that the scheduler uses to schedule the task
    """
    job = schedule.every().day.at(time).do(asyncio.create_task, func(guild_channel))
    # job = schedule.every(10).seconds.do(asyncio.create_task, func(guild_channel)) # uncomment for debugging

    _scheduled_subscription_jobs[guild_channel.id] = job


def _cancel_task(guild_channel: GuildChannel):
    """
    Removes the task associated to the given guild_channel in the dictionary and cancels it from scheduler.

    Prints out the resulting list of current scheduled jobs.

    Args:
        guild_channel: disnake.abc.GuildChannel
    """
    job = _scheduled_subscription_jobs.pop(guild_channel.id)
    schedule.cancel_job(job)
