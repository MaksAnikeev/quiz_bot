import re
from pprint import pprint
import logging
from textwrap import dedent
import random
from functools import partial
from enum import Enum, auto

import environs
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ParseMode, ReplyKeyboardMarkup, Update)


logger = logging.getLogger(__name__)

class States(Enum):
    START = auto()
    ANSWER = auto()


def create_quiz(quiz):
    question_answer = {}

    for part in quiz:
        part = part.split('\n\n')
        for element in part:
            if re.search(r'\bВопрос\b', element):
                question = element.partition(':\n')[2].replace('\n', '')
            if re.search(r'\bОтвет\b', element):
                answer = element.partition(':\n')[2].replace('\n', '')
                question_answer[question] = answer
    return question_answer


def start(update, context):
    user = update.effective_user
    greetings = dedent(fr'''
                Приветствую {user.mention_markdown_v2()}\!
                Я бот для викторины\.''')

    message_keyboard = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счет"],
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_markdown_v2(text=greetings, reply_markup=markup)
    return States.START


def handle_new_question_request(update, context, question_answer):
    question = random.choice(list(question_answer))
    update.message.reply_text(text=question)
    context.user_data["question"] = question
    context.user_data["question_answer"] = question_answer
    return States.ANSWER


def handle_solution_attempt(update, context):
    global score
    print(score)
    answer = update.message.text
    question_answer = context.user_data["question_answer"]
    question = context.user_data["question"]
    quiz_answer = question_answer[question]
    if quiz_answer.partition('.')[0] == answer or quiz_answer.partition(' (')[0] == answer:
        score += 1
        context.user_data["score"] = score
        update.message.reply_text(text=f'{quiz_answer}')
        answer_message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        message_keyboard = [
            ["Новый вопрос", "Сдаться"],
            ["Мой счет"],
        ]

        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        update.message.reply_text(text=answer_message, reply_markup=markup)
        return States.START

    else:
        answer_message = 'Неправильно… Попробуешь ещё раз?'
        message_keyboard = [
            ["Новый вопрос", "Сдаться"],
            ["Мой счет"],
        ]

        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        update.message.reply_text(text=answer_message, reply_markup=markup)

        return States.ANSWER


def send_correct_answer(update, context):
    question_answer = context.user_data["question_answer"]
    question = context.user_data["question"]
    quiz_answer = question_answer[question]
    update.message.reply_text(text=f'{quiz_answer}')
    handle_new_question_request(update, context, question_answer)


def send_score(update, context):
    score = context.user_data["score"]
    message_keyboard = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счет"],
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(text=f'Ваш счет {score}', reply_markup=markup)
    return States.START


def error(update, context):
    update.message.reply_text('Произошла ошибка')



if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    env = environs.Env()
    env.read_env()

    telegram_bot_token = env.str("TG_BOT_TOKEN")

    score = 0

    with open("../quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as file:
        quiz = file.read().split('\n\n\n')

    question_answer = create_quiz(quiz)

    updater = Updater(telegram_bot_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.START: [
                MessageHandler(Filters.text("Мой счет"), send_score),
                MessageHandler(Filters.text("Новый вопрос"), partial(handle_new_question_request,
                                       question_answer=question_answer)),
            ],
            States.ANSWER: [
                MessageHandler(Filters.text("Новый вопрос"), partial(handle_new_question_request,
                                                                     question_answer=question_answer)),
                MessageHandler(Filters.text("Сдаться"), send_correct_answer),
                MessageHandler(Filters.text("Мой счет"), send_score),
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
        },
        fallbacks=[],
        allow_reentry=True,
        name='bot_conversation',
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()
