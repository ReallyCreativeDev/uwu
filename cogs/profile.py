import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import pytz

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def create_profile_embed(self, member: discord.Member) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=False)

        created_at_timestamp = int(member.created_at.replace(tzinfo=pytz.UTC).timestamp())
        embed.add_field(
            name="Created Date",
            value=f"<t:{created_at_timestamp}:F> (<t:{created_at_timestamp}:R>)",
            inline=False
        )
        if isinstance(member, discord.Member) and member.joined_at:
            joined_at_timestamp = int(member.joined_at.replace(tzinfo=pytz.UTC).timestamp())
            embed.add_field(
                name="Join Date",
                value=f"<t:{joined_at_timestamp}:F> (<t:{joined_at_timestamp}:R>)",
                inline=False
            )
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=", ".join(roles) if roles else "None",
            inline=False
        )
        timenow = int(datetime.now(pytz.UTC).timestamp())
        embed.add_field(
            name="",
            value=f"-# {self.bot.user.name} • <t:{timenow}:D> <t:{timenow}:T>",
            inline=False
        )
        return embed
    @commands.command(name="profile")
    async def profile_text_command(self, ctx, member: discord.Member = None):
        """Text command variant. Usage: !profile [@member]"""
        member = member or ctx.author
        embed = self.create_profile_embed(member)
        await ctx.send(embed=embed)
    @app_commands.command(name="profile", description="Shows a user's profile details")
    @app_commands.describe(member="The member to view the profile of")
    async def profile_slash_command(self, interaction: discord.Interaction, member: discord.Member = None):
        """Slash command variant. Usage: /profile member:@user"""
        member = member or interaction.user
        embed = self.create_profile_embed(member)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
    print("Profile Cog Added")
