
import os
from flask import Flask, render_template, request
import pickle
import requests
import pandas as pd




app = Flask(__name__)

@app.route('/')
def index():
    
    return render_template('index.html'), 200

@app.route('/user', methods=["POST"])
def user():

    
    FILENAME = "Match_merge.csv"
    FILEPATH = os.path.join(os.getcwd(), FILENAME)


    features = ['foul', 'redcards', 'yellowcards', 'dribble', 'cornerkick',
       'possession', 'offsidecount', 'controller', 'match_result',
       'match_date', 'season_id', 'shoot_total',
       'effective_shoot_total', 'goal_total', 'shoot_heading', 'goal_heading',
       'shoot_freekick', 'goal_freekick', 'shoot_in_penalty',
       'goal_in_penalty', 'shoot_out_penalty', 'goal_out_penalty',
       'shoot_penaltykick', 'goal_penaltykick',
       'pass_try', 'pass_success', 'shortpass_success', 'longpass_try',
       'longpass_success', 'bouncinglobpass_try', 'bouncinglobpass_success',
       'drivengroundpass_try', 'drivengroundpass_success',
       'throughpass_success', 'lobbedthroughpass_try',
       'lobbedthroughpass_success', 'block_try',
       'block_success', 'tackle_try', 'tackle_success', 'shoot_heading_per',
       'goal_heading_per', 'shoot_out_penalty_per', 'goal_out_penalty_per',
       'field_shoot', 'field_goal', 'assist', 'intercept', 'defending']

    value = request.form["nickname"]
    nickname = "%s"%value
    headers = {'Authorization' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiMTg0OTE3MjMxIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExNDgxIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjUwMDoxMCIsIm5iZiI6MTY0OTg1NDI3MiwiZXhwIjoxNjY1NDA2MjcyLCJpYXQiOjE2NDk4NTQyNzJ9.qE--Kwy2lznUUHyGgZxkR2oZLdHN73VWmzqNbFstDI4'} 

    url = f"https://api.nexon.co.kr/fifaonline4/v1.0/users?nickname={nickname}"

    user = requests.get(url, headers=headers)
    user_id = user.json()

    Match_merge = pd.read_csv(FILEPATH)
    if len(user_id) == 1:
        return render_template('play_style.html', play_style = 9), 200
    
    wanted = Match_merge.loc[Match_merge["match_user_id"] == user_id["accessId"]]
    if len(wanted) == 0:
        return render_template('play_style.html', play_style = 9), 200
    wanted_list = wanted.iloc[0]

    with open('model.pkl','rb') as pickle_file:
        classifer_model = pickle.load(pickle_file)
    play_style = classifer_model.predict([wanted_list[features]])
    
    return render_template('play_style.html', play_style = play_style[0]), 200

@app.route('/user/4-1-4-1', methods=['POST'])
def formation1():
    return render_template('formation1.html'),200

@app.route('/user/4-1-2-3_W', methods=['POST'])
def formation2():
    return render_template('formation2.html'),200

@app.route('/user/4-1-2-3_F', methods=['POST'])
def formation3():
    return render_template('formation3.html'),200

@app.route('/user/4-1-2-1-2', methods=['POST'])
def formation4():
    return render_template('formation4.html'),200

@app.route('/user/4-2-2-2', methods=['POST'])
def formation5():
    return render_template('formation5.html'),200

@app.route('/user/4-3-1-2', methods=['POST'])
def formation6():
    return render_template('formation6.html'),200

@app.route('/user/4-2-3-1', methods=['POST'])
def formation7():
    return render_template('formation7.html'),200

@app.route('/user/4-4-2', methods=['POST'])
def formation8():
    return render_template('formation8.html'),200

@app.route('/user/4-3-3', methods=['POST'])
def formation9():
    return render_template('formation9.html'),200
@app.route('/dashboard', methods=["GET"])
def dashboard():
    return render_template('dashboard.html'),200

if __name__ == "__main__":
    app.run(debug=True)