import logging
import logging.handlers
import functools
import re
from random import choice
import constants
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler


log_formatter = logging.Formatter('%(asctime)s -- %(name)s:%(levelname)s: %(message)s')

file_handler = logging.handlers.TimedRotatingFileHandler(filename="root.log", when="midnight", interval=1, backupCount=7, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_formatter)

# Using root logger to create full logs
logging.getLogger().addHandler(file_handler)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram.ext.Application').setLevel(logging.INFO)

# Creating an error handler to keep track of errors (of the root logger) only
error_handler = logging.handlers.TimedRotatingFileHandler(filename='errors.log', when='midnight', interval=1, backupCount=7, encoding="utf-8")
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(log_formatter)
logging.getLogger().addHandler(error_handler)

# Creating a custom conversation logger to keep track of the conversation only.
# It will not be saved to a separate file, but will stream logs to the console
# Logs from this logger will be included in the root log
conversation_logger = logging.getLogger("conversation")

conversation_handler =  logging.StreamHandler()
conversation_handler.setLevel(logging.INFO)
conversation_handler.setFormatter(log_formatter)
conversation_logger.addHandler(conversation_handler)

conversation_logger.setLevel(logging.INFO)


# Logging logic

def logging_incoming_messages(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        update = args[0]
        chat_type: str = update.message.chat.type
        if chat_type == 'private':
            chat_name: str = update.message.chat.full_name
        else: 
            chat_name: str = update.message.chat.title
        attributes = {att: getattr(update.message, att) for att in constants.MESSAGE_TYPES if getattr(update.message, att)}
        conversation_logger.info(f"USER (@{update.message.from_user.username}) in {chat_type} ({repr(chat_name)}): {attributes}")
        return response
    return wrapper

def logging_bot_response(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        if response:
            update = args[0]
            chat_type: str = update.message.chat.type
            if chat_type == 'private':
                chat_name: str = update.message.chat.full_name
            else: 
                chat_name: str = update.message.chat.title
            conversation_logger.info(f"BOT ({constants.BOT_USERNAME}) in {chat_type} ({repr(chat_name)}): {repr(response)}")
        return response
    return wrapper

def logging_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        update, context = args[0], args[1]
        conversation_logger.error(f"Update {update} caused error {context.error}")
        return response
    return wrapper
        
# Commands

@logging_bot_response
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Calculator", callback_data="calc"),
            InlineKeyboardButton("Service network credentials", callback_data="srvc"),
        ],
        [InlineKeyboardButton("Go back", callback_data="bck")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    response = constants.START
    await update.message.reply_text(response, reply_markup=reply_markup)
    return response
  
@logging_bot_response
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = constants.HELP
    await update.message.reply_text(response)
    return response

@logging_bot_response
async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id == constants.CHAT_ID:
        response = ", ".join(f"[@{k}](tg://user?id={v})" for k, v in constants.ALL.items())
    else:
        response = "pass"
    await update.message.reply_text(response, parse_mode=constants.MARKDDOWN)
    return response

# Buttons

@logging_bot_response
async def start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    
    query = update.callback_query
    await query.answer()
    if query.data == "calc":
        response = "Держи: " + constants.CALCULATOR_LINK
    elif query.data == "srvc":
        response = constants.CREDENTIALS
    else:
        response = "Пака........."

    await query.edit_message_text(text=response)
    return response
    
@logging_bot_response
async def pamyatka_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    
    query = update.callback_query
    await query.answer()
    if query.data == "y":
        response = "Уместно."
    else:
        response = "Неуместно....."
        
    await query.edit_message_text(text=response)
    return response

# Responses

@logging_bot_response 
@logging_incoming_messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(constants.YES, callback_data="y")], [InlineKeyboardButton(constants.NO, callback_data="n")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    response = constants.MEMO_AUDIO
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode=constants.MARKDDOWN)
    return response

def handle_response(update: Update, text: str):
    """Here are the words and phrases that Stacey reacts to if she is mentioned in the message sent in a group. 
    In private chats she will react to them without a mention."""
    
    processed: str = text.lower()
    reply_to_message_id = None
    response = constants.BASIC_RESPONSE
    if any(trigger in processed for trigger in constants.GREETING_OPTIONS):
        response = constants.GREETING_RESPONSE
    elif any(trigger in processed for trigger in constants.ASKING_FOR_A_NICKNME_OPTIONS):
        name = choice(constants.SASHKA_NICKNAMES)
        response = f"{name} @{constants.SASHKA_USERNAME}"
    elif any(trigger in processed for trigger in constants.CUSS_REQUEST_OPTIONS):
        reply_to_message_id = update.message.reply_to_message.message_id
        response = choice(constants.CUSS_OPTIONS)
    return response, reply_to_message_id

@logging_bot_response
@logging_incoming_messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type: str = update.message.chat.type
    text: str = update.message.text
    
    if chat_type in ["group", "supergroup"]:
        if constants.BOT_USERNAME in text:
            new_text: str = text.replace(constants.BOT_USERNAME, "").strip()
            response, reply_to_message_id = handle_response(update, new_text)
        else:
            return
    else:
        response, reply_to_message_id = handle_response(update, text)
        
    await update.message.reply_text(response, parse_mode=constants.MARKDDOWN, reply_to_message_id=reply_to_message_id)
    return response
 
@logging_bot_response
@logging_incoming_messages
async def handle_suki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = constants.STICKER_WE
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=response)
    return response  

@logging_bot_response
@logging_incoming_messages
async def handle_sashechka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = choice(constants.STICKERS_SASHKA)
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=response)
    return response

@logging_bot_response
@logging_incoming_messages
async def handle_silence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = constants.STICKER_SILENCE
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=response)
    return response

@logging_bot_response    
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = constants.NO_COMMAND_FOUND_MESSAGE
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    return response

@logging_incoming_messages
async def handle_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return    

@logging_errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return
    
    
if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(constants.TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("all", all_command))
    
    # Query handlers
    app.add_handler(CallbackQueryHandler(start_button, pattern="^calc|srvc|bck$"))
    app.add_handler(CallbackQueryHandler(pamyatka_button, pattern="^y|n$"))
    
    # Messages
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile("сашечк", flags=re.IGNORECASE)), handle_sashechka))
    app.add_handler(MessageHandler(filters.Regex(re.compile("молчи", flags=re.IGNORECASE)), handle_silence))
    app.add_handler(MessageHandler(filters.Regex(re.compile("кто мы|мы кто", flags=re.IGNORECASE)), handle_suki))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.ALL, handle_default))
    
    # Errors
    app.add_error_handler(error)
    
    # Polls the bot    
    print("Polling...")
    app.run_polling(poll_interval=constants.POLL_INTERVAL)