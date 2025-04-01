import time
import json
from openai import OpenAI
import random

system_message = "Ты --- эксперт по знакомствам, который берёт интервью с человеком и основываясь на нём, пишет для этого человека привлекательную анкету для сайта знакомств на русском языке от первого лица. Это должен быть сплошной текст без абзацов, от 15 до 75 слов."
import json

with open('handcrafted_dataset.json', 'r') as file:
    data = json.load(file)

profiles = data["data"]
dataset_ft = []
questions = [
    "Кем ты работаешь/на кого учишься?",
    "Чем ты занимаешься в свободное время?",
    "Зачем ты здесь, что ищешь?",
    "Как бы ты описал себя тремя словами?",
    "Абсолютно любой интересный факт про тебя?"
]
q = len(questions)
last = -1
dataset_ft = []
for i in range(len(profiles)):
    if len(dataset_ft) >= 100:
        break
    profile = profiles[i]
    if q - profile["answers"].count("Не знаю") >= 3 and len(profile["bio"].split()) <= 75:
        last = i
        interview = ""
        answers = profile["answers"]
        for j in range(q):
            interview += f"- {questions[j]} - {answers[j]}\n"
        dataset_ft.append({
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": "\n Интервью: " + interview
                },
                {
                    "role": "assistant",
                    "content": profile["bio"]
                }
            ]
        })
print(last)
print(dataset_ft)

with open("dataset_ft.jsonl", "w") as f:
    for entry in dataset_ft:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")

API_KEY = ''
JSONL_FILE_PATH = "dataset_ft.jsonl"
MODEL_NAME = "gpt-4o-mini-2024-07-18"
JOB_SUFFIX = "dating1"


def write_jsonl(data, file_path):
    with open(file_path, "w") as f:
        for line in data:
            f.write(line + "\n")


def upload_files(client):
    train_file = client.files.create(
        file=open(JSONL_FILE_PATH, "rb"),
        purpose="fine-tune"
    )
    print(f"Training File ID: {train_file.id}")

    return train_file.id


def create_fine_tuning_job(client, training_file_id):
    try:
        job = client.fine_tuning.jobs.create(
            training_file=training_file_id,
            model=MODEL_NAME,
            suffix=JOB_SUFFIX,
            hyperparameters={"n_epochs": 3}  # Adjust epochs as needed
        )
        print(f"Job created. ID: {job.id}")
        return job.id
    except Exception as e:
        print(f"Error creating job: {str(e)}")
        return None


def monitor_job(client, job_id):
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status
        if status in ["succeeded", "failed"]:
            print(f"Job {job_id} {status}.")
            if status == "succeeded":
                print(f"Fine-tuned model: {job.fine_tuned_model}")
            break
        else:
            print(f"Current status: {status}. Sleeping for 60 seconds...")
            time.sleep(60)


client = OpenAI(api_key=API_KEY)

train_file_id = upload_files(client)

job = client.fine_tuning.jobs.create(
    training_file=train_file_id,
    model=MODEL_NAME,
    suffix=JOB_SUFFIX,
    hyperparameters={"n_epochs": 2}
)
print(f"Job created. ID: {job.id}")

monitor_job(client, job.id)

model1 = "ft:gpt-4o-mini-2024-07-18:personal:dating1:BH79i1o1"  # очищенные анкеты
model2 = "ft:gpt-4o-mini-2024-07-18:personal:dating1:BH7ZmMBB"  # неочищенные анкеты
model3 = "ft:gpt-4o-mini-2024-07-18:personal:dating1:BH82Ccte"  # 25 сделанных анкет
model4 = "gpt-4o-mini-2024-07-18"  # исходная модель

add_prompt = "Используй флирт, красивый язык и немного юмора. Твоя анкета должна быть краткой, но привлекательной и очаровательной."
add_prompt2 = "Напиши хорошую анкету для сайта знакомств, основываясь на этом интервью. Верни сплошной недлинный текст без абзацев."
# model_name = "gpt-4o-mini-2024-07-18"
completion = client.chat.completions.create(
    model=model4,
    messages=[
        {
            "role": "system",
            "content": "system_message"
        },
        {"role": "user", "content": """
- Кем ты работаешь/на кого учишься?
- Учусь на программиста
- Чем ты занимаешься в свободное время?
- Играю в баскетбол и смотрю советские фильмы
- Зачем ты здесь?
- Ищу мать моих будущих детей
- Как бы ты описал себя тремя словами?
- Целеустремлённый, умный, весёлый
- Любой интересный факт про тебя?
- Летал на параплане
"""
         }]
)
print("Response:")
print(completion.choices[0].message.content)
