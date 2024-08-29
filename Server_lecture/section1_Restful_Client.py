import requests

base_url = "http://127.0.0.1:8000"

# 아이템 목록 조회
def get_items():
    response = requests.get(f"{base_url}/items")
    return response.json()
# 출력
def print_items(title, items):
    print(f"\n{title}:\n",items)

# Get 요청 테스트

def test_get_items():
    items_before = get_items()
    print_items("Before GET Request", items_before)

    response = requests.get(f"{base_url}/items")
    print("GET Response", response.status_code, response.json())

    items_after = get_items()
    print_items("After GET Request", items_after)

# Post 요청 테스트

def test_create_item():
    items_before = get_items()
    print_items("Before POST Request", items_before)

    response = requests.post(f"{base_url}/items/3", data={"name":"Notebook"})
    print("POST Response", response.status_code, response.json())

    items_after = get_items()
    print_items("After POST Request", items_after)

# Put 요청 테스트

def test_update_item():
    items_before = get_items()
    print_items("Before PUT Request", items_before)

    response = requests.put(f"{base_url}/items/3", data={"name":"Laptop"})
    print("PUT Response", response.status_code, response.json())

    items_after = get_items()
    print_items("After PUT Request", items_after)

# Delete 요청 테스트
def test_delete_item():
    items_before = get_items()
    print_items("Before DELETE Request", items_before)

    response = requests.delete(f"{base_url}/items/2")
    print("DELETE Response", response.status_code, response.json())

    items_after = get_items()
    print_items("After DELETE Request", items_after)

# Patch 요청 테스트
def test_patch_item():
    items_before = get_items()
    print_items("Before PATCH Request", items_before)

    response = requests.patch(f"{base_url}/items/3", data={"name":"Tablet"})
    print("PATCH Response", response.status_code, response.json())

    items_after = get_items()
    print_items("After PATCH Request", items_after)


test_get_items()
test_create_item()
test_update_item()
test_delete_item()
test_patch_item()