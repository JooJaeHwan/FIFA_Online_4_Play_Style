import sqlite3
import os

DB_FILENAME = 'Match2.db'
DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)

DB_FILEPATH2 = os.path.join(os.getcwd(), "User.db")
conn2 = sqlite3.connect(DB_FILEPATH2)
cur2 = conn2.cursor()

conn = sqlite3.connect(DB_FILEPATH)
cur = conn.cursor()


# Match 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Matchs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    match_id VARCHAR,
    match_date VARCHAR,
    season_id INTEGER
    
);
''')

# Match 세부사항 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Match_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_home_user_id VARCHAR,
    match_away_user_id VARCHAR,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')


# Match_Home_Users 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Match_Home_Users (
    match_id VARCHAR NOT NULL PRIMARY KEY,
    foul INTEGER,
    redcards INTEGER,
    yellowcards INTEGER,
    dribble INTEGER,
    cornerkick INTEGER,
    possession INTEGER,
    offsidecount INTEGER,
    controller VARCHAR,
    match_user_id VARCHAR,
    match_result VARCHAR,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# Match_Away_Users 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Match_Away_Users (
    match_id VARCHAR NOT NULL PRIMARY KEY,
    foul INTEGER,
    redcards INTEGER,
    yellowcards INTEGER,
    dribble INTEGER,
    cornerkick INTEGER,
    possession INTEGER,
    offsidecount INTEGER,
    controller VARCHAR,
    match_user_id VARCHAR,
    match_result VARCHAR,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')


# Home_Player가 사용하는 선수 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Home_User_Use_Player (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    match_id VARCHAR,
    match_user_id VARCHAR,
    spid INTEGER,
    sp_position_id INTEGER,
    sp_grade INTEGER,
    goal INTEGER,
    assist INTEGER,
    dribble INTEGER,
    intercept INTEGER,
    defending INTEGER,
    pass_try INTEGER,
    pass_success INTEGER,
    dribble_try INTEGER,
    dribble_success INTEGER,
    ball_possesion_try INTEGER,
    ball_possesion_success INTEGER,
    aerial_try INTEGER,
    aerial_success INTEGER,
    block_try INTEGER,
    block INTEGER,
    tackle_try INTEGER,
    tackle INTEGER,
    rating FLOAT,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# Away_Player가 사용하는 선수 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Away_User_Use_Player (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    match_id VARCHAR,
    match_user_id VARCHAR,
    spid INTEGER,
    sp_position_id INTEGER,
    sp_grade INTEGER,
    goal INTEGER,
    assist INTEGER,
    dribble INTEGER,
    intercept INTEGER,
    defending INTEGER,
    pass_try INTEGER,
    pass_success INTEGER,
    dribble_try INTEGER,
    dribble_success INTEGER,
    ball_possesion_try INTEGER,
    ball_possesion_success INTEGER,
    aerial_try INTEGER,
    aerial_success INTEGER,
    block_try INTEGER,
    block INTEGER,
    tackle_try INTEGER,
    tackle INTEGER,
    rating FLOAT,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# 선수 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Player (
    spid INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR,
    season_class_id INTEGER,
    FOREIGN KEY (spid) REFERENCES Home_User_Use_Player(spid),
    FOREIGN KEY (spid) REFERENCES Away_User_Use_Player(spid)
);
''')

# 선수 시즌 클래스 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Season_Class (
    id INTEGER NOT NULL PRIMARY KEY,
    class_name VARCHAR,
    FOREIGN KEY (id) REFERENCES Player(season_class_id)
);
''')

# 유저 테이블 만들기
cur2.execute('''
CREATE TABLE IF NOT EXISTS User (
    id VARCHAR NOT NULL PRIMARY KEY,
    nickname VARCHAR,
    division_id INTEGER,
    FOREIGN KEY (id) REFERENCES Match_Detail(match_home_user_id)
    FOREIGN KEY (id) REFERENCES Match_Detail(match_away_user_id)
);
''')


# 등급 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Division (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR,
    FOREIGN KEY (id) REFERENCES User(division_id)
);
''')

# 포지션 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS Position (
    sp_position_id INTEGER NOT NULL PRIMARY KEY,
    position VARCHAR,
    FOREIGN KEY (sp_position_id) REFERENCES Home_User_Use_Player(sp_position_id),
    FOREIGN KEY (sp_position_id) REFERENCES Away_User_Use_Player(sp_position_id)
);
''')

# 홈팀 슛 세부정보 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS HT_Shoot_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_user_id VARCHAR NOT NULL,  
    shoot_total INTEGER,
    effective_shoot_total INTEGER,
    goal_total INTEGER,
    shoot_heading INTEGER,
    goal_heading INTEGER,
    shoot_freekick INTEGER,
    goal_freekick INTEGER,
    shoot_in_penalty INTEGER,
    goal_in_penalty INTEGER,
    shoot_out_penalty INTEGER,
    goal_out_penalty INTEGER,
    shoot_penaltykick INTEGER,
    goal_penaltykick INTEGER,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# 원정팀 슛 세부정보 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS AT_Shoot_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_user_id VARCHAR NOT NULL,  
    shoot_total INTEGER,
    effective_shoot_total INTEGER,
    goal_total INTEGER,
    shoot_heading INTEGER,
    goal_heading INTEGER,
    shoot_freekick INTEGER,
    goal_freekick INTEGER,
    shoot_in_penalty INTEGER,
    goal_in_penalty INTEGER,
    shoot_out_penalty INTEGER,
    goal_out_penalty INTEGER,
    shoot_penaltykick INTEGER,
    goal_penaltykick INTEGER,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# 홈팀 패스 세부정보 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS HT_Pass_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_user_id VARCHAR NOT NULL,  
    pass_try INTEGER,
    pass_success INTEGER,
    shortpass_try INTEGER,
    shortpass_success INTEGER,
    longpass_try INTEGER,
    longpass_success INTEGER,
    bouncinglobpass_try INTEGER,
    bouncinglobpass_success INTEGER,
    drivengroundpass_try INTEGER,
    drivengroundpass_success INTEGER,
    throughpass_try INTEGER,
    throughpass_success INTEGER,
    lobbedthroughpass_try INTEGER,
    lobbedthroughpass_success INTEGER,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# 원정팀 패스 세부정보 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS AT_Pass_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_user_id VARCHAR NOT NULL,  
    pass_try INTEGER,
    pass_success INTEGER,
    shortpass_try INTEGER,
    shortpass_success INTEGER,
    longpass_try INTEGER,
    longpass_success INTEGER,
    bouncinglobpass_try INTEGER,
    bouncinglobpass_success INTEGER,
    drivengroundpass_try INTEGER,
    drivengroundpass_success INTEGER,
    throughpass_try INTEGER,
    throughpass_success INTEGER,
    lobbedthroughpass_try INTEGER,
    lobbedthroughpass_success INTEGER,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')

# 홈팀_수비 세부정보 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS HT_Defence_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_user_id VARCHAR NOT NULL,  
    block_try INTEGER,
    block_success INTEGER,
    tackle_try INTEGER,
    tackle_success INTEGER,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')


# 원정팀_수비 세부정보 테이블 만들기
cur.execute('''
CREATE TABLE IF NOT EXISTS AT_Defence_Detail (
    match_id VARCHAR NOT NULL PRIMARY KEY, 
    match_user_id VARCHAR NOT NULL,  
    block_try INTEGER,
    block_success INTEGER,
    tackle_try INTEGER,
    tackle_success INTEGER,
    FOREIGN KEY (match_id) REFERENCES Matchs(match_id)
);
''')