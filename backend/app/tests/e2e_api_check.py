import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_e2e():
    print("Starting E2E API Check...")
    
    with httpx.Client(timeout=10.0) as client:
        # 1. Login
        print("Testing Login...")
        try:
            login_res = client.post(
                f"{BASE_URL}/auth/login",
                data={"username": "admin@school.com", "password": "admin"}
            )
            if login_res.status_code != 200:
                print(f"Login failed: {login_res.text}")
                return
            
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Login Successful.")

            # 2. Check New Endpoints
            endpoints = [
                "/leaves/",
                "/feedbacks/",
                "/quizzes/",
                "/salaries/salaries",
                "/assets/"
            ]

            for ep in endpoints:
                print(f"Checking {ep}...")
                res = client.get(f"{BASE_URL}{ep}", headers=headers)
                if res.status_code == 200:
                    print(f"  [OK] {ep}")
                else:
                    print(f"  [FAILED] {ep} - Status: {res.status_code}")
            
            print("\nE2E API Check Completed.")

        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    test_e2e()
