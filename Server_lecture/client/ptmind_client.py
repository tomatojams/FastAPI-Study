import requests

base_url = "http://127.0.0.1:8000"

def get_items():
    response = requests.get(f"{base_url}/chat/pt/")
    return response.json()
# 출력
def print_items(title, items):
    print(f"\n{title}:\n",items)

data = {'user_id':'a1234', 'user_answer':'안녕하세요'}

def test_create_item():
    # items_before = get_items()
    # print_items("Before POST Request", items_before)

    response = requests.post(f"{base_url}/chat/user/",json=data)
    print("POST Response", response.status_code, response.json())
    # items_after = get_items()
    # print_items("After POST Request", items_after)

test_create_item()