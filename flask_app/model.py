import sqlite3
import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier 
from category_encoders import TargetEncoder
from sklearn.pipeline import make_pipeline
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler({'apscheduler.timezone':'Asia/seoul'})

db_list = [d for d in os.listdir() if ".db" in d]
table_data = []
table_data_2 = []
table_data_3 = []
table_data_4 = []
user_data =[]


for db in db_list:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        sql = """
        SELECT * 
        FROM Home_User_Use_Player h
        JOIN Player p ON h.spid = p.spid
        JOIN Position ps ON h.sp_position_id = ps.sp_position_id
        JOIN Season_Class s ON p.season_class_id = s.id
        WHERE h.sp_position_id != 28;
        """
        cursor.execute(sql)
        table_data += cursor.fetchall()

        sql = """
        SELECT * 
        FROM Away_User_Use_Player a
        JOIN Player p ON a.spid = p.spid
        JOIN Position ps ON a.sp_position_id = ps.sp_position_id
        JOIN Season_Class s ON p.season_class_id = s.id
        WHERE a.sp_position_id != 28;
        """
        cursor.execute(sql)
        table_data_2 += cursor.fetchall()

        sql = """
        SELECT * 
        FROM Match_Home_Users mhu
        JOIN Matchs m USING (match_id)
        JOIN HT_Shoot_Detail hsd USING (match_id)
        JOIN HT_Pass_Detail hpd USING (match_id)
        JOIN HT_Defence_Detail hdd USING (match_id)
        WHERE mhu.match_result != "무";
        """
        cursor.execute(sql)
        table_data_3 += cursor.fetchall()

        sql = """
        SELECT * 
        FROM Match_Away_Users mau
        JOIN Matchs m USING (match_id)
        JOIN AT_Shoot_Detail asd USING (match_id)
        JOIN AT_Pass_Detail apd USING (match_id)
        JOIN AT_Defence_Detail ad USING (match_id)
        WHERE mau.match_result != "무";
        """
        cursor.execute(sql)
        table_data_4 += cursor.fetchall()
        
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        sql = """
        SELECT u.id, u.nickname 
        FROM User u
        """
        cursor.execute(sql)
        user_data += cursor.fetchall()



column = ["id","match_id", "match_user_id", "spid", "sp_position_id", "sp_grade", 
        "goal", "assist", "dribble", "intercept", "defending", "pass_try", "pass_success", 
        "dribble_try", "dribble_success", "ball_possesion_try", "ball_possesion_success", "aerial_try", 
        "aerial_success", "block_try", "block", "tackle_try", "tackle", "rating", "p_spid", "name", 
        "season_class_id", "ps_position_id", "position", "s_id", "class_name"] 

Home_User_Use_Player = pd.DataFrame(table_data, columns=column)
Home_User_Use_Player.drop(["id", "p_spid", "ps_position_id", "s_id"], axis=1, inplace=True)
Away_User_Use_Player = pd.DataFrame(table_data_2,columns=column)
Away_User_Use_Player.drop(["id", "p_spid", "ps_position_id", "s_id"], axis=1, inplace=True)
User_Use_Player = pd.concat([Home_User_Use_Player, Away_User_Use_Player])
User_Use_Player["name"] = User_Use_Player["class_name"] + User_Use_Player["name"]
User_Use_Player.drop(["spid", "sp_position_id", "season_class_id", "class_name"], axis=1, inplace=True)
User_Use_Player.reset_index(drop=True, inplace=True)


column_2 = ["match_id", "foul", "redcards", "yellowcards", "dribble", "cornerkick", "possession", "offsidecount", "controller", 
        "match_user_id", "match_result", "id", "match_date", "season_id", "hsd_match_user_id", "shoot_total", 
        "effective_shoot_total", "goal_total", "shoot_heading", "goal_heading", "shoot_freekick", "goal_freekick", "shoot_in_penalty",
        "goal_in_penalty", "shoot_out_penalty", "goal_out_penalty", "shoot_penaltykick", "goal_penaltykick", "hpd_match_user_id",
        "pass_try", "pass_success", "shortpass_try", "shortpass_success", "longpass_try", "longpass_success", "bouncinglobpass_try",
        "bouncinglobpass_success", "drivengroundpass_try", "drivengroundpass_success", "throughpass_try", "throughpass_success",
        "lobbedthroughpass_try", "lobbedthroughpass_success", "hdd_match_user_id", "block_try", "block_success", "tackle_try", "tackle_success"]

