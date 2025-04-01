from make_gpt_request import make_gpt_request
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import emoji


def calc_Flesh_Kincaid_Grade_rus(text):
    """
     Функция возвращает оценку удобочитаемости текста в соответствии с индексом Флеша-Кинкейда, адаптированного для русского языка
    :Параметры: текст для оценивания
    :Результат: оценка
    """
    RU_VOWELS = [u'а', u'е', u'и', u'у', u'о', u'я', u'ё', u'э', u'ю', u'я', u'ы']
    RU_MARKS = [u'ь', u'ъ']
    SENTENCE_SPLITTERS = [u'.', u'?', u'!']
    RU_LETTERS = [u'а', u'б', u'в', u'г', u'д', u'е', u'ё', u'ж', u'з', u'и', u'й', u'к', u'л', u'м', u'н', u'о', u'п',
                  u'р', u'с', u'т', u'у', u'ф', u'х', u'ц', u'ч', u'ш', u'щ', u'ъ', u'ы', u'ь', u'э', u'ю', u'я']
    SPACES = [u' ', u'\t']
    sentences = 0
    chars = 0
    spaces = 0
    letters = 0
    syllabes = 0
    words = 0

    wordStart = False
    for l in text.splitlines():
        chars += len(l)
        if l and l[-1] not in SENTENCE_SPLITTERS:
            sentences += 1
        for ch in l:
            if ch in SENTENCE_SPLITTERS:
                sentences += 1
            if ch in SPACES:
                spaces += 1

        for w in l.split():
            has_syl = False
            wsyl = 0
            for ch in w:
                if ch in RU_LETTERS:
                    letters += 1
                if ch in RU_VOWELS:
                    syllabes += 1
                    has_syl = True
                    wsyl += 1
            if has_syl:
                words += 1
    if sentences == 0 or words == 0:
        return 0
    n = 0.49 * (float(words) / sentences) + 7.3 * (float(syllabes) / words) - 16.59
    return n


pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")
label_to_score = {
    'Very Negative': 0, 'Negative': 0.25, 'Neutral': 0.5, 'Positive': 0.75, 'Very Positive': 1
}


def grade_emoji_usage(bio):
    """
     Функция оценивает текст по количеству эмодзи в нём
     :Параметры: текст для оценивания
    :Результат: оценка
    """
    emojis = [c for c in bio if c in emoji.EMOJI_DATA]
    count = len(emojis)

    if count == 0:
        return 0.7
    elif 1 <= count <= 3:
        return 1.0
    elif 4 <= count <= 5:
        return 0.6
    else:
        return 0.3


def grade_with_gpt(bio):
    """
     Функция оценивает текст по наличию в нём юмора и приглашения к диалогу
    :Параметры: текст для оценивания
    :Результат: оценка
    """
    prompt = """Ниже приведён список вопросов о профиле в приложении для знакомств и сам профиль. Каждый вопрос требует ответа да или нет. Внимательно изучи текст профиля и верни ответы в формате Python List. В случае ответа да возвращай 1, иначе 0. ВОЗВРАЩАЙ 1 ТОЛЬКО ЕСЛИ ОТВЕТ ТОЧНО ДА. Не возвращай ничего кроме списка. Вопросы:
    - Является ли автор данного текста веселым человеком (много шутит)?
    - Содержит ли данный текст фразу-приглашение к общению (по типу "жду твоего сообщения" или "напиши мне если...")?
    Профиль:
    """
    prompt += bio
    res = make_gpt_request(prompt, temperature=0.6)
    res_list = [0, 0]
    try:
        res_list = eval(res)
    except:
        try:
            res_list = eval(res[10:-4])
        except:
            print('ERROR')
            print(res)
    try:
        return sum(res_list)
    except:
        return 0


def calculate_uniqueness(texts):
    """
     Функция оценивает каждый текст в наборе по его уникальности
     :Параметры: список текстов для оценивания
    :Результат: список оценок в соответствующем порядке
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity_matrix = cosine_similarity(tfidf_matrix)

    n_texts = len(texts)
    uniqueness_scores = []

    for i in range(n_texts):
        avg_similarity = (similarity_matrix[i].sum() - similarity_matrix[i, i]) / (n_texts - 1)
        uniqueness_score = 1 - avg_similarity
        uniqueness_scores.append(uniqueness_score)

    return uniqueness_scores


def calculate_scores(profiles, reses):
    """
     Функция оценивает набор анкет комплексным оцениванием
     :Параметры: список текстов для оценивания, список ответов на вопросы или интервью
    :Результат: список оценок в соответствующем порядке
    """
    uniqueness_scores = calculate_uniqueness(profiles)

    scores = [0 for _ in range(n)]
    for i in range(n):
        if i % 10 == 0:
            print(i, "completed")
        # if q - reses[i].count("Не знаю") < 2:
        #    continue
        scores[i] += 1 * (q - reses[i].count("Не знаю"))
        scores[i] += uniqueness_scores[i] * 0.5
        scores[i] += grade_emoji_usage(profiles[i]) * 0.5
        scores[i] += calc_Flesh_Kincaid_Grade_rus(profiles[i]) / 10
        scores[i] += grade_with_gpt(profiles[i])

        sentences = list(profiles[i].split("."))
        av_sentiment = sum([label_to_score[el['label']] for el in pipe(sentences)]) / len(sentences)
        scores[i] += av_sentiment

    return scores


questions = [
    "Кем ты работаешь/на кого учишься?",
    "Чем ты занимаешься в свободное время?",
    "Зачем ты здесь, что ищешь?",
    "Как бы ты описал себя тремя словами?",
    "Абсолютно любой интересный факт про тебя?"
]
prompt_start = """
Ниже приведён список вопросов о человеке и профиль этого человека из приложения для знакомств. Попробуй ответить на эти вопросы от имени этого человека. Не включай в ответы информацию не по теме. ОПИРАЙСЯ ТОЛЬКО НА ТЕКСТ. Верни ответы в формате Python List в порядке, соответствующим вопросам, не возвращай ничего кроме этого. Если про какой-то вопрос ВООБЩЕ нет релевантной информации, обязательно возвращай "_" как ответ. Вопросы:
"""
prompt = prompt_start
for question in questions:
    prompt += "- " + question + "\n"
prompt += "Профиль:\n"
print(prompt)

with open('profiles.json', 'r') as file:
    profiles_dict = json.load(file)

MIN_WORDS = 15
MAX_WORDS = 75
profiles = profiles_dict['profiles']
profiles = [profile for profile in profiles if len(profile.split()) >= MIN_WORDS and len(profile.split()) <= MAX_WORDS]
cleared_profiles = [profile.split("–", maxsplit=1)[1] for profile in profiles]
print(len(profiles))
# random.shuffle(profiles)
reses = []
n = len(profiles)
profiles_subset = cleared_profiles[:n]
q = len(questions)
for i in range(n):
    if i % 10 == 0:
        print(i, "completed")
    res = make_gpt_request(prompt + profiles_subset[i], temperature=0.6)
    res_list = ["Не знаю" for _ in range(q)]
    try:
        res_list = eval(res[10:-4])
        res_list = [str(el) if el != "_" else "Не знаю" for el in res_list]
    except:
        try:
            res_list = eval(res)
            res_list = [str(el) if el != "_" else "Не знаю" for el in res_list]
        except:
            print('ERROR')
            print(res)
    if len(res_list) != q:
        res_list = ["Не знаю" for _ in range(q)]
    reses.append(res_list)

scores = calculate_scores(profiles_subset, reses)
