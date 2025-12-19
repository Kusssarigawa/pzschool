import requests
import json
import sys

# Адрес API Gateway
GATEWAY_URL = "http://127.0.0.1:8080"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def get_request(endpoint):
    try:
        res = requests.get(f"{GATEWAY_URL}{endpoint}")
        if res.status_code == 200:
            print_json(res.json())
        else:
            print(f"Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

# --- NEW FUNCTION: CREATE CLASS ---
def create_class():
    print("\n--- Create Class (via Gateway) ---")
    try:
        # ID більше не питаємо!
        
        name = input("Enter Class Name (e.g. 9-B): ").strip()
        profile = input("Enter Profile (e.g. Math, Bio): ").strip()
        
        data = {
            "id": 0, # Відправляємо 0, сервер сам видасть правильний ID
            "name": name,
            "profile": profile
        }
        
        res = requests.post(f"{GATEWAY_URL}/classes", json=data)
        
        if res.status_code == 200:
            print("[SUCCESS] Class created!")
            print_json(res.json())
        else:
            print(f"[ERROR] Server returned {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"[ERROR] {e}")
    print("\n--- Create Class (via Gateway) ---")
    try:
        # 1. Вводим ID
        c_id = input("Enter Class ID (e.g. 3): ").strip()
        if not c_id.isdigit():
            print("Error: ID must be a number.")
            return
            
        # 2. Вводим данные
        name = input("Enter Class Name (e.g. 9-B): ").strip()
        profile = input("Enter Profile (e.g. Math, Bio): ").strip()
        
        data = {
            "id": int(c_id),
            "name": name,
            "profile": profile
        }
        
        # 3. Отправляем через Gateway на class-service
        res = requests.post(f"{GATEWAY_URL}/classes", json=data)
        
        if res.status_code == 200:
            print("[SUCCESS] Class created!")
            print_json(res.json())
        else:
            print(f"[ERROR] Server returned {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"[ERROR] {e}")

def create_teacher():
    print("\n--- Create Teacher (via Gateway) ---")
    try:
        # ID більше не питаємо!
            
        name = input("Enter Full Name (e.g. Mr. White): ").strip()
        subject = input("Enter Subject (e.g. Chemistry): ").strip()
        
        data = {
            "id": 0, # Відправляємо 0, сервер сам видасть правильний ID
            "fullName": name,
            "subject": subject
        }
        
        res = requests.post(f"{GATEWAY_URL}/teachers", json=data)
        
        if res.status_code == 200:
            print("[SUCCESS] Teacher created!")
            print_json(res.json())
        else:
            print(f"[ERROR] Server returned {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"[ERROR] {e}")
    print("\n--- Create Teacher (via Gateway) ---")
    try:
        t_id = input("Enter Teacher ID: ").strip()
        if not t_id.isdigit():
            print("Error: ID must be a number.")
            return
            
        name = input("Enter Full Name (e.g. Mr. White): ").strip()
        subject = input("Enter Subject (e.g. Chemistry): ").strip()
        
        data = {
            "id": int(t_id),
            "fullName": name,
            "subject": subject
        }
        
        res = requests.post(f"{GATEWAY_URL}/teachers", json=data)
        
        if res.status_code == 200:
            print("[SUCCESS] Teacher created!")
            print_json(res.json())
        else:
            print(f"[ERROR] Server returned {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"[ERROR] {e}")

def create_schedule():
    print("\n--- Create Schedule (via Gateway) ---")
    try:
        class_id_str = input("Enter Class ID (must exist!): ").strip()
        if not class_id_str.isdigit():
            print("Error: ID must be a number.")
            return
        class_id = int(class_id_str)

        day = input("Enter Day of Week (e.g. Monday): ").strip()
        lessons_str = input("Enter Lessons (comma separated): ")
        lessons_list = [l.strip() for l in lessons_str.split(",") if l.strip()]

        data = {
            "classId": class_id,
            "day": day,
            "lessons": lessons_list
        }
        
        print(f"Sending data to Gateway: {data}")

        res = requests.post(f"{GATEWAY_URL}/schedules", json=data)
        
        if res.status_code == 200:
            print("[SUCCESS] Schedule created!")
            print("Response from server:")
            print_json(res.json())
        else:
            print(f"[ERROR] Server returned {res.status_code}")
            print(res.text)

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

def main():
    while True:
        print("\n--- SCHOOL SYSTEM (GATEWAY 8080) ---")
        print("1. List Classes (/classes)")
        print("2. List Teachers (/teachers)")
        print("3. List Schedules (/schedules)")
        print("4. Create Schedule (Checks Class Service via Discovery!)")
        print("5. Create Teacher") 
        print("6. Create Class ")  # <--- Добавили
        print("0. Exit")
        
        choice = input("Choice: ")
        
        if choice == '1': get_request('/classes')
        elif choice == '2': get_request('/teachers')
        elif choice == '3': get_request('/schedules')
        elif choice == '4': create_schedule()
        elif choice == '5': create_teacher()
        elif choice == '6': create_class() # <--- Вызов
        elif choice == '0': sys.exit()

if __name__ == "__main__":
    main()