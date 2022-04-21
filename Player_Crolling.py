import requests
import sqlite3
import psycopg2
import os


DB_FILENAME = 'Match.db'
DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)


# DB서버 주소
host = 'rajje.db.elephantsql.com'
user = 'wmqgbotr'
database = 'wmqgbotr'
password = 'd3BVueTS7Y2xTYAFPEIZBcb9YwQ1Fhni'

# DB-API
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# sqlite와 연결
conn = sqlite3.connect(DB_FILEPATH)
cur = conn.cursor()

# Nexon API Headers
headers = {'Authorization' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiMTg0OTE3MjMxIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExNDgxIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjUwMDoxMCIsIm5iZiI6MTY0OTg1NDI3MiwiZXhwIjoxNjY1NDA2MjcyLCJpYXQiOjE2NDk4NTQyNzJ9.qE--Kwy2lznUUHyGgZxkR2oZLdHN73VWmzqNbFstDI4'} 
player_url = "https://static.api.nexon.co.kr/fifaonline4/latest/spid.json"
data = requests.get(player_url, headers=headers)
player = data.json()
for p in player:
    sp = (p["id"], p["name"], p["id"]//1000000)
    cur.execute('INSERT OR IGNORE INTO Player (spid, name, season_class_id) VALUES (?, ?, ?)', sp)

conn.commit()
conn.close()