Home_Match = pd.DataFrame(table_data_3, columns=column_2)
Home_Match.drop(["id","hsd_match_user_id", "hpd_match_user_id","hdd_match_user_id"], axis=1, inplace=True)
Away_Match = pd.DataFrame(table_data_4, columns=column_2)
Away_Match.drop(["id","hsd_match_user_id", "hpd_match_user_id","hdd_match_user_id"], axis=1, inplace=True)

Match = pd.concat([Home_Match, Away_Match])
Match.reset_index(drop=True, inplace=True)

Match["shoot_heading_per"] = round(Match["shoot_heading"]/Match["shoot_total"] * 100, 2) # 헤딩 슛 비율
Match["goal_heading_per"] = round(Match["goal_heading"]/Match["goal_total"] * 100, 2) # 헤딩 골 비율
Match["shoot_out_penalty_per"] = round(Match["shoot_out_penalty"]/Match["shoot_total"]*100, 2) # 중거리 슈팅 비율
Match["goal_out_penalty_per"] = round(Match["goal_out_penalty"]/Match["goal_total"]*100, 2) # 중거리 골 비율
Match["field_shoot"] = Match["shoot_total"] - Match["shoot_freekick"] - Match["shoot_penaltykick"] # 필드 슈팅
Match["field_goal"] = Match["goal_total"] - Match["goal_freekick"] - Match["goal_penaltykick"] # 필드 골
Match = Match.fillna(0)

match_rating_max = User_Use_Player.loc[User_Use_Player.groupby(["match_id", "match_user_id"])["rating"].idxmax()]
match_rating_max = match_rating_max[["match_id", "match_user_id", "name", "position"]]
match_rating_max.rename(columns={"name" : "max_rating_player", "position" : "max_rating_player_position"}, inplace=True)

match_goal_max = User_Use_Player.loc[User_Use_Player.groupby(["match_id", "match_user_id"])["goal"].idxmax()]
match_goal_max = match_goal_max[["match_id", "match_user_id", "name", "position"]]
match_goal_max.rename(columns={"name" : "max_goal_player", "position" : "max_goal_player_position"}, inplace=True)

match_assist_max = User_Use_Player.loc[User_Use_Player.groupby(["match_id", "match_user_id"])["assist"].idxmax()]
match_assist_max = match_assist_max[["match_id", "match_user_id", "name", "position"]]
match_assist_max.rename(columns={"name" : "max_assist_player", "position" : "max_assist_player_position"}, inplace=True)

match_intercept_max = User_Use_Player.loc[User_Use_Player.groupby(["match_id", "match_user_id"])["intercept"].idxmax()]
match_intercept_max = match_intercept_max[["match_id", "match_user_id", "name", "position"]]
match_intercept_max.rename(columns={"name" : "max_intercept_player", "position" : "max_intercept_player_position"}, inplace=True)

match_defending_max = User_Use_Player.loc[User_Use_Player.groupby(["match_id", "match_user_id"])["defending"].idxmax()]
match_defending_max = match_defending_max[["match_id", "match_user_id", "name", "position"]]
match_defending_max.rename(columns={"name" : "max_defending_player", "position" : "max_defending_player_position"}, inplace=True)

match_pass_max = User_Use_Player.loc[User_Use_Player.groupby(["match_id", "match_user_id"])["pass_try"].idxmax()]
match_pass_max = match_pass_max[["match_id", "match_user_id", "name", "position"]]
match_pass_max.rename(columns={"name" : "max_pass_player", "position" : "max_pass_player_position"}, inplace=True)

match_sum = User_Use_Player.groupby(["match_id", "match_user_id"])[["assist", "intercept", "defending"]].sum()
match_sum.reset_index(inplace=True)

Match_merge = pd.merge(Match, match_sum, how="inner", on=["match_id", "match_user_id"])
Match_merge = pd.merge(Match_merge, match_rating_max, how="inner", on=["match_id", "match_user_id"])
Match_merge = pd.merge(Match_merge, match_goal_max, how="inner", on=["match_id", "match_user_id"])
Match_merge = pd.merge(Match_merge, match_assist_max, how="inner", on=["match_id", "match_user_id"])
Match_merge = pd.merge(Match_merge, match_defending_max, how="inner", on=["match_id", "match_user_id"])
Match_merge = pd.merge(Match_merge, match_intercept_max, how="inner", on=["match_id", "match_user_id"])
Match_merge = pd.merge(Match_merge, match_pass_max, how="inner", on=["match_id", "match_user_id"])
Match_merge.reset_index(drop=True, inplace=True)

