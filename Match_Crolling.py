import requests

import sqlite3
import os
import time
from User_Crolling import User
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler({'apscheduler.timezone':'Asia/seoul'})



def Crolling():
    DB_FILENAME = 'Match2.db'
    DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)

  

    i = 0
    cnt = 1
    match_id = []
    while i < 2500:
        # sqlite와 연결
        conn = sqlite3.connect(DB_FILEPATH)
        cur = conn.cursor()

        # Nexon API Headers
        headers = {'Authorization' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiMTg0OTE3MjMxIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExNDgxIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjUwMDoxMCIsIm5iZiI6MTY0OTg1NDI3MiwiZXhwIjoxNjY1NDA2MjcyLCJpYXQiOjE2NDk4NTQyNzJ9.qE--Kwy2lznUUHyGgZxkR2oZLdHN73VWmzqNbFstDI4'} 

        # Match_ID 받아오는 API 주소
        Match_ID_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/matches?matchtype=50&offset={}&limit=100&orderby=desc'.format(i*100)
        data = requests.get(Match_ID_url, headers=headers)
        match_id = data.json()
        
        # Match 세부 정보를 받아오는 API 주소
        for mi in match_id:
            start = time.time()
            Match_url = f'https://api.nexon.co.kr/fifaonline4/v1.0/matches/{mi}'
            match_data = requests.get(Match_url, headers=headers)

            match = match_data.json()
            if len(match) == 1  or match["matchInfo"][0]["matchDetail"]["matchEndType"] != 0 or len(match["matchInfo"]) < 2 or len(match["matchInfo"][0]["player"]) < 11 or len(match["matchInfo"][1]["player"]) < 11:
                continue

            # Matchs 테이블 데이터 채우기ß
            matchs_data = (match["matchId"], match["matchDate"], match["matchInfo"][0]["matchDetail"]["seasonId"])
            cur.execute('INSERT OR IGNORE INTO Matchs (match_id, match_date, season_id) VALUES (?, ?, ?);', matchs_data)    
            
            # Match_Detail 테이블 데이터 채우기
            match_detail_data = (match["matchId"], match["matchInfo"][0]["accessId"], match["matchInfo"][1]["accessId"])
            cur.execute('INSERT OR IGNORE INTO Match_Detail (match_id, match_home_user_id, match_away_user_id) VALUES (?, ?, ?);', match_detail_data)  
            
            # User 테이블 데이터 채우기
            home_user = match["matchInfo"][0]["accessId"]
            away_user = match["matchInfo"][1]["accessId"]
            User(conn, cur, home_user)
            User(conn, cur, away_user)

            # Match_Home_Users 테이블 데이터 채우기
            match_home_users = (
                                match["matchId"], 
                                match["matchInfo"][0]["matchDetail"]["foul"],
                                match["matchInfo"][0]["matchDetail"]["redCards"],
                                match["matchInfo"][0]["matchDetail"]["yellowCards"],
                                match["matchInfo"][0]["matchDetail"]["dribble"],
                                match["matchInfo"][0]["matchDetail"]["cornerKick"],
                                match["matchInfo"][0]["matchDetail"]["possession"],
                                match["matchInfo"][0]["matchDetail"]["offsideCount"],
                                match["matchInfo"][0]["matchDetail"]["controller"],
                                match["matchInfo"][0]["accessId"],
                                match["matchInfo"][0]["matchDetail"]["matchResult"]
                                )
            cur.execute('''
            INSERT OR IGNORE INTO Match_Home_Users (
                                            match_id, 
                                            foul, 
                                            redcards, 
                                            yellowcards, 
                                            dribble, 
                                            cornerkick, 
                                            possession, 
                                            offsidecount, 
                                            controller, 
                                            match_user_id, 
                                            match_result
                                            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', match_home_users
            ) 

            # Match_Away_Users 테이블 데이터 채우기
            match_away_users = (
                                match["matchId"], 
                                match["matchInfo"][1]["matchDetail"]["foul"],
                                match["matchInfo"][1]["matchDetail"]["redCards"],
                                match["matchInfo"][1]["matchDetail"]["yellowCards"],
                                match["matchInfo"][1]["matchDetail"]["dribble"],
                                match["matchInfo"][1]["matchDetail"]["cornerKick"],
                                match["matchInfo"][1]["matchDetail"]["possession"],
                                match["matchInfo"][1]["matchDetail"]["offsideCount"],
                                match["matchInfo"][1]["matchDetail"]["controller"],
                                match["matchInfo"][1]["accessId"],
                                match["matchInfo"][1]["matchDetail"]["matchResult"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO Match_Away_Users (
                                            match_id, 
                                            foul, 
                                            redcards, 
                                            yellowcards, 
                                            dribble, 
                                            cornerkick, 
                                            possession, 
                                            offsidecount, 
                                            controller, 
                                            match_user_id, 
                                            match_result
                                            )         
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', match_away_users
            )     


            # Home_User_Use_Player 테이블 데이터 수집
            for j in range(len(match["matchInfo"][0]["player"])):
                home_user_use_player = (
                                        match["matchId"],
                                        match["matchInfo"][0]["accessId"],
                                        match["matchInfo"][0]["player"][j]["spId"],
                                        match["matchInfo"][0]["player"][j]["spPosition"],
                                        match["matchInfo"][0]["player"][j]["spGrade"],
                                        match["matchInfo"][0]["player"][j]["status"]["goal"],
                                        match["matchInfo"][0]["player"][j]["status"]["assist"],
                                        match["matchInfo"][0]["player"][j]["status"]["dribble"],
                                        match["matchInfo"][0]["player"][j]["status"]["intercept"],
                                        match["matchInfo"][0]["player"][j]["status"]["defending"],
                                        match["matchInfo"][0]["player"][j]["status"]["passTry"],
                                        match["matchInfo"][0]["player"][j]["status"]["passSuccess"],
                                        match["matchInfo"][0]["player"][j]["status"]["dribbleTry"],
                                        match["matchInfo"][0]["player"][j]["status"]["dribbleSuccess"],
                                        match["matchInfo"][0]["player"][j]["status"]["ballPossesionTry"],
                                        match["matchInfo"][0]["player"][j]["status"]["ballPossesionSuccess"],
                                        match["matchInfo"][0]["player"][j]["status"]["aerialTry"],
                                        match["matchInfo"][0]["player"][j]["status"]["aerialSuccess"],
                                        match["matchInfo"][0]["player"][j]["status"]["blockTry"],
                                        match["matchInfo"][0]["player"][j]["status"]["block"],
                                        match["matchInfo"][0]["player"][j]["status"]["tackleTry"],
                                        match["matchInfo"][0]["player"][j]["status"]["tackle"],
                                        match["matchInfo"][0]["player"][j]["status"]["spRating"]
                                        )
                
                cur.execute('''
                INSERT INTO Home_User_Use_Player (
                                                match_id, 
                                                match_user_id, 
                                                spid, 
                                                sp_position_id, 
                                                sp_grade, 
                                                goal, 
                                                assist, 
                                                dribble, 
                                                intercept, 
                                                defending, 
                                                pass_try,
                                                pass_success,
                                                dribble_try,
                                                dribble_success,
                                                ball_possesion_try,
                                                ball_possesion_success,
                                                aerial_try,
                                                aerial_success,
                                                block_try,
                                                block,
                                                tackle_try,
                                                tackle,
                                                rating
                                                )         
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?);
                ''', home_user_use_player)
                conn.commit()

            for j in range(len(match["matchInfo"][1]["player"])):
                # Away_User_Use_Player 테이블 데이터 수집
                away_user_use_player = (
                                        match["matchId"],
                                        match["matchInfo"][1]["accessId"],
                                        match["matchInfo"][1]["player"][j]["spId"],
                                        match["matchInfo"][1]["player"][j]["spPosition"],
                                        match["matchInfo"][1]["player"][j]["spGrade"],
                                        match["matchInfo"][1]["player"][j]["status"]["goal"],
                                        match["matchInfo"][1]["player"][j]["status"]["assist"],
                                        match["matchInfo"][1]["player"][j]["status"]["dribble"],
                                        match["matchInfo"][1]["player"][j]["status"]["intercept"],
                                        match["matchInfo"][1]["player"][j]["status"]["defending"],
                                        match["matchInfo"][1]["player"][j]["status"]["passTry"],
                                        match["matchInfo"][1]["player"][j]["status"]["passSuccess"],
                                        match["matchInfo"][1]["player"][j]["status"]["dribbleTry"],
                                        match["matchInfo"][1]["player"][j]["status"]["dribbleSuccess"],
                                        match["matchInfo"][1]["player"][j]["status"]["ballPossesionTry"],
                                        match["matchInfo"][1]["player"][j]["status"]["ballPossesionSuccess"],
                                        match["matchInfo"][1]["player"][j]["status"]["aerialTry"],
                                        match["matchInfo"][1]["player"][j]["status"]["aerialSuccess"],
                                        match["matchInfo"][1]["player"][j]["status"]["blockTry"],
                                        match["matchInfo"][1]["player"][j]["status"]["block"],
                                        match["matchInfo"][1]["player"][j]["status"]["tackleTry"],
                                        match["matchInfo"][1]["player"][j]["status"]["tackle"],
                                        match["matchInfo"][1]["player"][j]["status"]["spRating"]
                                        )
                
                cur.execute('''
                INSERT INTO Away_User_Use_Player (
                                                match_id, 
                                                match_user_id, 
                                                spid, 
                                                sp_position_id, 
                                                sp_grade, 
                                                goal, 
                                                assist, 
                                                dribble, 
                                                intercept, 
                                                defending, 
                                                pass_try,
                                                pass_success,
                                                dribble_try,
                                                dribble_success,
                                                ball_possesion_try,
                                                ball_possesion_success,
                                                aerial_try,
                                                aerial_success,
                                                block_try,
                                                block,
                                                tackle_try,
                                                tackle,
                                                rating
                                                )         
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?);
                ''', away_user_use_player)
                conn.commit()
                
            # HT_Shoot_Detail 테이블 데이터 수집
            ht_shoot_detail = (
                                match["matchId"],
                                match["matchInfo"][0]["accessId"], 
                                match["matchInfo"][0]["shoot"]["shootTotal"],
                                match["matchInfo"][0]["shoot"]["effectiveShootTotal"],
                                match["matchInfo"][0]["shoot"]["goalTotal"],
                                match["matchInfo"][0]["shoot"]["shootHeading"],
                                match["matchInfo"][0]["shoot"]["goalHeading"],
                                match["matchInfo"][0]["shoot"]["shootFreekick"],
                                match["matchInfo"][0]["shoot"]["goalFreekick"],
                                match["matchInfo"][0]["shoot"]["shootInPenalty"],
                                match["matchInfo"][0]["shoot"]["goalInPenalty"],
                                match["matchInfo"][0]["shoot"]["shootOutPenalty"],
                                match["matchInfo"][0]["shoot"]["goalOutPenalty"],
                                match["matchInfo"][0]["shoot"]["shootPenaltyKick"],
                                match["matchInfo"][0]["shoot"]["goalPenaltyKick"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO HT_Shoot_Detail (
                                        match_id,
                                        match_user_id,
                                        shoot_total,
                                        effective_shoot_total,
                                        goal_total,
                                        shoot_heading,
                                        goal_heading,
                                        shoot_freekick,
                                        goal_freekick,
                                        shoot_in_penalty,
                                        goal_in_penalty,
                                        shoot_out_penalty,
                                        goal_out_penalty,
                                        shoot_penaltykick,
                                        goal_penaltykick
                                        )         
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', ht_shoot_detail
            )     


            # AT_Shoot_Detail 테이블 데이터 수집
            at_shoot_detail = (
                                match["matchId"],
                                match["matchInfo"][1]["accessId"], 
                                match["matchInfo"][1]["shoot"]["shootTotal"],
                                match["matchInfo"][1]["shoot"]["effectiveShootTotal"],
                                match["matchInfo"][1]["shoot"]["goalTotal"],
                                match["matchInfo"][1]["shoot"]["shootHeading"],
                                match["matchInfo"][1]["shoot"]["goalHeading"],
                                match["matchInfo"][1]["shoot"]["shootFreekick"],
                                match["matchInfo"][1]["shoot"]["goalFreekick"],
                                match["matchInfo"][1]["shoot"]["shootInPenalty"],
                                match["matchInfo"][1]["shoot"]["goalInPenalty"],
                                match["matchInfo"][1]["shoot"]["shootOutPenalty"],
                                match["matchInfo"][1]["shoot"]["goalOutPenalty"],
                                match["matchInfo"][1]["shoot"]["shootPenaltyKick"],
                                match["matchInfo"][1]["shoot"]["goalPenaltyKick"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO AT_Shoot_Detail (
                                        match_id,
                                        match_user_id,
                                        shoot_total,
                                        effective_shoot_total,
                                        goal_total,
                                        shoot_heading,
                                        goal_heading,
                                        shoot_freekick,
                                        goal_freekick,
                                        shoot_in_penalty,
                                        goal_in_penalty,
                                        shoot_out_penalty,
                                        goal_out_penalty,
                                        shoot_penaltykick,
                                        goal_penaltykick
                                        )         
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', at_shoot_detail
            )         


            # HT_Pass_Detail 테이블 데이터 수집
            ht_pass_detail = (
                                match["matchId"],
                                match["matchInfo"][0]["accessId"], 
                                match["matchInfo"][0]["pass"]["passTry"],
                                match["matchInfo"][0]["pass"]["passSuccess"],
                                match["matchInfo"][0]["pass"]["shortPassTry"],
                                match["matchInfo"][0]["pass"]["shortPassSuccess"],
                                match["matchInfo"][0]["pass"]["longPassTry"],
                                match["matchInfo"][0]["pass"]["longPassSuccess"],
                                match["matchInfo"][0]["pass"]["bouncingLobPassTry"],
                                match["matchInfo"][0]["pass"]["bouncingLobPassSuccess"],
                                match["matchInfo"][0]["pass"]["drivenGroundPassTry"],
                                match["matchInfo"][0]["pass"]["drivenGroundPassSuccess"],
                                match["matchInfo"][0]["pass"]["throughPassTry"],
                                match["matchInfo"][0]["pass"]["throughPassSuccess"],
                                match["matchInfo"][0]["pass"]["lobbedThroughPassTry"],
                                match["matchInfo"][0]["pass"]["lobbedThroughPassSuccess"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO HT_Pass_Detail (
                                        match_id,
                                        match_user_id,
                                        pass_try,
                                        pass_success,
                                        shortpass_try,
                                        shortpass_success,
                                        longpass_try,
                                        longpass_success,
                                        bouncinglobpass_try,
                                        bouncinglobpass_success,
                                        drivengroundpass_try,
                                        drivengroundpass_success,
                                        throughpass_try,
                                        throughpass_success,
                                        lobbedthroughpass_try,
                                        lobbedthroughpass_success
                                        )         
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', ht_pass_detail
            )


            # AT_Pass_Detail 테이블 데이터 수집
            at_pass_detail = (
                                match["matchId"],
                                match["matchInfo"][1]["accessId"], 
                                match["matchInfo"][1]["pass"]["passTry"],
                                match["matchInfo"][1]["pass"]["passSuccess"],
                                match["matchInfo"][1]["pass"]["shortPassTry"],
                                match["matchInfo"][1]["pass"]["shortPassSuccess"],
                                match["matchInfo"][1]["pass"]["longPassTry"],
                                match["matchInfo"][1]["pass"]["longPassSuccess"],
                                match["matchInfo"][1]["pass"]["bouncingLobPassTry"],
                                match["matchInfo"][1]["pass"]["bouncingLobPassSuccess"],
                                match["matchInfo"][1]["pass"]["drivenGroundPassTry"],
                                match["matchInfo"][1]["pass"]["drivenGroundPassSuccess"],
                                match["matchInfo"][1]["pass"]["throughPassTry"],
                                match["matchInfo"][1]["pass"]["throughPassSuccess"],
                                match["matchInfo"][1]["pass"]["lobbedThroughPassTry"],
                                match["matchInfo"][1]["pass"]["lobbedThroughPassSuccess"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO AT_Pass_Detail (
                                        match_id,
                                        match_user_id,
                                        pass_try,
                                        pass_success,
                                        shortpass_try,
                                        shortpass_success,
                                        longpass_try,
                                        longpass_success,
                                        bouncinglobpass_try,
                                        bouncinglobpass_success,
                                        drivengroundpass_try,
                                        drivengroundpass_success,
                                        throughpass_try,
                                        throughpass_success,
                                        lobbedthroughpass_try,
                                        lobbedthroughpass_success
                                        )         
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', at_pass_detail
            )

            # HT_Defence_Detail 테이블 데이터 수집
            ht_defence_detail = (
                                match["matchId"],
                                match["matchInfo"][0]["accessId"], 
                                match["matchInfo"][0]["defence"]["blockTry"],
                                match["matchInfo"][0]["defence"]["blockSuccess"],
                                match["matchInfo"][0]["defence"]["tackleTry"],
                                match["matchInfo"][0]["defence"]["tackleSuccess"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO HT_Defence_Detail (
                                        match_id,
                                        match_user_id,
                                        block_try,
                                        block_success,
                                        tackle_try,
                                        tackle_success
                                        )         
            VALUES (?, ?, ?, ?, ?, ?);
            ''', ht_defence_detail
            )


            # AT_Defence_Detail 테이블 데이터 수집
            at_defence_detail = (
                                match["matchId"],
                                match["matchInfo"][1]["accessId"], 
                                match["matchInfo"][1]["defence"]["blockTry"],
                                match["matchInfo"][1]["defence"]["blockSuccess"],
                                match["matchInfo"][1]["defence"]["tackleTry"],
                                match["matchInfo"][1]["defence"]["tackleSuccess"]
                                )

            cur.execute('''
            INSERT OR IGNORE INTO AT_Defence_Detail (
                                        match_id,
                                        match_user_id,
                                        block_try,
                                        block_success,
                                        tackle_try,
                                        tackle_success
                                        )         
            VALUES (?, ?, ?, ?, ?, ?);
            ''', at_defence_detail
            )

            print(f"{cnt}번째 데이터 수집")
            cnt += 1
            end = time.time()
            print(f"{end - start:.2f} sec")
            conn.commit()
            
        i += 1

    conn.close()

scheduler.add_job(func=Crolling, trigger='interval', hours=24, start_date='2022-04-19 09:41:00')
scheduler.start()