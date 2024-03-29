from disnake.ext import commands

import os
from dotenv import load_dotenv

import asyncio
from datetime import datetime
from pprint import pprint

from daos.subscriptions import Subscriptions
from utils import subscriptions_controller
from cogs.subscription_commands import SubscriptionCommands

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]

bot = commands.InteractionBot()


def main():
    # bot.load_extension("cogs.birthday_commands")
    # bot.load_extension("cogs.subscription_commands")
    # bot.load_extension("cogs.bot_management_commands")
    bot.load_extensions("./cogs")

    bot.run(TOKEN)


@bot.event
async def on_ready():
    print_start_message()

    # Load saved subscriptions
    subs_list = Subscriptions.all()
    
    channels = [
        await bot.fetch_channel(channel_id) for channel_id in subs_list
    ]
    await asyncio.gather(*[
        SubscriptionCommands.subscribe_channel(channel) for channel in channels
    ])

    # Run periodically scheduled tasks
    bot.loop.create_task(subscriptions_controller.run_scheduled_jobs(sleep=1))


def print_start_message():
    print("----------------------")
    print("Beigetreten als")
    print("Username: %s" % bot.user.name)
    print("ID: %s" % bot.user.id)
    print("Zeit: %s" % datetime.now().time())
    print("----------------------")
    print("Verfügbare Slash Commands\n")
    pprint([{
        "name": command.name,
        "description": command.description,
        "options": command.options
    } for command in bot.global_slash_commands],
           sort_dicts=False)
    print("----------------------")


if __name__ == "__main__":
    main()
