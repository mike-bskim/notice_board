from flask import Blueprint, render_template, url_for, redirect

import flask
import json
from functools import wraps
from flask import request, Response
import requests
from bs4 import BeautifulSoup
import urllib.request
from powernad.API import RelKwdStat
import time
from random import uniform

client_id               = "gOdpO8mnvRQFFjEjf6lU"
client_secret           = "maArTmZ7oM" 
NAVER_AD_CUSTOMER_ID    = "2193806"
NAVER_AD_ACCESS_LICENSE = "0100000000b27368371f38c0e9696199a2f0bf775b54d69a7db71b25e2a1751ed8d107b8aa"
NAVER_AD_SECRET_KEY     = "AQAAAACyc2g3HzjA6WlhmaLwv3dbxNMP3fEKwrhT4u0z2QPUoQ=="

NAVER_AD_API_URL = 'https://api.naver.com'
NAVER_BLOG_API_URL = 'https://openapi.naver.com/v1/search/blog?query='
NAVER_SHOP_API_URL = 'https://openapi.naver.com/v1/search/shop?query='

LIMIT = 10

# app = flask.Flask(__name__)
blueprint = Blueprint("naver", __name__, url_prefix="/trendy")

def getSearchList(keyword, URL):
    searchList = []
    encText = urllib.parse.quote(keyword)
    url = URL + encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    response_body = response.read()
    jsonString = response_body.decode('utf-8')
    jsonDict = json.loads(jsonString)
    items = jsonDict['items']
    for item in items:
        title = item['title']
        link = item['link']
        searchList.append({'title': title, 'link': link})
        # print(link)
    return searchList

def getSearchCount(keyword, URL):
    encText = urllib.parse.quote(keyword)
    url = URL + encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    response_body = response.read()
    jsonString = response_body.decode('utf-8')
    jsonDict = json.loads(jsonString)
    if(rescode==200):
        totalCount = jsonDict['total']
    else:
        totalCount = 0   
    return totalCount

def popularlist_unserial():
    NAVER_BEST100 = 'https://search.shopping.naver.com/best100v2/main.nhn#'
    popular10lists = []
    source = requests.get(NAVER_BEST100).text
    soup = BeautifulSoup(source, "html.parser")
    popular10 = soup.find(id="popular_srch_lst") 
    popular10names = popular10.select(".txt")

    for name in popular10names:
        popular10lists.append({"name": name.text})

    return (popular10lists)

def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = json.dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')

    return decorated_function

@blueprint.route('/getPopularlists', methods=['GET'])
@as_json
def popularlist():
    NAVER_BEST100 = 'https://search.shopping.naver.com/best100v2/main.nhn#'
    popular10lists = []
    source = requests.get(NAVER_BEST100).text
    soup = BeautifulSoup(source, "html.parser")
    popular10 = soup.find(id="popular_srch_lst") 
    popular10names = popular10.select(".txt")

    for name in popular10names:
        popular10lists.append({"name": name.text})

    # print('popularlist(): ', popular10lists)
    return (popular10lists)


@blueprint.route('/relatedKeywords', methods=['GET'])
@as_json
def relatedKeywords():
    keywords = []
    if 'keyword' in request.args:
        keyword = str(request.args['keyword']).replace(' ', '')
        # print('keyword: ', keyword)
    else:
        return "Error: keyword field was not provided. Please enter a keyword."

    relKwdStat = RelKwdStat.RelKwdStat(NAVER_AD_API_URL, NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID)
    kwDataList = relKwdStat.get_rel_kwd_stat_list(None, hintKeywords=keyword, showDetail='1')
    # print('kwDataList: ', kwDataList)
    for idx, outdata in enumerate(kwDataList):
        time.sleep(uniform(0.11, 0.12)) # Naver search API limit - Daily 2500 Max 10/sec  
        relKeyword = outdata.relKeyword # A related keyword
        monthlyPcQcCnt = outdata.monthlyPcQcCnt # Sum of PC query counts in recent 30 days.
        monthlyMobileQcCnt = outdata.monthlyMobileQcCnt # Sum of Mobile query counts in recent 30 days. 
        monthlyAvePcCtr = outdata.monthlyAvePcCtr   # Click-through rate of PC in recent 4 weeks.
        monthlyAveMobileCtr = outdata.monthlyAveMobileCtr # Click-through rate of Mobile in recent 4 weeks.
        compIdx = outdata.compIdx   # A competitiveness index based on PC ad. 

        blogsTotal = getSearchCount(relKeyword, NAVER_BLOG_API_URL)
        shopsTotal = getSearchCount(relKeyword, NAVER_SHOP_API_URL)                 

        if(str(monthlyPcQcCnt).isnumeric() and str(monthlyMobileQcCnt).isnumeric() and compIdx == "높음"):
            totalCnt = monthlyPcQcCnt + monthlyMobileQcCnt
            clickCnt = round(monthlyAvePcCtr + monthlyAveMobileCtr, 1)
            # print(idx, relKeyword, totalCnt, clickCnt, blogsTotal, shopsTotal)
            keywords.append({ 'word': relKeyword, 'totalCnt': totalCnt, 'clickCnt': clickCnt, 'blogsTotal': blogsTotal, 'shopsTotal': shopsTotal })
            if(idx >= LIMIT):
                break

    return keywords

@blueprint.route('/getBlogs', methods=['GET'])
@as_json
def getBlogs():
    if 'keyword' in request.args:
        keyword = str(request.args['keyword'])
    else:
        return "Error: keyword field was not provided. Please enter a keyword."

    return getSearchList(keyword, NAVER_BLOG_API_URL)

@blueprint.route('/getShops', methods=['GET'])
@as_json
def getShops():
    if 'keyword' in request.args:
        keyword = str(request.args['keyword'])
    else:
        return "Error: keyword field was not provided. Please enter a keyword."

    return getSearchList(keyword, NAVER_SHOP_API_URL)


@blueprint.route("/", methods=['GET', 'POST'])
def naverList():

    datas = popularlist_unserial()

    if request.method == "POST":
        return redirect(url_for("naver.naverList"))

    else:
        return render_template(
            "naver_search.html",
            datas=datas,
            title="네이버 상품",
        )

# app.run(host="192.168.0.165",port=5000)

print('naver_api.py:', __name__)