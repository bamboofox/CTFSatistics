import requests
from requests.compat import urljoin
import json

class Trello:
    def getData(self, url, param = {}):
        url = urljoin(self.baseurl,url)
        reqdata = self.authdata
        reqdata = self.authdata.copy()
        reqdata.update(param)
        res = requests.get(url, reqdata)
        if res.status_code != 200:
            return False
        return json.loads(res.text)

    def __init__(self, baseurl, apikey, token, board):
        self.authdata = {"key":apikey, "token":token}
        self.baseurl = baseurl
        #url = urljoin(self.baseurl,"boards/"+board)
        #reqdata = self.authdata
        #print(url)
        #res = requests.get(url, reqdata)
        self.board = self.getData("boards/"+board)
        if self.board == False:
            return None

 #   def 

class CTFTime:
    def getData(self, url, param = {}):
        url = urljoin(self.baseurl,url)
        #print(url)
        res = requests.get(url, headers = {'User-Agent': ''})
        #print(res.text)
        #print(res.request.headers)
        if res.status_code != 200:
            return False
        return json.loads(res.text)

    def __init__(self, baseurl, id, teamid):
        self.baseurl = baseurl
        self.event = self.getData("events/"+str(id)+"/")
        self.result = None
        if teamid==-1:
            return
        self.result = self.getData("results/")
        if not self.result:
            return
        #print(self.result)
        if str(id) in self.result:
            self.result = self.result[str(id)]
            #print(self.result)
            res = {}
            res['total_teams'] = len(self.result['scores'])
            for t in self.result['scores']:
                if t['team_id'] != teamid:
                    continue
                res['rank'] = t['place']
                res['points'] = t['points']
            if not 'rank' in res:
                self.result = None
            else:
                self.result = res
        else:
            self.result = None
    '''
    def getEventInfo():
        return self.event
    '''