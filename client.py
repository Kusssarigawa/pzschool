import requests
import json
import sys

# Адреси сервісів
URLS = {
    "class": "http://127.0.0.1:8001",
    "teacher": "http://127.0.0.1:8002",
    "schedule": "http://127.0.0.1:8003"
}

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def get_request(service_name, endpoint):
    try:
        res = requests.get(f"{URLS[service_name]}{endpoint}")
        if res.status_code == 200:
            print_json(res.json())
        else:
            print(f"Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Connection Error to {service_name}: {e}")

def create_class():
    name = input("Class Name (e.g. 10-A): ")
    profile = input("Profile (e.g. Math): ")
    data = {"name": name, "profile": profile}
    try:
        res = requests.post(f"{URLS['class']}/classes", json=data)
        print_json(res.json())
    except Exception as e: print(e)

def create_schedule():
    print("\n--- Creating Schedule ---")
    try:
        class_id = int(input("Enter Class ID (must exist in Class Service): "))
        # Спрощені дані для тесту
        data = {
            "classId": class_id,
            "daySchedules": [
                {
                    "dayOfWeek": "Monday",
                    "lessons": [
                        {
                            "subjectName": "Math",
                            "teacherName": "Mr. Smith",
                            "room": "101",
                            "startTime": "09:00",
                            "endTime": "10:30"
                        }
                    ]
                }
            ]
        }
        res = requests.post(f"{URLS['schedule']}/schedules", json=data)
        if res.status_code == 200:
            print("Success! Schedule created.")
            print_json(res.json())
        else:
            print(f"Server Error: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        print("\n--- MICROSERVICES CLIENT ---")
        print("1. [Class Service] List Classes")
        print("2. [Class Service] Create Class")
        print("3. [Teacher Service] List Teachers")
        print("4. [Schedule Service] List Schedules")
        print("5. [Schedule Service] Create Schedule (Will check Class Service!)")
        print("0. Exit")
        
        choice = input("Choice: ")
        
        if choice == '1': get_request('class', '/classes')
        elif choice == '2': create_class()
        elif choice == '3': get_request('teacher', '/teachers')
        elif choice == '4': get_request('schedule', '/schedules')
        elif choice == '5': create_schedule()
        elif choice == '0': sys.exit()

if __name__ == "__main__":
    main()