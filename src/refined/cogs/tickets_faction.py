"""
This cog allows us to create tickets.
"""

import discord, logging
from discord.ext import commands
from better_profanity import profanity

logger = logging.getLogger(__name__)


class AddFactionTicketButton(commands.Cog):
    """
    This is the slash command that sends our UI element.
    """

    def __init__(self, bot):
        self.bot = bot
        profanity.load_censor_words()

    @commands.slash_command()
    async def faction(self, ctx, name):
        """
        A simple command with a view.
        """
        # logger.info("%s used the %s command.", ctx.author.name, ctx.command)
        await ctx.respond(
            "Are you trying to start a faction?",
            view=MakeAFactionTicket(self.bot.server_settings, name),
            ephemeral=True,
        )


class MakeAFactionTicket(discord.ui.View):
    """
    A UI component that sends a button, which does other things.
    """

    def __init__(self, server_settings, name, *, timeout=None):
        super().__init__(timeout=timeout)
        self.server_settings = server_settings
        self.name = name

    @discord.ui.button(label="Open a faction ticket", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        """
        The callback on the button, or... what happens on click.
        """
        await interaction.response.defer()
        button.label = "Faction ticket created!"
        button.disabled = True
        await interaction.edit_original_response(view=self)

        faction = await interaction.guild.fetch_channel(
            self.server_settings.mod_channel["faction_ticket"]
        )
        # staff = interaction.guild.get_role(self.server_settings.admin_roles["staff"])

        ticket = await faction.create_thread(
            name=profanity.censor(self.name, "■").title(),
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            invitable=False,
            reason=None,
        )

        # depreciated
        # for person in interaction.guild.members:
        #     if staff in person.roles:
        #         await ticket.add_user(person)

        faction_embed = discord.Embed(
            title=self.name.title(),
            description="For all members in  your faction, please list their discord usernames "
            "(by tagging them in blue), their steam64 id or URL, and their character name.\n"
            "Please also list your base locations (XXXX/YYYY coordinates).",
        )
        faction_embed.set_footer(
            text="Please bare with us as we set up your faction role."
        )
        faction_embed.set_thumbnail(url="https://i.imgur.com/CJdL1vw.png")

        await ticket.add_user(interaction.user)
        await ticket.send(
            f"**{interaction.user.mention}, we have received your ticket.\n"
            f'A <@&{self.server_settings.admin_roles["faction_master"]}> will be with you as soon as possible.**',
            embed=faction_embed,
        )


def setup(bot):
    """
    Required
    """
    bot.add_cog(AddFactionTicketButton(bot))
