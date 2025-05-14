import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import traceback # Import traceback for better error reporting

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
        name="sync",
        description="Synchonizes the slash commands.",
    )
    @app_commands.describe(scope="The scope of the sync. Can be `global` or `guild`")
    @commands.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        """
        Synchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global` or `guild`.
        """
        scope = scope.lower() # Convert scope to lowercase for easier comparison
        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            if context.guild: # Make sure it's used in a guild
                context.bot.tree.copy_global_to(guild=context.guild)
                await context.bot.tree.sync(guild=context.guild)
                embed = discord.Embed(
                    description=f"Slash commands have been synchronized in this guild (`{context.guild.name}`).",
                    color=0xBEBEFE,
                )
                await context.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="Guild scope sync can only be used inside a server.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    @commands.command(
        name="unsync",
        description="Unsynchonizes the slash commands.",
    )
    @app_commands.describe(
        scope="The scope of the sync. Can be `global`, `current_guild` or `guild`"
    )
    @commands.is_owner()
    async def unsync(self, context: Context, scope: str) -> None:
        """
        Unsynchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global`, `current_guild` or `guild`.
        """
        scope = scope.lower() # Convert scope to lowercase
        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally unsynchronized.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
             if context.guild: # Make sure it's used in a guild
                context.bot.tree.clear_commands(guild=context.guild)
                await context.bot.tree.sync(guild=context.guild)
                embed = discord.Embed(
                    description=f"Slash commands have been unsynchronized in this guild (`{context.guild.name}`).",
                    color=0xBEBEFE,
                )
                await context.send(embed=embed)
             else:
                embed = discord.Embed(
                    description="Guild scope unsync can only be used inside a server.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
             return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    # --- Load/Unload/Reload Section ---

    @commands.hybrid_command(
        name="load",
        description="Load a cog",
    )
    @app_commands.describe(cog="The name of the cog to load (e.g., 'general')")
    @commands.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        """
        The bot will load the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}") # Assuming cogs are in a 'cogs' folder
            embed = discord.Embed(
                description=f"✅ Successfully loaded the `{cog}` cog.", color=0x00FF00 # Green for success
            )
            await context.send(embed=embed)
        except commands.ExtensionAlreadyLoaded:
             embed = discord.Embed(
                description=f"⚠️ The `{cog}` cog is already loaded.", color=0xFFFF00 # Yellow for warning
            )
             await context.send(embed=embed)
        except commands.ExtensionNotFound:
             embed = discord.Embed(
                description=f"❌ Could not find the `{cog}` cog. Make sure the file `cogs/{cog}.py` exists.", color=0xE02B2B
            )
             await context.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title=f"❌ Error loading `{cog}` cog",
                description=f"```py\n{traceback.format_exc()}\n```", # Show traceback for debugging
                color=0xE02B2B
            )
            await context.send(embed=embed)


    @commands.hybrid_command(
        name="unload",
        description="Unloads a cog.",
    )
    @app_commands.describe(cog="The name of the cog to unload (e.g., 'general')")
    @commands.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        """
        The bot will unload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        if f"cogs.{cog}" == self.extension_name: # Prevent unloading the owner cog itself
             embed = discord.Embed(
                description="❌ You cannot unload the `owner` cog.", color=0xE02B2B
            )
             await context.send(embed=embed)
             return
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                description=f"✅ Successfully unloaded the `{cog}` cog.", color=0x00FF00
            )
            await context.send(embed=embed)
        except commands.ExtensionNotLoaded:
            embed = discord.Embed(
                description=f"⚠️ The `{cog}` cog is not loaded.", color=0xFFFF00
            )
            await context.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title=f"❌ Error unloading `{cog}` cog",
                description=f"```py\n{traceback.format_exc()}\n```",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="reload",
        description="Reloads a specific cog.",
        aliases=["r"] # <<< Added alias 'r' here
    )
    @app_commands.describe(cog="The name of the cog to reload (e.g., 'general')")
    @commands.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        """
        The bot will reload the given cog. Can be invoked with !r <cog>.

        :param context: The hybrid command context.
        :param cog: The name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                description=f"✅ Successfully reloaded the `{cog}` cog.", color=0x00FF00
            )
            await context.send(embed=embed)
        except commands.ExtensionNotLoaded:
             embed = discord.Embed(
                description=f"⚠️ The `{cog}` cog is not loaded. Use `load {cog}` first.", color=0xFFFF00
            )
             await context.send(embed=embed)
        except commands.ExtensionNotFound:
             embed = discord.Embed(
                description=f"❌ Could not find the `{cog}` cog. Make sure the file `cogs/{cog}.py` exists.", color=0xE02B2B
            )
             await context.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title=f"❌ Error reloading `{cog}` cog",
                description=f"```py\n{traceback.format_exc()}\n```",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    # --- New command to reload all cogs ---
    @commands.command(
        name="reloadall",
        description="Reloads all loaded cogs.",
        aliases=["rall"] # Added alias 'rall'
    )
    @commands.is_owner()
    async def reloadall(self, context: Context) -> None:
        """
        Reloads all currently loaded cogs except the owner cog.
        Invoked with !reloadall or !rall.
        """
        reloaded_cogs = []
        failed_cogs = []
        # Get a list of extensions to reload (iterate over a copy)
        # Exclude the owner cog itself to prevent locking yourself out on error
        extensions_to_reload = [
            ext for ext in list(self.bot.extensions.keys())
            if ext != self.extension_name # self.extension_name gets the name of the current cog file
        ]

        if not extensions_to_reload:
            embed = discord.Embed(description="⚠️ No cogs available to reload (besides Owner).", color=0xFFFF00)
            await context.send(embed=embed)
            return

        await context.send(f"🔄 Reloading {len(extensions_to_reload)} cog(s)...")

        for extension in extensions_to_reload:
            try:
                await self.bot.reload_extension(extension)
                reloaded_cogs.append(f"`{extension.split('.')[-1]}`") # Show short name
            except Exception as e:
                print(f"Failed to reload extension {extension}: {e}") # Log error to console
                traceback.print_exc() # Print full traceback to console
                failed_cogs.append(f"`{extension.split('.')[-1]}`") # Show short name

        # Send summary report
        embed = discord.Embed(title="Cog Reload Report", color=0xBEBEFE)
        if reloaded_cogs:
            embed.add_field(name="✅ Successfully Reloaded", value=", ".join(reloaded_cogs) or "None", inline=False)
        if failed_cogs:
            embed.add_field(name="❌ Failed to Reload", value=", ".join(failed_cogs) or "None", inline=False)
            embed.color = 0xE02B2B # Change color to red if any failed
        elif not reloaded_cogs: # If nothing was reloaded (and nothing failed, unlikely with the check above)
            embed.description = "No cogs were reloaded."

        await context.send(embed=embed)

    # --- Other Owner Commands ---

    @commands.hybrid_command(
        name="shutdown",
        description="Make the bot shutdown.",
    )
    @commands.is_owner()
    async def shutdown(self, context: Context) -> None:
        """
        Shuts down the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(description="Shutting down. Bye! :wave:", color=0xBEBEFE)
        await context.send(embed=embed)
        await self.bot.close()
        
    @commands.hybrid_command(
        name="say",
        description="The bot will say anything you want.",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @commands.is_owner()
    async def say(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        # Prevent potential abuse if context is somehow invoked without interaction
        if context.interaction:
            await context.interaction.response.defer(ephemeral=True) # Acknowledge interaction privately
            await context.channel.send(message) # Send message publicly in the channel
            await context.followup.send("Message sent.", ephemeral=True) # Confirm privately to owner
        else:
            # For prefix command, just send
            await context.channel.send(message)
            try: # Attempt to delete the invoking command message for prefix commands
                await context.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass # Ignore if delete fails


    @commands.hybrid_command(
        name="embed",
        description="The bot will say anything you want, but within embeds.",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @commands.is_owner()
    async def embed(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want, but using embeds.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        embed = discord.Embed(description=message, color=0xBEBEFE)
         # Prevent potential abuse if context is somehow invoked without interaction
        if context.interaction:
            await context.interaction.response.defer(ephemeral=True)
            await context.channel.send(embed=embed)
            await context.followup.send("Embed sent.", ephemeral=True)
        else:
            # For prefix command, just send
            await context.channel.send(embed=embed)
            try: # Attempt to delete the invoking command message for prefix commands
                await context.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass


async def setup(bot) -> None:
    # Need to get the name of the file for the owner cog exclusion in reloadall
    # This assumes your cog file is named 'owner.py' inside the 'cogs' folder
    # If it's named differently, adjust accordingly or pass it during init
    import os
    cog_name = f"cogs.{os.path.splitext(os.path.basename(__file__))[0]}"
    owner_cog = Owner(bot)
    owner_cog.extension_name = cog_name # Store the extension name in the cog instance
    await bot.add_cog(owner_cog)