Match_merge.loc[(Match_merge["shoot_heading_per"] >= 60) & (Match_merge["max_assist_player_position"].str.contains("L")) | (Match_merge["max_assist_player_position"].str.contains("R")), "Play_Style"] = 1 # 철퇴 축구
Match_merge.loc[(Match_merge["lobbedthroughpass_try"]>=10) | (Match_merge["throughpass_try"]>20), "Play_Style"] = 2 # 침투 축구
Match_merge.loc[(Match_merge["possession"] < 40) & ((Match_merge["max_goal_player_position"].str.contains("S")) | (Match_merge["max_goal_player_position"].str.contains("LW")) | (Match_merge["max_goal_player_position"].str.contains("RW"))) & (Match_merge["max_goal_player_position"] != "SW"), "Play_Style"] = 3 # 역습 축구
Match_merge.loc[Match_merge["shortpass_try"]>=90, "Play_Style"] = 4 # 티키타카
Match_merge.loc[((Match_merge["max_defending_player_position"].str.contains("F"))| (Match_merge["max_defending_player_position"].str.contains("S")) | (Match_merge["max_defending_player_position"].str.contains("LW")) | (Match_merge["max_defending_player_position"].str.contains("RW"))) & (Match_merge["max_defending_player_position"] != "SW") | 
                ((Match_merge["max_intercept_player_position"].str.contains("F"))| (Match_merge["max_intercept_player_position"].str.contains("S")) | (Match_merge["max_intercept_player_position"].str.contains("LW")) | (Match_merge["max_intercept_player_position"].str.contains("RW"))) & (Match_merge["max_intercept_player_position"] != "SW"), "Play_Style"] = 5 # 압박축구
Match_merge.loc[(Match_merge["max_assist_player_position"].str.contains("L")) & (Match_merge["max_assist_player_position"] != "LF") & (Match_merge["max_assist_player_position"] != "LS") | (Match_merge["max_assist_player_position"].str.contains("R")) & (Match_merge["max_assist_player_position"] != "RF") & (Match_merge["max_assist_player_position"] != "RS"), "Play_Style"] = 6 # 측면 공략 공격
Match_merge.loc[(Match_merge["max_goal_player_position"].str.contains("M")) & (Match_merge["max_assist_player_position"].str.contains("M")), "Play_Style"] = 7 # 2선활용공격
Match_merge.loc[(Match_merge["max_goal_player_position"].str.contains("C")) & (Match_merge["max_assist_player_position"].str.contains("C")), "Play_Style"] = 8 # 중앙 공략 공격
Match_merge.loc[(Match_merge["max_pass_player_position"].str.contains("CM")) & (Match_merge["max_pass_player_position"].str.contains("CDM")), "Play_Style"] = 9 # 중앙 관제탑 미드필더
Match_merge.fillna(0, inplace=True) # 평범한 축구
Match_merge["Play_Style"] = Match_merge.Play_Style.astype("int64")


train, test = train_test_split(Match_merge, train_size=0.8, random_state=42)
train, val = train_test_split(train, train_size=0.8, random_state=42)

target = "Play_Style"
features = train.drop(columns=[target, "match_id","match_user_id", 'max_rating_player',
       'max_rating_player_position', 'max_goal_player',
       'max_goal_player_position', 'max_assist_player',
       'max_assist_player_position', 'max_defending_player',
       'max_defending_player_position', 'max_intercept_player',
       'max_intercept_player_position', 'max_pass_player',
       'max_pass_player_position', 'throughpass_try', 'shortpass_try']).columns

X_train = train[features]
y_train = train[target]
X_val = val[features]
y_val = val[target]
X_test = test[features]
y_test = test[target]
pipe = Pipeline([
    ('preprocessing', make_pipeline(TargetEncoder(), SimpleImputer(strategy = 'mean'))),
    ('xgb', XGBClassifier(random_state=42, eta=0.8682247206087741, max_depth=5, n_estimators=361))
    ])
pipe.fit(X_train, y_train)


def pickling(pipe, Match_merge):
        with open('model.pkl','wb') as pickle_file:
                pickle.dump(pipe, pickle_file)

        Match_merge.to_csv("./Match_merge.csv", index=False)
        pd.DataFrame(user_data, columns=["id", "nickname"]).to_csv("./User.csv", index=False)
pickling(pipe, Match_merge)
scheduler.add_job(func=pickling, trigger='interval', hours=24, start_date='2022-04-20 09:00:00')
scheduler.start()


