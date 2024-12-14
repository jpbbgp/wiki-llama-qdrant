import json
import config
from llama_index.llms.openai import OpenAI

def access_data() -> any:
    try:
        with open(config.DATA_JSON_PATH, 'r') as data_file:
            data = json.load(data_file)
        return data
    except FileNotFoundError:
        return None

def init(chat):
    global data, messages
    data = access_data()
    messages = chat['messages']

async def gen_title(response,question, chat)->None:
    init(chat)
    if len(messages) == 3:
        chat_title_task = OpenAI().acomplete(config.TITLE_PROMPT.format(response = response, question = question))
        chat_title =  await chat_title_task
        chat['title'] = chat_title.text
    else:
        pass
    save_data(data)

async def gen_summary(question, chat)->None:
    init(chat)
    if len(messages) % 10 == 0 and len(messages) > chat['summary_used_messages']:
        chat_summary_task = OpenAI().acomplete(config.SUMMARY_PROMPT.format(
            summary = chat['summary'],
            history = messages[-10:]
        ))
        chat_summary =  await chat_summary_task
        chat['summary'] = chat_summary.text
        chat['summary_used_messages'] = len(messages)
    else:
        pass
    save_data(data)


def save_data(data)->None:
    with open(config.DATA_JSON_PATH, 'w') as data_json:
        json.dump(data, data_json, indent=4)