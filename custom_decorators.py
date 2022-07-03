import functools
from datetime import datetime
import utils

# Following the recipe from https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
def repeatable(jobs_dict={}, time=datetime.now().time().strftime("%H:%M")):
    """
    Removes and reschedules a function using the scheduler package.

    This is an ugly bugfix to work around the exception:
        RuntimeError('cannot reuse already awaited coroutine')
    
    Args:
        jobs_dict: dictionary containing all scheduled jobs associated to the guild_id
        time: time to that the function should be rescheduled. Defaults to the current time when decorator is invoked.

    Returns:
        A decorator function that expects the wrapped function to pass a discord.py context as first positional argument.
    """
    def decorator_repeatable(func):
        @functools.wraps(func)
        def wrapper_repeatable(ctx, *args, **kwargs):
            value = func(ctx, *args, **kwargs)

            # Check if job already exists (not true for first subscription)
            if ctx.guild.id in jobs_dict:
                # Remove and cancel old job
                utils.remove_task(ctx, jobs_dict)
                # Schedule new job
                utils.schedule_task(ctx, func, time, jobs_dict)
              
            return value
        return wrapper_repeatable    
    return decorator_repeatable
    