from config import Config
from api import Trello, CTFTime
from datastore import update
from datetime import datetime
import re
import sys
import math

#boardid = input("Board: ")
boardid = sys.argv[1]

trello = Trello(Config['trello_baseurl'], Config['trello_apikey'], Config['trello_token'], boardid)
if trello.board:
    #print(trello.board)
    print("[Info] Init")
else:
    print("[Error] Board not found")
    exit(0)

Contest = {"name": trello.board['name'], "ctftime_rating":0.0, "rank": 1,"total_teams": 1, "total_score":0}
ctftime_eventid = int(input("CTFTime event id (-1 if the event doesn't exist on the CTFTime): "))
ctftime_teamid = -1

if "ctftime_teamid" in Config:
    ctftime_teamid = Config['ctftime_teamid']

Contest['rating'] = 0
if ctftime_eventid != -1:
    ctftime = CTFTime(Config['ctftime_baseurl'], ctftime_eventid, ctftime_teamid)
    if not ctftime.event:
        print("[Error] CTFTime event not found")
        exit(0)

    Contest['ctftime_rating'] = ctftime.event['weight']
    if ctftime.result != None:
        Contest['ctftime_points'] = ctftime.result['points']
        Contest['rank'] = ctftime.result['rank']
        Contest['total_teams'] = ctftime.result['total_teams']
        Contest['start_time'] = ctftime.event['start'].split("+")[0]+"+"+("".join(ctftime.event['start'].split("+")[1].split(":")))
        Contest['start_time'] = datetime.timestamp(datetime.strptime(Contest['start_time'],"%Y-%m-%dT%H:%M:%S%z"))
        #Contest['rating'] = Contest['ctftime_points']
    else:
        print("[WARN] Can't found your team in the ctftime scoreboard")
elif input("Do you want to input team ranking manually? [Y/n]: ")[0] == "Y":
    #Contest['ctftime_rating'] = float(input("ctftime rating: "))
    #Contest['ctftime_points'] = float(input("ctftime points (use to calculate user's rating): "))
    Contest['rank'] = int(input("rank: "))
    Contest['total_teams'] = int(input("How many teams participate this event: "))

if Contest['rating'] == 0:
    Contest['rating'] = float(input("Please input a rating for calculate everyone's rating (now rating is 0): "))
elif input("Do you want to input rating manually? (now rating is "+str(Contest['rating'])+") [Y/n]: ")[0] == "Y":
    Contest['rating'] = float(input("Please input a rating: "))
Contest['trello_id'] = trello.board['id']

print("[Info] Rating: "+str(Contest['rating']))

Challenges = []

cards = trello.getData("boards/"+boardid+"/cards")
for card in cards:
    inlist = trello.getData("cards/"+card['id']+"/list")['name']
    #print(inlist)
    if inlist == 'Info':
        continue
    
    print("[Info] Fetching "+card['name'])
    chal = {}
    chal['name'] = card['name']
    chal['type'] = inlist

    score_param = card['desc'].split("[SCORE]")
    chal['score_param'] = {}
    chal['score_param_sum'] = 0.0
    if len(score_param) == 3:
        for u_str in score_param[1].split("\n"):
            #print(u_str)
            if len(u_str.split()) != 2:
                continue
            chal['score_param'][u_str.split()[0][1:]] = float(u_str.split()[1])
            chal['score_param_sum'] += float(u_str.split()[1])

    chal['solved'] = False
    card_stickers = trello.getData("cards/"+card['id']+"/stickers")
    for st in card_stickers:
        if st['image'] == "check":
            chal['solved'] = True

    matchres = re.search("\[(\d+)\]",card['name'])
    if matchres != None:
        chal['score'] = int(matchres.group(1))
        if chal['solved']:
            Contest['total_score'] += chal['score']
    else:
        chal['score'] = 0
        if chal['solved']:
            print("[Notice] "+chal['name']+" doesn't have score")
        else:
            print("[WARN] "+chal['name']+" doesn't have score")
    chal['members'] = []
    card_members = trello.getData("cards/"+card['id']+"/members")
    for m in card_members:
        chal['members'].append(m['username'])


    Challenges.append(chal)
#print(Challenges)
print("[Info] Fetched all cards.")

People = {}

def MaybeNewPeople(username):
    if username in People:
        return
    People[username] = {"rating": 0.0,"attend":0, "score": 0, "attend_list": [], "score_list": {}}

def CheckScoreParam(score_param, userlist):
    if len(score_param) != len(userlist):
        return False
    for u in score_param.keys():
        if not u in userlist:
            return False
    return True

print("[Info] Caculating...")
for chal in Challenges:
    print("[Info] Caculating challenge "+chal['name'])
    for m in chal['members']:
        MaybeNewPeople(m)
        People[m]['attend'] += 1
        People[m]['attend_list'].append(chal['name'])
        if not chal['solved']:
            continue
        if len(chal['members']) == 0:
            print("[WARN] challenge "+chal['name']+" was solved, but it doesn't have any member." )
            continue
        if len(chal['members']) == 1:
            ps = chal['score']
        else:
            #if not CheckScoreParam(chal['score_param'], chal['members']):
            #    print("[WARN] challenge "+chal['name']+" doesn't have score param or the people in the score param doesn't match the members. So the score will be divided equally to members in the card.")
            #    ps = int(round(chal['score']/len(chal['members'])))
            if m in chal['score_param']:
                ps = int(round(chal['score']*(chal['score_param'][m]/chal['score_param_sum'])))
            elif len(chal['score_param']) == 0:
                ps = int(round(chal['score']*(1/len(chal['members']))))
        
        People[m]['score_list'][chal['name']] = ps
        People[m]['score'] += ps
import json
#print(People)

for p in People:
    r = Contest['rating'] * 10.0 * (People[p]['score'] / Contest['total_score'])
    r = round(r, 2)
    People[p]['rating'] = r

update(Contest, People, Challenges)

print(json.dumps(People,indent = 2))