import requests
def User(conn, cur, user):
    # Nexon API Headers
    headers = {'Authorization' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiMTg0OTE3MjMxIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExNDgxIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjUwMDoxMCIsIm5iZiI6MTY0OTg1NDI3MiwiZXhwIjoxNjY1NDA2MjcyLCJpYXQiOjE2NDk4NTQyNzJ9.qE--Kwy2lznUUHyGgZxkR2oZLdHN73VWmzqNbFstDI4'} 
    user_url =f"https://api.nexon.co.kr/fifaonline4/v1.0/users/{user}"
    division_url = f"https://api.nexon.co.kr/fifaonline4/v1.0/users/{user}/maxdivision"
    user_data = requests.get(user_url, headers=headers)
    division_data = requests.get(division_url, headers=headers)
    user_ = user_data.json()
    division = division_data.json()
    for d in division:
        if d["matchType"] != 50:
            continue
        user = (user_["accessId"], user_["nickname"], d["division"])
        cur.execute('INSERT OR IGNORE INTO User (id, nickname, division_id) VALUES (?, ?, ?)', user)