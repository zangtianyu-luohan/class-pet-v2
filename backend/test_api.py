import requests

BASE = "http://localhost:8000"

# 登录
r = requests.post(f"{BASE}/api/auth/login", json={"username": "demo", "password": "1234"})
print("Login:", r.status_code, r.json().get("user", {}).get("display_name"))
token = r.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 测试 /me
r2 = requests.get(f"{BASE}/api/auth/me", headers=headers)
print("Me:", r2.status_code, r2.json())

# 创建班级
r3 = requests.post(f"{BASE}/api/classes/", json={"name": "三年级一班", "description": "演示班级"}, headers=headers)
print("Create class:", r3.status_code, r3.json())

# 获取班级列表
r4 = requests.get(f"{BASE}/api/classes/", headers=headers)
print("List classes:", r4.status_code, r4.json())
