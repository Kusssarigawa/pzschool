import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def menu():
    print("\n--- CLIENT MENU ---")
    print("1. [GET] Отримати всі розклади")
    print("2. [GET] Отримати розклади з фільтром (Query Param)")
    print("3. [GET] Отримати за ID")
    print("4. [POST] Створити новий розклад")
    print("5. [PUT] Оновити розклад")
    print("6. [DELETE] Видалити розклад")
    print("7. [GET] Sub-resource: Отримати дні розкладу")
    print("0. Вихід")

def main():
    while True:
        menu()
        choice = input("Ваш вибір: ")
        
        try:
            if choice == '1':
                res = requests.get(f"{BASE_URL}/schedules")
                print_json(res.json())

            elif choice == '2':
                c_name = input("Введіть назву класу для пошуку (напр. 10A): ")
                # Вимога: фільтрація через Query Parameters 
                res = requests.get(f"{BASE_URL}/schedules", params={"class_name": c_name})
                print_json(res.json())

            elif choice == '3':
                sid = input("ID: ")
                res = requests.get(f"{BASE_URL}/schedules/{sid}")
                if res.status_code == 200:
                    print_json(res.json())
                else:
                    print(f"Error: {res.status_code} - {res.text}")

            elif choice == '4':
                sid = int(input("Новий ID: "))
                cname = input("Клас: ")
                data = {
                    "id": sid,
                    "className": cname,
                    "daySchedules": []
                }
                res = requests.post(f"{BASE_URL}/schedules", json=data)
                print(f"Status: {res.status_code}")
                print_json(res.json())

            elif choice == '5':
                sid = int(input("ID для оновлення: "))
                new_name = input("Нова назва класу: ")
                data = {
                    "id": sid,
                    "className": new_name,
                    "profile": "Updated Profile",
                    "daySchedules": []
                }
                # Вимога: HTTP PUT 
                res = requests.put(f"{BASE_URL}/schedules/{sid}", json=data)
                print(f"Status: {res.status_code}")
                if res.status_code == 200:
                    print_json(res.json())
                else:
                    print(res.text)

            elif choice == '6':
                sid = input("ID для видалення: ")
                # Вимога: HTTP DELETE 
                res = requests.delete(f"{BASE_URL}/schedules/{sid}")
                print(f"Status: {res.status_code}")
                print_json(res.json())

            elif choice == '7':
                sid = input("ID розкладу: ")
                # Вимога: Sub-resource 
                res = requests.get(f"{BASE_URL}/schedules/{sid}/days")
                if res.status_code == 200:
                    print_json(res.json())
                else:
                    print(res.text)

            elif choice == '0':
                break
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    main()