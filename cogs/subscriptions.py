import disnake
from disnake.ext import commands

import models.birthday_calendar as bc
import utils.subscriptions_controller as subscriptions_controller

from config import PUBLISH_BIRTHDAYS_TIME

class SubscriptionCommands(commands.Cog):
    """Handling interactions manage subscriptions."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command()
    async def subscribe(self, inter: disnake.ApplicationCommandInteraction):
        """Schedules a job to be executed at PUBLISH_BIRTHDAYS_TIME from config.py."""
        """
        Args:
            inter: disnake.ApplicationCommandInteraction object
        """
        # Only add new subscription if channel is not subscribed yet
        if not subscriptions_controller.is_scheduled(inter.channel.id):
            await self.subscribe_channel(inter.channel)
        
            await inter.send(f"Subscription successful.")
        else:
            await inter.send(f"Already subscribed.")
    
    @classmethod
    async def subscribe_channel(cls, channel):
        """
        Schedules a job to be executed at PUBLISH_BIRTHDAYS_TIME from config.py.

        Args:
            channel_id: discord.py channel
        """
        subscriptions_controller.new_task(channel, cls.publish_daily_birthdays, PUBLISH_BIRTHDAYS_TIME)

    @commands.slash_command()
    async def unsubscribe(self, inter: disnake.ApplicationCommandInteraction):
        """Removes a job associated with the guild_id derived from the context."""
        """
        Args:
            inter: disnake.ApplicationCommandInteraction object
        """
        # Only try to remove subscription if channel is already subscribed
        if subscriptions_controller.is_scheduled(inter.channel.id):
            subscriptions_controller.remove_task(inter.channel)
            await inter.send(f"Successfully unsubscribed.")
        else:
            await inter.send(f"Not subscribed yet.")

    @subscriptions_controller.run_daily_at(time=PUBLISH_BIRTHDAYS_TIME)
    @staticmethod
    async def publish_daily_birthdays(guild_channel):
        """
        Fetches todays birthdays and publishes it to the given context.
        
        On subscription a task is created and scheduled to execute this coroutine with the correct context
        (e.g. to send the message to the channel, that the subscribe command was called in).

        Args:
            guild_channel: discord.py discord.abc.GuildChannel
        """
        birthdays = await bc.BirthdayCalendar().get_todays_birthdays(guild_channel.guild.id)
        output = bc.make_output_table(birthdays)
        await guild_channel.send(f"Heutige Geburtstage:\n```\n{output}\n```")


def setup(bot: commands.Bot):
    bot.add_cog(SubscriptionCommands(bot))