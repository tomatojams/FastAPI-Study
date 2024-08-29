import requests
import json

url = 'http://127.0.0.1:8000/items' # URL 및 엔드포인트
data = {'key':'value'} #전송할 json 데이터

# 요청본문방식
response = requests.post(url, json=data) # POST 요청

print("Status Code:", response.status_code) # 응답 상태코드
print("JSON Response:", response.json()) # 응답 본문