import httpx

BASE_URL = "http://127.0.0.1:8000"

def create_user(name: str, email: str):
    try:
        response = httpx.post(f"{BASE_URL}/users/", json={"name": name, "email": email})
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            print(f"User with email {email} already exists.")
            return {"error": "User already exists"}
        else:
            print(f"Error: {e.response.text}")
            return {"error": e.response.text}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

    print("Create user response:", response.json())  # Debug print
    return response.json()

def get_user(user_id: int):
    response = httpx.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    return response.json()

def get_users(skip: int = 0, limit: int = 10):
    response = httpx.get(f"{BASE_URL}/users/", params={"skip": skip, "limit": limit})
    response.raise_for_status()
    return response.json()

def main():
    # 사용자 생성
    try:
        user1_response = create_user(name="John Doe", email="john.doe@example.com")
        if "error" in user1_response:
            print(user1_response["error"])
            user1 = get_users()  # Assuming you want to retrieve the existing user
        else:
            user1 = user1_response
        print("User 1:", user1)
        user1_id = user1['id']
    except Exception as e:
        print("Error creating user 1:", e)
        return

    try:
        user2_response = create_user(name="Jane Smith", email="jane.smith@example.com")
        if "error" in user2_response:
            print(user2_response["error"])
            user2 = get_users()  # Assuming you want to retrieve the existing user
        else:
            user2 = user2_response
        print("User 2:", user2)
    except Exception as e:
        print("Error creating user 2:", e)
        return

    # 사용자 조회
    try:
        user = get_user(user_id=user1_id)
        print("Fetched User:", user)
    except Exception as e:
        print("Error fetching user:", e)

    # 모든 사용자 조회
    try:
        users = get_users()
        print("All Users:", users)
    except Exception as e:
        print("Error fetching users:", e)

if __name__ == "__main__":
    main()
