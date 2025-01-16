https runserver command : py manage.py runsslserver --certificate C:\Users\xbit\cert.pem --key C:\Users\xbit\key.pem 0.0.0.0:8000
for websocket runserver :daphne -b 192.168.150.18 -p 4000 core.asgi:application

for websocket runserver :daphne -p 8000 core.asgi:application


GET /api/chat/search-user/?query=john HTTP/1.1
Host: 192.168.186.112:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MzQxOTY1LCJpYXQiOjE3MzQzMzgzNjUsImp0aSI6Ijc4MDYxOTRjMzExYzRhYTJiNGM3MjMzZjczMjY0YTdjIiwidXNlcl9pZCI6Mn0.daNKDjTBVJUIFYAyEZL0jKi5FYsui5dtB-L9wTHRolw
Connection: close