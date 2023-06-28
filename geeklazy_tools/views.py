import os.path
from urllib.parse import urlparse
from urllib.parse import parse_qs
import time
import datetime
import base64
import json
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from aip import AipSpeech
import ffmpeg


# 配置谷歌浏览器静默启动【后台启动】
chrome_options = webdriver.ChromeOptions()
# 初始化谷歌浏览器的配置【必须加上】
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')


APP_ID = '34437290'
API_KEY = 'TkvaQuKxbhTocyLRIOLSDn0q'
SECRET_KEY = '18snpzy80Zy3TsGXxGwGS0CcokgK5hj6'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


# Create your views here.
def decode_base64(data):
    """Decode base64, padding being optional.
    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return str(base64.urlsafe_b64decode(data), encoding='utf-8')


def encode_base64(data):
    """Decode base64, padding being optional.
    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    return str(base64.urlsafe_b64encode(bytes(data, encoding='utf-8')), encoding='utf-8')


def lncn_ssr():
    browser = webdriver.Chrome(executable_path="./src/chromedriver", options=chrome_options)
    browser.get("https://lncn.org")
    # print(f"browser text = {browser.page_source}")
    time.sleep(0.5)
    time_ele = browser.find_element(By.CLASS_NAME, "time")
    print(f"执行时间：{datetime.datetime.now()}")
    print(f"最近更新：{time_ele.text}")

    ssr_list = browser.execute_script(
        "return window.document.getElementsByClassName('el-button--small')[0].__vue__.$parent.$data.list")
    browser.quit()
    ssr_links = ""
    for ssr in ssr_list:
        ssr_links += (ssr["url"] + "\n")
    print(ssr_links)
    return ssr_links


def ssr(request):
    if request.method == "GET":
        parse = urlparse(request.get_full_path())
        query = parse_qs(parse.query)
        print(f"type：{query.get('type')}")
        if query.get("type")[0] == "lncn" or query.get("type") is None:
            return HttpResponse(content=encode_base64(lncn_ssr()))
        return HttpResponse(content='None')
    return HttpResponse(content='None')


def speech2text(request):
    # 获取上传的文件
    file = request.FILES.get("file")
    # 保存文件到tmp文件夹
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    with open("tmp/" + file.name, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    # 使用ffmpeg转换pcm格式
    out, _ = (ffmpeg
              .input("tmp/" + file.name)
              .output('-', format='s16le', ac=1, ar=16000)
              .overwrite_output()
              .run(capture_stdout=True)
              )
    res = client.asr(out, 'pcm', 16000, {
        'dev_pid': 1537,
    })

    res_str = "".join(res["result"])
    return HttpResponse(res_str)

