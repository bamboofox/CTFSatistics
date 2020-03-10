import json
import os

def update(contest, People_data, contestdata):
    Users = {}
    with open("data/users.json","r") as f:
        Users = json.loads(f.read())
    Contests = {}
    with open("data/contests.json","r") as f:
        Contests = json.loads(f.read())
    Contests[contest['name']] = contest
    with open("data/contests/"+contest['trello_id']+".json","w") as f:
        f.write(json.dumps(contestdata))
    
    for p in People_data:
        personal_data = {}
        if not p in Users:
            Users[p] = {"username":p, "nickname":"", "rating": 0, "attend": 0}
        else:
            with open("data/users/"+p+".json","r") as f:
                personal_data = json.loads(f.read())
        if not contest['name'] in personal_data:
            personal_data[contest['name']] = {"rating": 0.0,"attend":0, "score": 0, "attend_list": [], "score_list": {}}
        Users[p]['rating'] -= personal_data[contest['name']]['rating']
        Users[p]['attend'] -= personal_data[contest['name']]['attend']

        personal_data[contest['name']] = People_data[p]
        
        Users[p]['rating'] += personal_data[contest['name']]['rating']
        Users[p]['rating'] = round(Users[p]['rating'], 2)
        Users[p]['attend'] += personal_data[contest['name']]['attend']

        Users[p]['attend_contests'] = len(personal_data)

        if not 'last_event' in Users[p]:
            Users[p]['last_event'] = ""
        mtime = 0
        for c in personal_data:
            if Contests[c]['start_time'] > mtime:
                mtime = Contests[c]['start_time']
                Users[p]['last_event'] = c

        with open("data/users/"+p+".json","w") as f:
            f.write(json.dumps(personal_data))
            
    
    with open("data/contests.json","w") as f:
        f.write(json.dumps(Contests))
    with open("data/users.json","w") as f:
        f.write(json.dumps(Users))

def getStatisticsData():
    Users = {}
    with open("data/users.json","r") as f:
        Users = json.loads(f.read())
    Contests = {}
    with open("data/contests.json","r") as f:
        Contests = json.loads(f.read())

    return {"users": Users, "contests": Contests}

def getUserDetail(username):
    if not os.path.isfile("data/users/"+username+".json"):
        return None
    with open("data/users/"+username+".json","r") as f:
        return json.loads(f.read())