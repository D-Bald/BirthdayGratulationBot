import disnake
from disnake.ext import commands

import time

from config import LINK

class ManagementCommands(commands.Cog):
    """Handling interactions to ping or invite the bot and get server information."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """See if The Bot is Working"""
        ping = time.time()
        await inter.send("Pinging...")
        pingtime = time.time() - ping
        await inter.edit_original_message(content = ":ping_pong:  time is `%.01f seconds`" % pingtime)
        
    @commands.slash_command()
    async def botinvite(self, inter: disnake.ApplicationCommandInteraction, recipient: disnake.Member = None):
        """A Link To Invite This Bot To Your Server!"""
        await inter.send("Check Your Dm's :wink:")
        message = f"Add me to Your Server: {LINK}"
        if recipient:
            await recipient.send(message)
        else:
            await inter.author.send(message)

    @commands.slash_command()
    async def serverinfo(self, inter: disnake.ApplicationCommandInteraction):
        """Displays Info About The Server!"""

        guild = inter.guild
        roles = [x.name for x in guild.roles]
        role_length = len(roles)

        # Just in case there are too many roles...
        if role_length > 50:
            roles = roles[:50]
            roles.append('>>>> Displaying[50/%s] Roles'%len(roles))

        roles = ', '.join(roles)
        channels = len(guild.channels)
        time = str(guild.created_at); time = time.split(' '); time= time[0]

        join = disnake.Embed(description= '%s '%(str(guild)),title = 'Server Info', colour = 0xFFFF)
        # join.set_thumbnail(file = guild.icon)
        join.add_field(name = '__Owner__', value = str(guild.owner) + '\n' + str(guild.owner_id))
        join.add_field(name = '__ID__', value = str(guild.id))
        join.add_field(name = '__Member Count__', value = str(guild.member_count))
        join.add_field(name = '__Text/Voice Channels__', value = str(channels))
        join.add_field(name = '__Roles (%s)__'%str(role_length), value = roles)
        join.set_footer(text ='Created: %s'%time)

        await inter.send(embed = join)

def setup(bot: commands.Bot):
    bot.add_cog(ManagementCommands(bot))