import re


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