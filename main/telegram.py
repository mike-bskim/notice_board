# 텔레그램봇을 위한 라이브러리
# from main import *
# from flask import Blueprint, send_from_directory, Response
# import json

import telegram
import os
from pprint import pprint

# 로그 관련 라이브러리
#import logging

# 기능을 분리해놓은 모듈
# modules.py 파일은 같은 경로에 있어야 합니다.
# from modules import *

# 로그 생성
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

# 봇생성 후 받은 텔레그램 API 토큰
TELEGRAM_TOKEN = "1773459059:AAGJuNIKJySfnZTIpNprf3OUZ-K31icVVV4"
# telepot 의 객체를 생성하여 bot 변수에 저장합니다.
# bot = telepot.Bot(TELEGRAM_TOKEN)
bot = telegram.Bot(token = TELEGRAM_TOKEN)

# webhook = OrderedWebhook(bot, telebotHandler)
# webhook.run_as_thread()

def messageToTelegram(msg):
    bot.sendMessage(chat_id=518558056, text=msg)


print('telegram.py:', __name__)
