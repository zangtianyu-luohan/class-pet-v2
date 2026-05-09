from jose import jwt
from app.config import settings

# 测试 token 解码
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIsImV4cCI6MTc3ODkzNzQwM30.wZJLqJUnlQfF4Q-IsWPbn7AoCyRz43t3Q8Vv0cRQFU8"

print("SECRET_KEY:", repr(settings.SECRET_KEY))
print("ALGORITHM:", settings.ALGORITHM)

try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print("Decoded:", payload)
except Exception as e:
    print("Error:", e)
