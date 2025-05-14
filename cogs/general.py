import platform
import random
import time # Import the time module
import datetime # Import the datetime module

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


# --- Assume self.bot.start_time is set when the bot starts ---
# Example in your main bot file:
# bot = commands.Bot(...)
# bot.start_time = datetime.datetime.utcnow()

class FeedbackForm(discord.ui.Modal, title="Feeedback"):
    feedback = discord.ui.TextInput(
        label="What do you think about this bot?",
        style=discord.TextStyle.long,
        placeholder="Type your answer here...",
        required=True,
        max_length=256,
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.answer = str(self.feedback)
        self.stop()


class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot
        # --- Add bot start time attribute FOR UPTIME CALCULATION ---
        # It's better to set this in your main bot setup file
        # For example: bot.start_time = datetime.datetime.utcnow()
        # If it's not set elsewhere, uncomment and set it here,
        # but it will reset every time the cog reloads.
        # self.bot.start_time = datetime.datetime.utcnow()
        # ------
        self.context_menu_user = app_commands.ContextMenu(
            name="Grab ID", callback=self.grab_id
        )
        self.bot.tree.add_command(self.context_menu_user)
        self.context_menu_message = app_commands.ContextMenu(
            name="Remove spoilers", callback=self.remove_spoilers
        )
        self.bot.tree.add_command(self.context_menu_message)

    # Message context menu command
    async def remove_spoilers(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """
        Removes the spoilers from the message. This command requires the MESSAGE_CONTENT intent to work properly.

        :param interaction: The application command interaction.
        :param message: The message that is being interacted with.
        """
        spoiler_attachment = None
        for attachment in message.attachments:
            if attachment.is_spoiler():
                spoiler_attachment = attachment
                break
        embed = discord.Embed(
            title="Message without spoilers",
            description=message.content.replace("||", ""),
            color=0xBEBEFE,
        )
        if spoiler_attachment is not None:
            # Make sure to use the correct attachment variable if found
            embed.set_image(url=spoiler_attachment.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # User context menu command
    async def grab_id(
        self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        """
        Grabs the ID of the user.

        :param interaction: The application command interaction.
        :param user: The user that is being interacted with.
        """
        embed = discord.Embed(
            description=f"The ID of {user.mention} is `{user.id}`.",
            color=0xBEBEFE,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    async def help(self, context: Context) -> None:
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0xBEBEFE
        )
        # Dynamically adjust columns based on number of cogs? Maybe too complex now.
        embed.set_thumbnail(url=self.bot.user.display_avatar.url) # Add bot avatar
        embed.set_footer(text=f"Requested by {context.author.display_name}", icon_url=context.author.display_avatar.url)

        for i in sorted(self.bot.cogs): # Sort cogs alphabetically
            # Skip owner cog if user is not owner
            is_owner = await self.bot.is_owner(context.author)
            if i.lower() == "owner" and not is_owner:
                continue

            cog = self.bot.get_cog(i.lower())
            # Ensure cog is not None and get_commands exists
            if cog is None or not hasattr(cog, 'get_commands'):
                 continue

            commands_list = cog.get_commands()
            # Filter out hidden commands or subcommands if necessary
            commands_list = [cmd for cmd in commands_list if not cmd.hidden]

            if not commands_list: # Skip cog if it has no visible commands
                 continue

            data = []
            for command in sorted(commands_list, key=lambda cmd: cmd.name): # Sort commands alphabetically
                # Get the first line of the description
                description = command.description.partition('\n')[0] if command.description else "No description"
                # Show command signature if possible (can get complex with groups/hybrid)
                # For simplicity, just name and short desc for now
                data.append(f"`{command.name}` - {description}")

            if data:
                 help_text = "\n".join(data)
                 embed.add_field(
                     name=f"{i.capitalize()} Commands", # Add "Commands" suffix
                     value=help_text,
                     inline=False # Keep command groups separate
                 )

        await context.send(embed=embed)


    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    async def botinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            #description="Im just a sillt little femboy >_<", # You can keep or change this
            color=0xBEBEFE,
            timestamp=datetime.datetime.utcnow() # Add timestamp
        )
        # Use the bot's actual avatar and name
        embed.set_author(name=f"{self.bot.user.name} Information", icon_url=self.bot.user.display_avatar.url)

        # Find the application owner (might take a moment)
        try:
            app_info = await self.bot.application_info()
            owner = app_info.owner
        except Exception:
            owner = "Could not fetch owner" # Fallback

        embed.add_field(name="My silly little owner", value=f"{owner}", inline=True) # Use actual owner, maybe add a cute icon like <:dev:123...> (replace id)
        embed.add_field(name="My Python Version", value=f"{platform.python_version()}", inline=True) # Add icon
        embed.add_field(name="My discord.py Version", value=f"{discord.__version__}", inline=True) # Add library version and icon

        # Calculate uptime if start_time is available
        if hasattr(self.bot, 'start_time') and self.bot.start_time:
             delta_uptime = datetime.datetime.utcnow() - self.bot.start_time
             hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
             minutes, seconds = divmod(remainder, 60)
             days, hours = divmod(hours, 24)
             uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
             uptime_str = "N/A" # Fallback if start_time isn't set
        embed.add_field(name="Uptime", value=uptime_str, inline=True) # Add uptime and icon

        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}", inline=True) # Server count
        embed.add_field(name="Users", value=f"{len(self.bot.users)}", inline=True) # User count (cached users)

        # Determine prefix (less relevant with primarily slash commands)
        legacy_prefix = getattr(self.bot, 'bot_prefix', 'None') # Safely get prefix if exists
        if legacy_prefix:
            prefix_str = f"`{legacy_prefix}` (Thats it for now sorry)"

        embed.add_field(
            name="Prefix",
            value=prefix_str,
            inline=False, # Span full width
        )
        # Add bot ID
        embed.add_field(name="Bot ID", value=f"`{self.bot.user.id}`", inline=False)


        # Set the footer with requester info
        embed.set_footer(text=f"Requested by {context.author.display_name}", icon_url=context.author.display_avatar.url)
        await context.send(embed=embed)


    @commands.hybrid_command(
        name="ping",
        description="Check the bot's responsiveness and latency.", # Improved description
    )
    async def ping(self, context: Context) -> None:
        """
        Measures the bot's latency to Discord's various endpoints.

        :param context: The hybrid command context.
        """
        # 1. Initial response (let user know we're working)
        start_time = time.monotonic()
        initial_embed = discord.Embed(
            title="🏓 Pinging...",
            description="Measuring latencies...",
            color=0xBEBEFE # You can use a "working" color like yellow or grey
        )
        message = await context.send(embed=initial_embed)
        end_time = time.monotonic()

        # 2. Calculate latencies
        websocket_latency = self.bot.latency * 1000  # Latency between bot and Discord's websocket servers (in ms)
        api_latency = (end_time - start_time) * 1000 # Round-trip time for the message send/ack (in ms)

        # 3. Calculate Uptime (if start_time attribute exists)
        uptime_str = "N/A"
        if hasattr(self.bot, 'start_time') and self.bot.start_time:
             delta_uptime = datetime.datetime.utcnow() - self.bot.start_time
             hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
             minutes, seconds = divmod(remainder, 60)
             days, hours = divmod(hours, 24)
             uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        # 4. Create the final, detailed embed
        final_embed = discord.Embed(
            title="🏓 Pong!",
            description="Here are the current latency details:",
            color=0xBEBEFE # Final "good" color
        )
        final_embed.set_thumbnail(url=self.bot.user.display_avatar.url) # Optional: Add bot's avatar

        # Add latency fields with icons (replace IDs with actual emoji IDs if using custom ones)
        final_embed.add_field(
            name="📶 Websocket Latency",
            value=f"`{websocket_latency:.2f} ms`\n*(IM FAST)*", # Format to 2 decimal places
            inline=True
        )
        final_embed.add_field(
            name="<:api:1234567890> API Latency", # Replace with a relevant emoji/ID
            value=f"`{api_latency:.2f} ms`\n*(Round-Trip >_<)*", # Format to 2 decimal places
            inline=True
        )
        # Add Uptime field
        final_embed.add_field(
            name="⏱️ Bot Uptime",
            value=f"`{uptime_str}`",
            inline=False # Make uptime span the full width or set inline=True if space allows
        )

        # Add footer with requester info
        final_embed.set_footer(text=f"Requested by {context.author.display_name}", icon_url=context.author.display_avatar.url)

        # 5. Edit the original message with the final embed
        await message.edit(embed=final_embed)


    @commands.hybrid_command(
        name="8ball",
        description="Ask the mystical 8-ball a question.", # Slightly more thematic description
    )
    @app_commands.describe(question="The question you dare to ask fate.") # Thematic description
    async def eight_ball(self, context: Context, *, question: str) -> None:
        """
        Ask any question to the bot.

        :param context: The hybrid command context.
        :param question: The question that should be asked by the user.
        """
        answers = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        embed = discord.Embed(
            title="🎱 The Magic 8-Ball Responds...", # Thematic title
            #description=f"**Your Question:**\n> {discord.utils.escape_markdown(question)}\n\n" # Moved question to field or footer
                          #f"**My Answer:**\n> {random.choice(answers)}",
            color=random.randint(0x000000, 0xFFFFFF), # Random color for fun
            timestamp=datetime.datetime.utcnow()
        )
        # You can use fields for better separation:
        embed.add_field(name="❓ Your Question", value=f"> {discord.utils.escape_markdown(question)}", inline=False)
        embed.add_field(name="💬 My Answer", value=f"> {random.choice(answers)}", inline=False)

        # Or keep the question in the footer for a cleaner look:
        # embed.description=f"> {random.choice(answers)}"
        # embed.set_footer(text=f"Question: {question[:100]}{'...' if len(question) > 100 else ''}") # Truncate long questions

        # Using fields example here:
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Magic_8_ball_icon.svg/1200px-Magic_8_ball_icon.svg.png") # Add an 8-ball image
        embed.set_footer(text=f"Asked by {context.author.display_name}", icon_url=context.author.display_avatar.url) # Add requester

        await context.send(embed=embed)


    @app_commands.command(
        name="feedback", description="Submit feedback about the bot to the owner" # Clearer description
    )
    async def feedback(self, interaction: discord.Interaction) -> None:
        """
        Submit feedback for the owners of the bot.

        :param interaction: The application command interaction.
        """
        feedback_form = FeedbackForm()
        # Send the modal to the user
        await interaction.response.send_modal(feedback_form)

        # Wait for the modal to be submitted
        modal_timed_out = await feedback_form.wait() # Returns True if timed out

        # Ensure we got a response back (check interaction isn't None and not timed out)
        if modal_timed_out or not feedback_form.interaction:
             # Handle timeout case (optional) - You could send a follow-up message
             # await interaction.followup.send("Feedback submission timed out.", ephemeral=True)
             return # Stop processing if timed out

        # Use the interaction object stored in the form (feedback_form.interaction)
        interaction = feedback_form.interaction # Retrieve the interaction from the form submit

        # Respond ephemerally to the user who submitted
        await interaction.response.send_message(
            embed=discord.Embed(
                title="💌 Feedback Sent!", # More informative title
                description="Thank you for your feedback! The owner has been notified. UwU", # Adjusted message
                color=0xBEBEFE,
            ),
            ephemeral=True # Keep confirmation private
        )

        # Send the feedback to the application owner(s)
        try:
            app_info = await self.bot.application_info()
            if app_info.team: # Check if there's a team
                owners = app_info.team.members
            else:
                 owners = [app_info.owner] # Fallback to single owner

            feedback_embed = discord.Embed(
                title="📝 New Feedback Received!",
                description=f"**Submitted by:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                            f"**In Guild:** {interaction.guild.name if interaction.guild else 'Direct Message'} (`{interaction.guild_id}`)\n"
                            f"**Channel:** {interaction.channel.mention if interaction.channel else 'Direct Message'} (`{interaction.channel_id}`)\n"
                            f"```\n{feedback_form.answer}\n```", # Use the stored answer
                color=0xFFFF00, # Yellow for "notification"
                timestamp=interaction.created_at # Use interaction timestamp
            )
            feedback_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)


            for owner in owners:
                if owner: # Make sure owner object exists
                    try:
                         await owner.send(embed=feedback_embed)
                    except discord.Forbidden:
                         print(f"Could not send feedback DM to owner {owner.id} - They might have DMs disabled.")
                    except Exception as e:
                         print(f"Error sending feedback DM to {owner.id}: {e}")

        except Exception as e:
            print(f"Failed to send feedback to owner(s): {e}")
            # Optionally inform the user there was an issue sending to owner
            await interaction.followup.send("There was an error notifying the bot owner, but your feedback might have been recorded internally.", ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(General(bot))