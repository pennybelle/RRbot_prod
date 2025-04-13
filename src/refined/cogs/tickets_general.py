"""
This cog allows us to create tickets.
"""

import discord, logging
from discord.ext import commands
from pathlib import Path

logger = logging.getLogger(__name__)
ticket_tracker = Path.cwd().joinpath(
    "src", "refined", "cogs", "core", "ticket_tracker.log"
)


class AddTicketButton(commands.Cog):
    """
    This is the slash command that sends our UI element.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def ticket(self, ctx, reason):
        """
        A simple command with a view.
        """
        # logger.info("%s used the %s command.", ctx.author.name, ctx.command)
        await ctx.respond(
            "Do you need help, or do you have a question for the Staff?",
            view=MakeATicket(self.bot.server_settings, reason),
            ephemeral=True,
        )


class MakeATicket(discord.ui.View):
    """
    A UI component that sends a button, which does other things.
    """

    def __init__(self, server_settings, reason, *, timeout=None):
        super().__init__(timeout=timeout)
        self.server_settings = server_settings
        self.reason = reason

    @discord.ui.button(label="Open a support Ticket", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        """
        The callback on the button, or... what happens on click.
        """
        await interaction.response.defer()
        button.label = "Ticket Created!"
        button.disabled = True
        await interaction.edit_original_response(view=self)

        ticket_channel = await interaction.guild.fetch_channel(
            self.server_settings.mod_channel["server_support"]
        )
        # staff = interaction.guild.get_role(self.server_settings.admin_roles["staff"])

        with open(ticket_tracker, "r+") as f:
            ticket_num = f.read()
            if ticket_num == "":
                ticket_num = 0
                f.seek(0)
                f.write("1")
            else:
                f.seek(0)
                f.write(str(int(ticket_num) + 1))

        ticket = await ticket_channel.create_thread(
            name=f"{int(ticket_num):04}",
            message=None,
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            invitable=False,
            reason=None,
        )

        # for person in interaction.guild.members:
        #     if staff in person.roles:
        #         await ticket.add_user(person)

        embed = discord.Embed(title="Reason for ticket:", description=self.reason)
        embed.set_footer(
            text="To speed up resolution times, please describe your issue in detail."
        )
        embed.set_thumbnail(url="https://i.imgur.com/CJdL1vw.png")

        moderator = self.server_settings.user_roles["admin"]["moderator"]
        await ticket.add_user(interaction.user)
        await ticket.send(
            f"**{interaction.user.mention}, we have received your ticket and "
            f"a <@&{moderator}> will be with you as soon as possible.**",
            embed=embed,
        )


def setup(bot):
    """
    Required
    """
    bot.add_cog(AddTicketButton(bot))
