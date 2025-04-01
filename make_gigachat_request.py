from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GIGACHAT_KEY')

giga = GigaChat(
    credentials=API_KEY,
    verify_ssl_certs=False,
)


def make_gigachat_request(prompt):
    messages = [HumanMessage(content=prompt)]
    res = giga.invoke(messages)
    return res.content
