from dotenv import load_dotenv
import os
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from main import ai_bot_response

load_dotenv()
TOKEN=os.getenv("TELEGRAM_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

HI, PHOTO, LOCATION, BIO = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("start()!")
    print("User said:")
    print("update.message.text")
    await update.message.reply_text(
        "Hey! My name is Damon, and I'm your digital boyfriend 🤓"
        "Send /cancel to stop talking to me.\n\n",
    )
    return HI

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("ai_chat()!")
    print("User said:")
    print(update.message.text)
    user = update.message.from_user
    await update.message.reply_text(ai_bot_response(update.message.text).replace('"', ''))

    return HI


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "See ya! I hope we can talk again some day", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states HI
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("hi", start)],
        states={
            HI: [MessageHandler(filters.TEXT, ai_chat)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()