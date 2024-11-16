# main.py
import os
import telegram
import functions_framework
import asyncio
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
)

# upload audio file to deepgram and get the transcription
def deepgram_transcribe(file_path):

    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    deepgram = DeepgramClient(DEEPGRAM_API_KEY)

    # Load the audio file into a buffer
    with open(file_path, "rb") as file:
        audio = file.read()

    source = {'buffer': audio}

    # Configure options for audio analysis
    options = PrerecordedOptions(
        model='nova-2',
        detect_language=True,
        smart_format=True,
        diarize=True,
        punctuate=True,
        paragraphs=True,
    )

    # Transcribe the audio from the buffer
    response = deepgram.listen.rest.v("1").transcribe_file(
        source, options, timeout=120000
    )
    
    # delete the audio file
    os.remove(file_path)

    return response

# using telegram.Bot
async def send(bot, chat, msg):
    await bot.sendMessage(chat_id=chat, text=msg)

async def download_audio(bot, file_id):
    return await bot.get_file(file_id)

async def download_file_to_local(bot,chat_id, file_id):
    file = await download_audio(bot, file_id)
    await file.download_to_drive(f'{file_id}.ogg')
    
    # transcribe the audio file
    transcription = "Transkript: " + deepgram_transcribe(f'{file_id}.ogg')['results']['channels'][0]['alternatives'][0]['transcript'] 
    
    # send the transcription to the user
    await send(bot, chat_id, transcription)

@functions_framework.http
def webhook(request):
    request_json = request.get_json()
    bot = telegram.Bot(os.environ["TELEGRAM_TOKEN"])

    # get the chat_id
    chat_id = request_json["message"]["chat"]["id"]

    # check if valid user_name
    user_list = os.getenv("USER_LIST").split(";")
    if request_json["message"]["from"]["username"] not in user_list:
        return "bye"

    # check if the message is an audio file
    if "text" in request_json["message"]:
        msg = request_json["message"]["text"]
        asyncio.run(send(bot, chat_id, msg))

    # check if the message is an audio file
    if "voice" in request_json["message"]:
        file_id = request_json["message"]["voice"]["file_id"]
        asyncio.run(download_file_to_local(bot, chat_id, file_id))

    return "ok"
