from make_gpt_request import make_gpt_request
from make_gigachat_request import make_gigachat_request
from scoring import calculate_scores

cool_prompt = """
Ты --- эксперт по знакомствам, который берёт интервью с человеком и основываясь на нём, пишет для этого человека привлекательную анкету для сайта знакомств на русском языке от первого лица. Это должен быть сплошной текст без абзацов, от 15 до 75 слов. Обязательно используй флирт, юмор и эмодзи и пиши красивым языком. Интервью:
"""
few_shot_prompt = """
Составь анкету по приведённому ниже интервью. Вот пару удачных примеров:
  Интервью #1:
  - Кем ты работаешь/на кого учишься?
  - Учусь в политехническом колледже имени Николая Николаевича Годовикова на авиатехника
  - Чем ты занимаешься в свободное время?
  - Учусь по возможности летать на мотопараплане, люблю обнимашки, путешествовать, кататься на велосипеде, сочинять хоку
  - Зачем ты здесь, что ищешь?
  - Ищу новые знакомства, отношения
  - Как бы ты описал себя тремя словами?
  - Творческий, активный, общительный
  - Абсолютно любой интересный факт про тебя?
  - Выполнил на мотопараплане 24 самостоятельных вылета и налетал 4 часа 50 минут
  Анкета #1:
  Учусь на авиатехника, поэтому в будущем соберу для нас частный самолёт. А пока люблю ездить на велосипеде и летать на мотопараплане. Если напишешь мне, сочиню для тебя хоку😉.

  Интервью #2:
  - Кем ты работаешь/на кого учишься?
  - Фотограф
  - Чем ты занимаешься в свободное время?
  - Фотография, юмор, стендап
  - Зачем ты здесь, что ищешь?
  - Нужен хороший друг или подруга
  - Как бы ты описал себя тремя словами?
  - Юморист, любитель, фотограф
  - Абсолютно любой интересный факт про тебя?
  - Пробую себя в стендапе
  Анкета #2:
  Умею классно шутить и фотографировать, поэтому расчищай место для фоток, где ты улыбаешься😁. Напиши мне, если хочешь в будущем стать подругой успешного стендап-комика.

  Вот само интервью, по которому нужно составить анкету:
*Интервью*
"""
sysmes = ("Ты --- эксперт по знакомствам, который берёт интервью с человеком и основываясь на нём, пишет для этого "
          "человека привлекательную анкету для сайта знакомств на русском языке от первого лица. Это должен быть "
          "сплошной текст без абзацов, от 15 до 75 слов.")


def gen_gpt_prompting(interview):
    return make_gpt_request(cool_prompt + interview)


def gen_gpt_few_shot(interview):
    return make_gpt_request(few_shot_prompt + interview)


def gen_gpt_fine_tuning(interview):
    return make_gpt_request(interview, system_message=sysmes,
                            model_name="ft:gpt-4o-mini-2024-07-18:personal:dating1:BH79i1o1")


def gen_gpt_fine_tuning_custom(interview):
    return make_gpt_request(interview, system_message=sysmes,
                            model_name="ft:gpt-4o-mini-2024-07-18:personal:dating1:BH82Ccte")


def gen_gigachat_prompting(interview):
    return make_gigachat_request(cool_prompt + interview)


def gen_gigachat_few_shot(interview):
    return make_gigachat_request(few_shot_prompt + interview)


import json
import random

'''
def parse_jsonl_and_extract_user_content(file_path):
    user_contents = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                data = json.loads(line.strip())
                if "messages" in data:
                    for message in data["messages"]:
                        if message.get("role") == "user":
                            user_contents.append(message.get("content", ""))
            except json.JSONDecodeError as e:
                print(f"Ошибка при парсинге строки: {line}. Ошибка: {e}")

    return user_contents


file_path = "/content/dataset_ft_enhanced.jsonl"
user_contents = parse_jsonl_and_extract_user_content(file_path)
print(user_contents[0])'

test_df = [random.choice(user_contents) for _ in range(100)]

profiles1 = []
inter1 = []
profiles2 = []
inter2 = []
profiles3 = []
inter3 = []
profiles4 = []
inter4 = []
profiles5 = []
inter5 = []
profiles6 = []
inter6 = []

for interview in test_df:
    pr1 = gen_gpt_prompting(interview)
    pr2 = gen_gpt_few_shot(interview)
    pr3 = gen_gpt_fine_tuning(interview)
    pr4 = gen_gpt_fine_tuning_custom(interview)
    pr5 = gen_gigachat_prompting(interview)
    pr6 = gen_gigachat_few_shot(interview)
    profiles1.append(pr1)
    profiles2.append(pr2)
    profiles3.append(pr3)
    profiles4.append(pr4)
    profiles5.append(pr5)
    profiles6.append(pr6)

scores1 = calculate_scores(profiles1, test_df)
scores2 = calculate_scores(profiles2, test_df)
scores3 = calculate_scores(profiles3, test_df)
scores4 = calculate_scores(profiles4, test_df)
scores5 = calculate_scores(profiles5, test_df)
scores6 = calculate_scores(profiles6, test_df)
print(np.mean(scores1), np.mean(scores2), np.mean(scores3), np.mean(scores4), np.mean(scores5), np.mean(scores6))
'''