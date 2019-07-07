# -*- coding: utf-8 -*-
# Imports general functions
import logging
import subprocess as sp
import os
import io
import unidecode as u

# Imports Telegram Bot
from telegram import Bot, ParseMode
from telegram.ext import Updater, MessageHandler, Filters
from Commons import log_it, get_res_string

# Imports Google APIs
from google.cloud import vision, speech
from google.cloud.vision import types as v_types
from google.cloud.speech import enums
from google.cloud.speech import types as s_types

#Import Image search/download
from google_images_download import google_images_download

# Import credentials and definition
from secret_stuff import declare_vars
declare_vars()

# Declaring google APIs clients
client = vision.ImageAnnotatorClient()
s_client = speech.SpeechClient()

# Declaring config for ogg audio file
config = s_types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=16000,
    language_code='es-ES')

# Declaring logging config.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, handlers=[
        logging.FileHandler("TEL_BOT.log"),
        logging.StreamHandler()])

# Declaring image download client
FNULL = open(os.devnull, 'w')
response = google_images_download.googleimagesdownload()
arguments = {"keywords":"Beaches","limit":1,"print_urls":True}

# Declaring Telegram bot client
tb = Bot(token=os.environ['TB_TOKEN'])
tb_up = Updater(tb.token)

# Function to analyze pictures.
def picture(bot, update):
    # Log information
    chat_id = update.message.chat_id
    log_it(chat_id, str(update.message.photo[-1].file_id), "voice")
    update.message.reply_text("Analizando la imagen!")

    # Downloading and opening image
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = '{}.jpg'.format(photo_file.file_id)
    photo_file.download(filename)
    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    # Analyzing image with google API
    image = v_types.Image(content=content)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # Handling results
    res = 'Hemos encontrado la siguiente info:\n\nLabels:\n'
    for label in labels[:3]:
        res = res + str(label.description) + ' : ' + '%.2f' % (label.score*100) + '%\n'
    response = client.web_detection(image=image).web_detection
    res = res + get_res_string(response)

    # Sending results to user
    update.message.reply_text(res, disable_web_page_preview=True, parse_mode='HTML')
    sp.call(["rm", filename])

# Function to download picture from text
def text(bot, update):
    # Log information
    text = update.message.text
    log_it(update.message.chat_id, text, "text")
    update.message.reply_text("Buscando una imagen!")

    # Searching and downloading images
    arguments["keywords"]=u.unidecode(text)
    arguments["silent_mode"]=True
    paths = response.download(arguments)

    #Sending found image to user
    tb.send_photo(chat_id=update.message.chat_id, caption="Palabras clave: "+ text, photo=open(paths[0][u.unidecode(text)][0], 'rb'))
    sp.call(["rm","-r", "downloads"])

# Function to download picture from voice
def voice(bot, update):
    # Log information
    chat_id = update.message.chat_id
    log_it(chat_id, str(update.message.voice.file_id), "voice")
    update.message.reply_text("Buscando una imagen!")

    # Downloading and opening audio file
    newFile = tb.get_file(update.message.voice.file_id)
    file_name = str(chat_id)+'.ogg'
    newFile.download(file_name)
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = s_types.RecognitionAudio(content=content)

    # Translating audio file to text with google API
    s_response = s_client.recognize(config, audio)
    for result in s_response.results:
        text = result.alternatives[0].transcript
    sp.call(["rm", file_name])
    log_it(update.message.chat_id, str(text), "voice")

    # Searching and downloading images
    arguments["keywords"]=u.unidecode(text)
    arguments["silent_mode"]=True
    paths = response.download(arguments)

    #Sending found image to user
    tb.send_photo(chat_id=update.message.chat_id, caption="Palabras clave: "+text, photo=open(paths[0][u.unidecode(text)][0], 'rb'))
    sp.call(["rm","-r", "downloads"])

# Declaring Telegram Handlers
# If recieved == text --> text()
tb_up.dispatcher.add_handler(MessageHandler(Filters.text, text))
# If recieved == voice --> voice()
tb_up.dispatcher.add_handler(MessageHandler(Filters.voice, voice))
# If recieved == picture --> picture()
tb_up.dispatcher.add_handler(MessageHandler(Filters.photo, picture))

# Starting the bot polling (infinite loop)
tb_up.start_polling()
tb_up.idle()