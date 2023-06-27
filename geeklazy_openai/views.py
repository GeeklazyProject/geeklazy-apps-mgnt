from urllib.parse import urlparse
from urllib.parse import parse_qs
from django.shortcuts import render
from django.http import HttpResponse
import os
import openai
import json

# OPENAI配置
OPENAI_API_KEY = "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"
OPENAI_ORGANIZATION = "org-Pi98XUeBPOOTbFRwq6DFC117"

openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_API_KEY

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"


# Create your views here.
def chat(request):
    # 获取请求参数
    print(request.get_full_path)
    print(request.body)
    parse = urlparse(request.get_full_path())
    query = parse_qs(parse.query)
    body = json.loads(request.body)
    print(body)
    print(query)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": body["question"]}],
    )

    print(completion.choices[0].message.content)
    return HttpResponse(content=completion.choices[0].message.content)
