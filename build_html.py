from jinja2 import Environment, FileSystemLoader
from datastore import getStatisticsData, getUserDetail
from functools import cmp_to_key
from config import Config
import shutil
import os

env = Environment(loader=FileSystemLoader('./template'))
env.globals['PATH_PREFIX'] = Config['path_prefix']

def build_html(template, dst, params = {}):
    template = env.get_template(template)
    with open(Config['build_dir_path']+dst,"w") as f:
        f.write(template.render(params))

#build_html("rank.html", "rank.html")

Stat = getStatisticsData()

def genRankHtml():
    def cmp(a,b):
        if a['rating'] != b['rating']:
            if a['rating'] > b['rating']:
                return 1
            elif a['rating'] < b['rating']:
                return -1
            else:
                return 0
        elif a['attend'] != b['attend']:
            if a['attend'] > b['attend']:
                return 1
            elif a['attend'] < b['attend']:
                return -1
            else:
                return 0
        else:
            return 0

    ranking = []
    for u in Stat['users']:
        ranking.append(Stat['users'][u])

    ranking.sort(key = cmp_to_key(cmp))
    ranking.reverse()
    for i in range(len(ranking)):
        ranking[i]['rank'] = i+1

    build_html("rank.html", "rank.html", {"ranking": ranking})
    build_html("rank.html", "index.html", {"ranking": ranking})

def genUserData(username):
    user = getUserDetail(username)
    if user == None:
        return None
    
    def cmp(a,b):
        #print(a)
        if Stat['contests'][a['contest']]['start_time'] > Stat['contests'][b['contest']]['start_time']:
            return -1
        elif Stat['contests'][a['contest']]['start_time'] < Stat['contests'][b['contest']]['start_time']:
            return 1
        else:
            return 0
    
    events = []
    for e in user:
        eobj = user[e]
        eobj['contest'] = e
        eobj['event_trello_id'] = Stat['contests'][e]['trello_id']
        eobj['solves'] = len(eobj['score_list'])
        eobj['score_rate'] = round((eobj['score']/Stat['contests'][e]['total_score'])*100,2)
        events.append(eobj)
    events.sort(key = cmp_to_key(cmp))
    return events
    #print(events)
    #

def genUserHtml(username):
    data = genUserData(username)
    if data == None:
        print("[Error] User "+username+" not found.")
        return False
    build_html("user.html", "users/"+username+".html", {"events": data, "username":username})

def genEventHtml(eventname):
    if not eventname in Stat['contests']:
        print("[Error] Event "+eventname+" not found.")
        return False
    event = Stat['contests'][eventname]

    users = []
    for username in Stat['users']:
        udata = genUserData(username)
        for e in udata:
            if e['contest'] != eventname:
                continue
            e['username'] = username
            users.append(e)

    def cmp(a,b):
        if a['score'] == b['score']:
            return 0
        elif a['score'] > b['score']:
            return -1
        else:
            return 1
    
    users.sort(key = cmp_to_key(cmp))
    build_html("event_detail.html", "events/"+Stat['contests'][eventname]['trello_id']+".html", {"users": users, "eventname":eventname, "event":Stat['contests'][eventname]})
    #print(users)

def genEvents():
    events = []
    for e in Stat['contests']:
        events.append(Stat['contests'][e])
    def cmp(a,b):
        if a['start_time'] == b['start_time']:
            return 0
        elif a['start_time'] > b['start_time']:
            return -1
        else:
            return 1
    events.sort(key = cmp_to_key(cmp))
    build_html("events.html", "events.html", {"events": events})

def build_full():
    if not os.path.isdir(Config['build_dir_path']):
        os.makedirs(Config['build_dir_path'])
        os.makedirs(Config['build_dir_path']+"users/")
        os.makedirs(Config['build_dir_path']+"events/")
    if not os.path.isdir(Config['build_dir_path']+"/static/"):
        shutil.copytree("template/static/",Config['build_dir_path']+"/static/")
    genRankHtml()
    for u in Stat['users']:
        genUserHtml(u)
        
    genEvents()
    for e in Stat['contests']:
        genEventHtml(e)

build_full()