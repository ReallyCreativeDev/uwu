import discord
from discord.ext import commands
from discord.ext.commands import Context
import aiohttp
import io
import random
import asyncio

class TopConfirmationView(discord.ui.View):
    def __init__(self, initiator: discord.Member, target: discord.Member, timeout=180.0):
        super().__init__(timeout=timeout)
        self.initiator = initiator
        self.target = target
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.target.id:
            return True
        else:
            await interaction.response.send_message("Sorry i dont whant to top you >_<", ephemeral=True)
            return False

    @discord.ui.button(label="Accept Top", style=discord.ButtonStyle.danger, custom_id="accept_top_button")
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        final_message = f"**{self.target.mention} accepted the top from {self.initiator.mention}!**"
        await interaction.response.edit_message(content=final_message, view=self)
        self.stop()

    async def on_timeout(self) -> None:
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(content=f"Looks like {self.target.mention} didn't respond in time... the top offer expired.", view=self)
            except discord.NotFound:
                pass
            except discord.Forbidden:
                 pass
        self.stop()

class FuckConfirmationView(discord.ui.View):
    def __init__(self, initiator: discord.Member, target: discord.Member, timeout=180.0):
        super().__init__(timeout=timeout)
        self.initiator = initiator
        self.target = target
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.target.id:
            return True
        else:
            await interaction.response.send_message("Sorry i dont whant to fuck you >_<", ephemeral=True)
            return False

    @discord.ui.button(label="Accept To fuck them!", style=discord.ButtonStyle.danger, custom_id="accept_fuck_button")
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        final_message = f"**{self.target.mention} accepted to fuck you {self.initiator.mention}! (no ai yet sorry i will add soon)**"
        await interaction.response.edit_message(content=final_message, view=self)
        self.stop()

    async def on_timeout(self) -> None:
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(content=f"Looks like {self.target.mention} didn't respond in time... To fuck so mean >~<.", view=self)
            except discord.NotFound:
                pass
            except discord.Forbidden:
                 pass
        self.stop()

class UwU(commands.Cog, name="uwu"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="top",
        description="Offer to top another user.",
    )
    async def top(self, context: Context, target: discord.Member) -> None:
        initiator = context.author

        if target == self.bot.user:
            await context.send("You can't top me, silly!", ephemeral=True)
            return
        if target == initiator:
            await context.send("You can't top yourself!", ephemeral=True)
            return

        view = TopConfirmationView(initiator=initiator, target=target)
        initial_message_text = f"Hey Cutie {target.mention}! {initiator.mention} wants to top you... 😏 Will you let them?"
        sent_message = await context.send(initial_message_text, view=view)
        view.message = sent_message

    @commands.hybrid_command(
        name="fuck",
        description="Offer to fuck another user.",
    )
    async def fuck_command(self, context: Context, target: discord.Member) -> None:
        initiator = context.author

        if target == self.bot.user:
            await context.send("You can't fuck me, silly!", ephemeral=True)
            return
        if target == initiator:
            await context.send("You can't fuck yourself!", ephemeral=True)
            return

        view = FuckConfirmationView(initiator=initiator, target=target)
        initial_message_text = f"Hey {target.mention}! {initiator.mention} wants to Fuck you... 😏 Will you let them?"
        sent_message = await context.send(initial_message_text, view=view)
        view.message = sent_message

    @commands.hybrid_command(
        name="cat",
        description="Fetches a random cat image from cataas.com.",
    )
    async def cat(self, context: Context) -> None:
        image_url = "https://cataas.com/cat"
        params = {'rand': random.randint(1, 100000)}
        placeholder_message = await context.send("Fetching a cute kitty... 🐾")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'image' in content_type:
                            image_bytes = await response.read()
                            extension = content_type.split('/')[-1].split(';')[0]
                            if not extension or len(extension) > 5 or not extension.isalnum():
                                extension = 'jpg'
                            filename = f"random_cat.{extension}"
                            image_file = discord.File(fp=io.BytesIO(image_bytes), filename=filename)
                            embed = discord.Embed(title="Meow!", color=discord.Color.random())
                            embed.set_image(url=f"attachment://{filename}")
                            await placeholder_message.edit(content=None, embed=embed, attachments=[image_file])
                        else:
                            await placeholder_message.edit(content=f"The URL didn't provide a valid image. Content-Type: `{content_type}`", embed=None, attachments=[])
                    else:
                        await placeholder_message.edit(content=f"Error fetching cat image. Status code: {response.status}", embed=None, attachments=[])
        except aiohttp.ClientError as e:
            await placeholder_message.edit(content=f"Could not connect to the cat image source: `{e}`", embed=None, attachments=[])
        except asyncio.TimeoutError:
            await placeholder_message.edit(content=f"The request to the cat image source timed out.", embed=None, attachments=[])
        except Exception as e:
            print(f"Error in cat command: {e}")
            await placeholder_message.edit(content="An unexpected error occurred while fetching a cat. Please try again later.", embed=None, attachments=[])

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UwU(bot))