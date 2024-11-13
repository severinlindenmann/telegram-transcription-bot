# main.py
import os
import telegram
import functions_framework
import asyncio

# using telegram.Bot
async def send(chat, msg):
    await telegram.Bot(os.environ["TELEGRAM_TOKEN"]).sendMessage(chat_id=chat, text=msg)

@functions_framework.http
def webhook(request):
    request_json = request.get_json()
    # get the chat_id and message from the request
    chat_id = request_json["message"]["chat"]["id"]
    
    if "voice" in request_json["message"]:
        file_id = request_json["message"]["voice"]["file_id"]
        asyncio.run(send(chat_id, file_id))
    
    if "text" in request_json["message"]:

        message = request_json["message"]["text"]
        asyncio.run(send(chat_id, message))

    return "ok"



