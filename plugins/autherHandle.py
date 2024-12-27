from pyrogram import Client, filters
from pyrogram.types import Message
from globals import Authers  # Import the global Authers list
from config import Config  # Import the OWNER ID

# Middleware to check if a user is authorized
def is_auth(user_id: int) -> bool:
    """Check if a user is in the authorized list or is the owner."""
    return user_id == Config.OWNER or user_id in Authers

@Client.on_message(filters.command("addAuth") & filters.private)
async def add_auth(client: Client, message: Message):
    """Command to add a user to the authorized list."""
    try:
        # Only the owner can add users to the authorized list
        if message.from_user.id != Config.OWNER:
            await message.reply_text("❌ Only the bot owner can use this command.")
            return

        # Check if a user ID is provided
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: `/addAuth <user_id>`")
            return

        # Extract the user ID
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return

        # Add the user to the authorized list if not already added
        if user_id in Authers:
            await message.reply_text(f"✅ User `{user_id}` is already authorized.")
        else:
            Authers.append(user_id)
            await message.reply_text(f"✅ User `{user_id}` has been added to the authorized list.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("banAuth") & filters.private)
async def ban_auth(client: Client, message: Message):
    """Command to remove a user from the authorized list."""
    try:
        # Only the owner can remove users from the authorized list
        if message.from_user.id != Config.OWNER:
            await message.reply_text("❌ Only the bot owner can use this command.")
            return

        # Check if a user ID is provided
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: `/banAuth <user_id>`")
            return

        # Extract the user ID
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return

        # Remove the user from the authorized list if present
        if user_id in Authers:
            Authers.remove(user_id)
            await message.reply_text(f"✅ User `{user_id}` has been removed from the authorized list.")
        else:
            await message.reply_text(f"❌ User `{user_id}` is not in the authorized list.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("listAuth") & filters.private)
async def list_auth(client: Client, message: Message):
    """Command to list all authorized users."""
    try:
        # Check if the user is authorized
        if message.from_user.id != Config.OWNER:
            await message.reply_text("❌ You are not authorized to use this command.")
            return

        # Display the list of authorized users
        if Authers:
            auth_list = "\n".join([f"`{user_id}`" for user_id in Authers])
            await message.reply_text(f"✅ **Authorized Users:**\n{auth_list}")
        else:
            await message.reply_text("❌ No authorized users found.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
