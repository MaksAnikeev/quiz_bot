import argparse
import logging
import random

import environs
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from quiz import create_quiz

logger = logging.getLogger(__name__)


def receive_message(vk_token, text, question_answer, quiz_score):
    vk_session = vk.VkApi(token=vk_token)
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            send_message(
                user_id=event.user_id,
                text=text,
                vk_token=vk_token)
            break

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Сдаться":
                question = send_correct_answer(question=question,
                                               user_id=event.user_id)

            elif event.text == "Новый вопрос":
                question = random.choice(list(question_answer))
                send_message(
                    user_id=event.user_id,
                    text=question,
                    vk_token=vk_token)

            elif event.text == "Мой счет":
                send_score(quiz_score=quiz_score,
                           user_id=event.user_id)

            else:
                quiz_score = handle_solution_attempt(question=question,
                                                     answer=event.text,
                                                     user_id=event.user_id,
                                                     quiz_score=quiz_score)


def send_message(user_id, text, vk_token):
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)

    vk_api.messages.send(
        peer_id=user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=text
    )


def handle_solution_attempt(question, answer, user_id, quiz_score):
    quiz_answer = question_answer[question]
    if quiz_answer.partition('.')[0] == answer or\
            quiz_answer.partition(' (')[0] == answer:
        quiz_score += 1
        answer_message = f'{quiz_answer} \n\n Правильно! Поздравляю!' \
                         f' Для следующего вопроса нажми «Новый вопрос»'
        send_message(
            user_id=user_id,
            text=answer_message,
            vk_token=vk_token)
        return quiz_score

    else:
        answer_message = 'Неправильно… Попробуешь ещё раз?'
        send_message(
            user_id=user_id,
            text=answer_message,
            vk_token=vk_token)
        return quiz_score


def send_correct_answer(question, user_id):
    quiz_answer = question_answer[question]
    send_message(
        user_id=user_id,
        text=quiz_answer,
        vk_token=vk_token)
    question = random.choice(list(question_answer))
    send_message(
        user_id=user_id,
        text=question,
        vk_token=vk_token)
    return question


def send_score(quiz_score, user_id):
    send_message(
        user_id=user_id,
        text=f'Ваш счет {quiz_score}',
        vk_token=vk_token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--quiz_path',
        type=str,
        help='quiz_path путь и название файла с вопросами и ответами',
        default='quiz-questions/1vs1200.txt'
    )
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    env = environs.Env()
    env.read_env()

    vk_token = env.str("VK_TOKEN")

    with open(args.quiz_path, "r", encoding="KOI8-R") as file:
        quiz = file.read().split('\n\n\n')

    question_answer = create_quiz(quiz)

    quiz_score = 0

    try:
        greetings = 'Приветствую! Я бот для викторины'
        receive_message(
            vk_token=vk_token,
            text=greetings,
            question_answer=question_answer,
            quiz_score=quiz_score
        )

    except Exception as err:
        print(err)
