from random import choice
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

import constants
import log

# Commands

@log.conversation
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
 
@log.conversation
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = constants.HELP
    await update.message.reply_text(response)
    return response

@log.conversation
async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id == constants.CHAT_ID:
        response = ", ".join(f"[@{k}](tg://user?id={v})" for k, v in constants.TEAMMATES.items())
    else:
        response = "pass"
    await update.message.reply_text(response, parse_mode=constants.MARKDDOWN)
    return response

# Buttons

@log.conversation
async def start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    
    query = update.callback_query
    await query.answer()
    if query.data == "calc":
        response = "Here it is: " + constants.CALCULATOR_LINK
    elif query.data == "srvc":
        uid = update.callback_query.from_user.id
        if uid in constants.TEAMMATES.values():
            response = constants.CREDENTIALS
        else:
            response = "Sorry, this data is confidential and is only availble to my Technical Support Teammates. 😔"
    else:
        response = "Paka........."

    await query.edit_message_text(text=response)
    return response
    
@log.conversation
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

@log.conversation
async def handle_edited_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

@log.conversation
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


@log.conversation
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type: str = update.message.chat.type
    text: str = update.message.text
    
    if chat_type in constants.GROUP_TYPES:
        if constants.BOT_USERNAME in text:
            new_text: str = text.replace(constants.BOT_USERNAME, "").strip()
            response, reply_to_message_id = handle_response(update, new_text)
        else:
            return
    else:
        response, reply_to_message_id = handle_response(update, text)
        
    await update.message.reply_text(response, parse_mode=constants.MARKDDOWN, reply_to_message_id=reply_to_message_id)
    return response
 
@log.conversation
async def handle_we(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = constants.STICKER_WE
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=response)
    return response  

@log.conversation
async def handle_sashechka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = choice(constants.STICKERS_SASHKA)
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=response)
    return response

@log.conversation
async def handle_silence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = constants.STICKER_SILENCE
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=response)
    return response

@log.conversation 
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = constants.NO_COMMAND_FOUND_MESSAGE
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    return response

@log.conversation
async def handle_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return    

@log.error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return
    
    
if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(constants.TOKEN).build()
    
    app.add_handler(MessageHandler(filters.UpdateType.EDITED, handle_edited_messages))
    
    # Commands
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("all", all_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Query handlers
    app.add_handler(CallbackQueryHandler(start_button, pattern="^calc|srvc|bck$"))
    app.add_handler(CallbackQueryHandler(pamyatka_button, pattern="^y|n$"))
    
    # Messages
    app.add_handler(MessageHandler(filters.Regex(constants.REGEX_SASHKA), handle_sashechka))
    app.add_handler(MessageHandler(filters.Regex(constants.REGEX_SILENCE), handle_silence))
    app.add_handler(MessageHandler(filters.Regex(constants.REGEX_WE), handle_we))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.ALL, handle_default))
    
    # Errors
    app.add_error_handler(error)
    
    # Polls the bot    
    print("Polling...")
    app.run_polling(poll_interval=constants.POLL_INTERVAL)