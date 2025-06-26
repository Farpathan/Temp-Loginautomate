import logging
import datetime
import pytz
from telegram import Update, ChatMember, ChatMemberUpdated, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
)
import user_manager

# --- Configuration ---
# Your bot's secret credentials from the file you uploaded
BOT_TOKEN = "7783964471:AAHIkKcVIRGfqxDDBjLRwtXnlcni8Kd2-yk" 
GROUP_CHAT_ID = "-1002793378249" 
GROUP_INVITE_LINK = "https://t.me/+v01yaOhRCHFkNzEx" 

# --- Setup ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Define states for all conversations ---
(
    GETTING_USERNAME, GETTING_PASSWORD,
    GETTING_LEAVE_DATE,
    GETTING_CANCEL_DATE
) = range(4)


# --- Helper Function ---
def parse_date(text: str) -> str | None:
    """Parses text like 'today', 'tomorrow', 'yesterday', or 'YYYY-MM-DD'."""
    today = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()
    text_lower = text.lower()
    
    if 'today' in text_lower: return today.strftime('%Y-%m-%d')
    if 'tomorrow' in text_lower: return (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    if 'yesterday' in text_lower: return (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        return datetime.datetime.strptime(text, '%Y-%m-%d').date().strftime('%Y-%m-%d')
    except ValueError:
        return None

# --- Invalid Input Handler ---
async def invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles any command or text that is not expected in the current conversation state."""
    await update.message.reply_text(
        "Invalid input. You are in the middle of another operation.\n\n"
        "Please complete the current task or use /cancel to start over."
    )

# --- NEW: /start command now ONLY displays the menu ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and displays a helpful menu."""
    user = update.message.from_user
    welcome_message = (
        f"Hi {user.first_name}!\n\n"
        "I'm the Beehive Automator bot. Here's a list of available commands:\n\n"
        "*/setupaccount* - Set up your Beehive credentials for the first time.\n"
        "*/leave* - Mark yourself as on leave for a day.\n"
        "*/cancelleave* - Cancel a scheduled leave.\n"
        "*/cancel* - Stop any current operation."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

# --- NEW: /setupaccount conversation ---
async def setup_account_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the account setup conversation."""
    await update.message.reply_text("Let's set up your account. First, please send me your Beehive username (e.g., GS1234).")
    return GETTING_USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['beehive_username'] = update.message.text
    await update.message.reply_text("Great! Now, please send me your Beehive password.")
    return GETTING_PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    beehive_password = update.message.text
    beehive_username = context.user_data.get('beehive_username')
    user_manager.add_user(user.id, beehive_username, beehive_password)
    await update.message.reply_text(
        f"You are all set up! The final step is to join the announcements group using this link:\n{GROUP_INVITE_LINK}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# --- Leave Request Conversation ---
async def leave_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the /leave conversation."""
    if context.args and (date_str := parse_date(" ".join(context.args))):
        if user_manager.add_leave_date(update.message.from_user.id, date_str):
            await update.message.reply_text(f"Confirmed. You are marked as on leave for {date_str}.")
        else:
            await update.message.reply_text("Sorry, I couldn't process your request.")
        return ConversationHandler.END

    reply_keyboard = [["Today", "Tomorrow"]]
    await update.message.reply_text(
        "Which date would you like to take leave for?\n\nYou can type a date (YYYY-MM-DD) or use the buttons below.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GETTING_LEAVE_DATE

async def get_leave_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the date received during the leave conversation."""
    date_str = parse_date(update.message.text)
    if not date_str:
        await update.message.reply_text("Sorry, I didn't understand that date. Please try again.", reply_markup=ReplyKeyboardRemove())
    elif user_manager.add_leave_date(update.message.from_user.id, date_str):
        await update.message.reply_text(f"Confirmed. You are marked as on leave for {date_str}.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Sorry, I couldn't process your request.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Cancel Leave Conversation ---
async def cancel_leave_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the /cancelleave conversation."""
    if context.args and (date_str := parse_date(" ".join(context.args))):
        if user_manager.remove_leave_date(update.message.from_user.id, date_str):
            await update.message.reply_text(f"Got it. Your leave for {date_str} has been canceled.")
        else:
            await update.message.reply_text("Couldn't find a leave scheduled for that date.")
        return ConversationHandler.END
    
    await update.message.reply_text("Which leave date would you like to cancel? (YYYY-MM-DD)")
    return GETTING_CANCEL_DATE

async def get_cancel_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the date received during the cancel leave conversation."""
    date_str = parse_date(update.message.text)
    if not date_str:
        await update.message.reply_text("Invalid date format. Please use<y_bin_564>-MM-DD.")
    elif user_manager.remove_leave_date(update.message.from_user.id, date_str):
        await update.message.reply_text(f"Got it. Your leave for {date_str} has been canceled.")
    else:
        await update.message.reply_text("Couldn't find a leave scheduled for that date.")
    return ConversationHandler.END

# --- Welcome New Member Handler ---
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets a user when they join the group and tags them."""
    result = update.chat_member
    if result.new_chat_member.status == ChatMember.MEMBER:
        user = result.new_chat_member.user
        logger.info(f"User {user.full_name} joined the group.")
        user_mention = f"[{user.first_name}](tg://user?id={user.id})"
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Welcome to the team, {user_mention}! I'll keep you updated on your automation status here.",
            parse_mode='MarkdownV2'
        )

# --- Global Cancel Command ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels any active conversation."""
    await update.message.reply_text("Operation canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Builds and runs the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            # NEW: The setup process is now initiated by /setupaccount
            CommandHandler("setupaccount", setup_account_start),
            CommandHandler("leave", leave_start),
            CommandHandler("cancelleave", cancel_leave_start),
        ],
        states={
            GETTING_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            GETTING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            GETTING_LEAVE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_leave_date)],
            GETTING_CANCEL_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cancel_date)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, invalid_input),
        ],
    )
    # Add the conversation handler first
    application.add_handler(conv_handler)
    
    # Add the simple /start command handler (it's not part of the conversation)
    application.add_handler(CommandHandler("start", start))
    
    # Add the handler to watch for new members
    application.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
