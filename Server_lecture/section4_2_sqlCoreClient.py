import requests
BASE_URL = 'http://127.0.0.1:8000/users'

def get_users():
    response = requests.get(BASE_URL)
    return response.json()

def create_user(name,age):
    response = requests.post(BASE_URL +"/", json={'name': name, 'age': age})
    return response.json()

def get_user(user_id):
    response = requests.get(BASE_URL +"/" + str(user_id))
    return response.json()

def update_user(user_id,name,age):
    response = requests.put(BASE_URL +"/" + str(user_id), json={'name': name, 'age': age})
    return response.json()

def delete_user(user_id):
    response = requests.delete(BASE_URL +"/" + str(user_id))
    return response.json()

#예시
print("Get users:",get_users())
new_user = create_user('John','18')
print("Create user:",new_user)
user_id = new_user['id']
print("Update user:",update_user(user_id,"John updated",30))
print("Delete user:",delete_user(user_id))