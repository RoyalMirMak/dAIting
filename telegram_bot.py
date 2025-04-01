from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler
import logging
import random
from collections import defaultdict
from testing import gen_gpt_prompting, gen_gpt_fine_tuning_custom, gen_gigachat_prompting 
from scoring import give_advice

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

QUESTIONS = [
    "Кем ты работаешь/на кого учишься?",
    "Чем занимаешься в свободное время?",
    "Зачем ты здесь? Что ищешь?",
    "Как бы ты описал себя тремя словами?",
    "Абсолютно любой интересный факт про тебя?",
]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = []

    keyboard = [
            [InlineKeyboardButton("Сгенерировать анкету по 5 ответам на вопросы", callback_data="restart")],
            [InlineKeyboardButton("Дать совет, как улучшить твою анкету", callback_data="advice")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        'Привет! Я создан, чтобы люди становились в тебе заинтересованы "с первого прочтения". Как именно я могу тебе помочь?\n\n',
        reply_markup=reply_markup
    )
    return 0

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = []
    await query.edit_message_text(
        QUESTIONS[0],
        reply_markup=None
    )
    return 0

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = []
    await query.message.reply_text(
        "Введи свою анкету, я помогу тебе ее исправить",
        reply_markup=None
    )
    user_data[user_id].append(update.message.text)
    result = give_advice(user_data[-1])
    keyboard = [
            [InlineKeyboardButton("Сгенерировать анкету по 5 ответам на вопросы", callback_data="restart")],
            [InlineKeyboardButton("Дать совет, как улучшить твою анкету", callback_data="advice")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        'Вот мой вердикт:\n\n' + result + 'Как я могу помочь тебе дальше?',
        reply_markup=reply_markup
    )
    return 0

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = []
    user_data[user_id].append(update.message.text)
    
    current_question = len(user_data[user_id])
    
    if current_question < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[current_question])
        return current_question
    else:        
        summary = "Итого, что мы имеем\n\n"
        summary += "\n".join(
            f"{i+1}. {q}\n   {a}"
            for i, (q, a) in enumerate(zip(QUESTIONS, user_data[user_id]))
        )
        summary += "\n\nТы всего в одной кнопке от вступления в лучшую жизнь"

        keyboard = [
            [InlineKeyboardButton("Сгенерировать анкету", callback_data="generate_profile")],
            [InlineKeyboardButton("Ответить на вопросы заново", callback_data="restart")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, reply_markup=reply_markup)

async def generate_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_data or len(user_data[user_id]) < len(QUESTIONS):
        await query.edit_message_text("Что-то пошло не так. Попробуйте начать заново /start")
        return ConversationHandler.END
    
    generation_functions = [
        gen_gpt_prompting,
        gen_gpt_fine_tuning_custom,
        gen_gigachat_prompting
    ]
    selected_function = random.choice(generation_functions)

    summary = "\n".join(
            f"{i+1}. {q}\n   {a}"
            for i, (q, a) in enumerate(zip(QUESTIONS, user_data[user_id]))
        )
    
    
    try:
        profile_text = selected_function(summary)
        
        keyboard = [
            [InlineKeyboardButton("Сгенерировать заново", callback_data="generate_profile")],
            [InlineKeyboardButton("Ответить на вопросы заново", callback_data="restart")],
            [InlineKeyboardButton("Дать совет, как улучшить твою анкету", callback_data="advice")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Вот твоя анкета, сгенерированная с помощью {selected_function.__name__}:\n\n{profile_text}",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error generating profile: {e}")
        await query.edit_message_text(
            f"Произошла ошибка {e}, при генерации анкеты. Попробуйте еще раз.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Попробовать снова", callback_data="generate_profile")],
                [InlineKeyboardButton("Ответить на вопросы заново", callback_data="restart")]
                [InlineKeyboardButton("Дать совет, как улучшить твою анкету", callback_data="advice")]
            ])
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    
    await update.message.reply_text(
        "Почему ты перестал хотеть быть сигмой(. Напиши /start, чтобы начать заново."
    )
    return ConversationHandler.END

def main():
    application = Application.builder().token("7622446016:AAHRyc7ACmyuKyea8G8Tw4W88pB1M1Z0NKY").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
            for i in range(len(QUESTIONS))
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(generate_profile, pattern="^generate_profile$"))
    application.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    application.add_handler(CallbackQueryHandler(advice, pattern="^advice$"))
    application.run_polling()

if __name__ == "__main__":
    main()
