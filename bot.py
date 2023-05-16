import logging
import os
from api import ask_openAI, parse_image_text, substitute_string
from dotenv import load_dotenv
from telegram import ForceReply, Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, constants
from variables import *

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text("Nice to see you! Just write me yor question!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Just ask a question!")


async def ask_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks model of the bot"""
    reply_keyboard = [["GPT-3.5", "GPT-4"]]
    context.user_data['question'] = update.message.text
    await update.message.reply_text("Please, select the model of chat:",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="GPT Model?"))
    return MODEL_SELECTION


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask OpenAI and print the answer."""
    question = context.user_data.get('question')
    if question is None:
        await update.message.reply_text("No question found\, try once again", parse_mode=constants.ParseMode.MARKDOWN_V2)
    if update.message.text == 'GPT-3.5':
        await update.message.reply_text(ask_openAI(question, 'gpt-3.5-turbo'), parse_mode=constants.ParseMode.MARKDOWN_V2)
    elif update.message.text == 'GPT-4':
        await update.message.reply_text(ask_openAI(question, 'gpt-4'), parse_mode=constants.ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Unknown GPT model\, try once again", parse_mode=constants.ParseMode.MARKDOWN_V2)


async def photo_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse text from photo, Ask OpenAI and print the answer."""
    file = await context.bot.getFile(update.message.photo[-1].file_id)
    await file.download_to_drive(custom_path=f'photos/{update.effective_chat.id}.jpg')
    question = parse_image_text(update.effective_chat.id)
    await update.message.reply_text(ask_openAI(question, 'gpt-3.5-turbo'), parse_mode=constants.ParseMode.MARKDOWN_V2)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(os.getenv("TG_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(
            filters.TEXT & ~filters.COMMAND, ask_model)],
        states={
            MODEL_SELECTION: [MessageHandler(filters.Regex(
                "^(GPT-3.5|GPT-4)$"), answer)]
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_model)],
    )
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.PHOTO, photo_answer))
    application.run_polling()


if __name__ == "__main__":
    main()
