import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
import pytz

class Test(commands.Cog, name="Test"):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="test")
    async def test_text_command(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(f"Hello! <@{member.id}>")
    @app_commands.command(name="test", description="testing the shits :3")
    @app_commands.describe(member="a member?")
    async def test_slash_command(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"Hello! <@{member.id}>")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Test(bot))
    print("Added cog ""test""")