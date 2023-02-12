import asyncio

import discord
from typing import Literal
from discord.ext import commands

from constants.snowflakes import GuildID, ChannelID, MessageID
from constants.teams import GTE_TEAMS, GT3_TEAMS


class RosterSelectMenu(discord.ui.Select):
    def __init__(self, guild: discord.Guild, category: Literal['GTE', 'GT3']):

        self.guild = guild
        self.category = GT3_TEAMS if category == 'GT3' else GTE_TEAMS
        teams = {guild.get_role(team.role_id).name: team for team in self.category}

        options = []
        for name, team in teams.items():
            emoji = team.supported_brands[0].value if category == 'GTE' else None
            options.append(discord.SelectOption(label=name, value=team.role_id, emoji=emoji))

        super().__init__(
            placeholder='Select a team...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        team_role = self.guild.get_role(int(self.values[0]))

        team_members = ['▸ ' + member.mention for member in team_role.members]
        team_members_str = '\n'.join(team_members)

        racer_count = str(len(team_role.members))
        racer_count += ' racers' if int(racer_count) != 1 else ' racer'

        message_title = '**__Pick a GTE team from the menu!__**'

        content = (
            f"{message_title}\n\n"
            f"**{team_role.mention}** | **{racer_count}**\n"
            f"{team_members_str}")

        await interaction.response.edit_message(content=content)


class RosterView(discord.ui.View):
    def __init__(self, guild: discord.Guild):

        self.guild = guild
        self.select_view = discord.ui.View(timeout=500)

        super().__init__(timeout=None)

    def attach_select_menu(self, category: Literal['GTE', 'GT3']) -> None:
        """Clears the old select menu if exists and attaches a new one to the view."""

        if self.select_view.children:
            self.select_view.clear_items()
        self.select_view.add_item(RosterSelectMenu(self.guild, category))

    @discord.ui.button(label='GTE Roster', style=discord.ButtonStyle.primary, custom_id='gte_roster_bt')
    async def gte_roster(self, interaction: discord.Interaction, _button: discord.ui.Button):

        self.attach_select_menu(category='GTE')
        await interaction.response.send_message(
            '**__Pick a GTE team from the menu!__**', ephemeral=True, view=self.select_view)

    @discord.ui.button(label='GT3 Roster', style=discord.ButtonStyle.primary, custom_id='gt3_roster_bt')
    async def gt3_roster(self, interaction: discord.Interaction, _button: discord.ui.Button):

        self.attach_select_menu(category='GT3')
        await interaction.response.send_message(
            '**__Pick a GT3 team from the menu!__**', ephemeral=True, view=self.select_view)


class RosterEmbed(discord.Embed):
    def __init__(self, title: str, content: str, color: discord.Color):
        super().__init__(title=title, description=content, color=color)


class RosterHandler:
    def __init__(self, guild: discord.Guild, embed_color: discord.Color):
        self.guild = guild
        self.embed_color = embed_color

    def get_roster_content(self) -> list[str, str]:
        """Returns a list of two strings containing the roster contents."""

        decorated_gt3_teams: list[str] = []
        decorated_gte_teams: list[str] = []
        roster_contents: list[str, str] = []

        for category, teams in enumerate([GT3_TEAMS, GTE_TEAMS], 1):
            for team in teams:
                team_role = self.guild.get_role(team.role_id)

                if team_role is None:
                    continue

                supported_brands = ' '.join([brand.value for brand in team.supported_brands])
                racers_count = str(len(team_role.members))
                racers_count += ' racers' if int(racers_count) != 1 else ' racer'

                decorated_team = f'{team_role.mention}\n{supported_brands} — **{racers_count}**\n'
                decorated_gt3_teams.append(decorated_team) if category == 1 \
                    else decorated_gte_teams.append(decorated_team)

        for decorated_teams in [decorated_gt3_teams, decorated_gte_teams]:
            roster_contents.append(''.join(decorated_teams))

        return roster_contents

    def make_roster_embeds(
            self, roster_contents: list[str, str]) -> list[RosterEmbed, RosterEmbed]:
        """Generates the roster embeds and returns them as a tuple."""

        embed1 = RosterEmbed(
            title='Supported GT3 Teams',
            content=roster_contents[0],
            color=self.embed_color)
        embed2 = RosterEmbed(
            title='Supported GTE Teams',
            content=roster_contents[1],
            color=self.embed_color)

        return embed1, embed2

    def get_count(self) -> dict[str, int]:
        """Returns a dict containing the number of teams and racers."""

        all_teams = [self.guild.get_role(team.role_id) for team in GTE_TEAMS + GT3_TEAMS]
        all_teams = [team for team in all_teams if team is not None]

        all_racers = []
        for team in all_teams:
            all_racers.extend(team.members)
        unique_racers = set(all_racers)

        return {'teams': len(all_teams), 'racers': len(unique_racers)}


class Roster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.loop.create_task(self.load_persistent_views())
        self.bot.loop.create_task(self.update_roster_on_ready())

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def roster(self, ctx: commands.Context):
        guild = self.bot.get_guild(GuildID.MAIN.value)

        # Generating embeds for the roster
        roster = RosterHandler(guild=guild, embed_color=self.bot.embed_color)
        roster_contents = roster.get_roster_content()
        embed1, embed2 = roster.make_roster_embeds(roster_contents)

        # Getting the total number of teams and racers
        count = roster.get_count()

        await ctx.send(
            content='**__Olzhasstik Motorsports Teams__**\n'
                    f'Teams: {count["teams"]}, Drivers: {count["racers"]}',
            embeds=[embed1, embed2], view=RosterView(guild=guild))

    # Auto-Updating the Roster
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.guild.id != GuildID.MAIN.value:
            return

        roles_added = set(after.roles) - set(before.roles)
        roles_removed = set(before.roles) - set(after.roles)
        all_modified_roles = roles_added | roles_removed

        if not all_modified_roles:
            return

        gt3_teams = [team.role_id for team in GT3_TEAMS]
        gte_teams = [team.role_id for team in GTE_TEAMS]
        all_teams = gt3_teams + gte_teams

        for role in all_modified_roles:
            if role.id in all_teams:

                # Generating embeds for the roster
                roster = RosterHandler(guild=after.guild, embed_color=self.bot.embed_color)
                roster_contents = roster.get_roster_content()
                embed1, embed2 = roster.make_roster_embeds(roster_contents)

                # Getting the total number of teams and racers
                count = roster.get_count()

                roster_channel = self.bot.get_channel(ChannelID.ROSTER.value)
                roster_message = roster_channel.get_partial_message(MessageID.ROSTER.value)

                await roster_message.edit(
                    content='**__Olzhasstik Motorsports Teams__**\n'
                            f'Teams: {count["teams"]}, Drivers: {count["racers"]}',
                    embeds=[embed1, embed2])

                break

    # Load Persistent Views
    async def load_persistent_views(self):
        await self.bot.wait_until_ready()

        # Sleeping to let Bot.main_guild get populated
        await asyncio.sleep(3)

        self.bot.add_view(RosterView(guild=self.bot.main_guild), message_id=MessageID.ROSTER.value)

    # Updating the Roster Message on Bot Startup
    async def update_roster_on_ready(self):
        await self.bot.wait_until_ready()

        # Sleeping to let Bot.main_guild get populated
        await asyncio.sleep(3)

        # Generating embeds for the roster
        roster = RosterHandler(guild=self.bot.main_guild, embed_color=self.bot.embed_color)
        roster_contents = roster.get_roster_content()
        embed1, embed2 = roster.make_roster_embeds(roster_contents)

        # Getting the total number of teams and racers
        count = roster.get_count()

        roster_channel = self.bot.get_channel(ChannelID.ROSTER.value)
        roster_message = roster_channel.get_partial_message(MessageID.ROSTER.value)

        await roster_message.edit(
            content='**__Olzhasstik Motorsports Teams__**\n'
                    f'Teams: {count["teams"]}, Drivers: {count["racers"]}',
            embeds=[embed1, embed2])


async def setup(bot: commands.Bot):
    await bot.add_cog(Roster(bot), guilds=[discord.Object(GuildID.MAIN.value)])
