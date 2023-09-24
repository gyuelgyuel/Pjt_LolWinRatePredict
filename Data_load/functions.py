import requests
from pathlib import Path
import time
import datetime
import csv
import os

data_path = Path(__file__).parent / 'data/'
## csv파일 list로 반환
def csv2list(filename):
    ## filename이 포함되어있는 파일 찾기
    for i in os.listdir(data_path):
        if filename in i:
            filename = i
            break
    l = []
    f = open(data_path/filename,'r',encoding='utf-8-sig')
    r = csv.reader(f)
    for row in r:
        l.append(row)
    f.close()
    return l

def list2csv(_list,filename):
    with open(data_path/(filename+'.csv'),'w',encoding='utf-8-sig',newline='') as f:
        write = csv.writer(f)
        write.writerows(_list)
        f.close()
    return filename+'.csv'

## 챌린저 유저의 소환사명, puuid가 적혀있는 csv파일을 ./data 폴더에 생성
def gen_challenger_userlist(my_api):
    # file이 여러개일경우, 가장 앞의 file 가져오므로 뒤의 파일 여는 걸 원하면 기존 파일을 삭제 또는 다른 폴더에 넣기
    file = ''
    for i in os.listdir(data_path):
        if '_userlist_' in i:
            file = i
            break
    # 기존 파일이 없는 경우
    if len(file)==0:
        print("Message(gen_challenger_userlist) : request to riot on process ")
        ## 챌린저 유저 목록 (300명)
        request_header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "https://developer.riotgames.com",
                        "X-Riot-Token": my_api
                    }
        url = 'https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
        requestData = requests.get(url, headers=request_header)
        cnt = 0
        start_time = time.time()
        cnt += 1

        ## 리그 정보 [티어,리그ID,게임종류]
        league_info = [requestData.json()['tier'],requestData.json()['leagueId'],requestData.json()['queue']]

        ## 챌린저 유저 목록
        user_list = requestData.json()['entries']
        name_list = []
        for info in user_list:
            name_list.append([info['summonerName']])

        ## 챌린저 puuid 목록
        puuid_list = []
        request_header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "https://developer.riotgames.com",
                        "X-Riot-Token": my_api
                    }
        
        for name in name_list:
            if cnt%100==0 and cnt!=0:   # 2분에 100request 가능
                end_time = time.time()
                sleep_time = 120-(end_time-start_time)
                if sleep_time > 0:
                    print(f"Message(gen_challenger_userlist) : sleep {round(sleep_time,2)}sec due to request condition")
                    time.sleep(sleep_time)
            url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+name[0]
            requestData = requests.get(url, headers=request_header)
            if cnt%100==0:
                start_time = time.time()
            cnt += 1
            if requestData.status_code == 200:
                puuid_list.append(requestData.json().get('puuid'))
            else:
                puuid_list.append(None)
            time.sleep(0.05)    # 1초에 20request 가능

        for i in range(len(name_list)):
            name_list[i].append(puuid_list[i])

        ## 날짜
        date = requestData.headers['Date'].split(' ')

        ## puuid 포함 저장
        name_list.insert(0,['summonerName', 'puuid'])
        list2csv(name_list,league_info[0]+'_userlist_'+''.join(date[3:0:-1]))
        return name_list
    # userlist 파일이 이미 존재할 경우 list로 변환후 반환
    else:
        print(f"Message(gen_challenger_userlist) : user list from '{data_path/file}'")
        return csv2list(file)
    
## return list that contains recent n matchid of each puuid in puuid_list
## And make csv file 'MatchId_<date>.csv' in data folder
## If you want to make another matchid csv file, move old matchid csv file to other folder
def recent_matchid_by_puuids(count,puuid_list,my_api):
    file = ''
    for i in os.listdir(data_path):
        if 'MatchId_' in i:
            file = i
            break
    if len(file)==0:
        print("Message(recent_matchid_by_puuids) : request to riot on process ")
        request_header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
                        "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,es;q=0.7",
                        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "https://developer.riotgames.com",
                        "X-Riot-Token": my_api
                    }
        matchid_list = [['matchid']]
        cnt = 0
        start_time = time.time()
        for puuid in puuid_list:
            if cnt%100==0 and cnt!=0:   # 2분에 100request 가능
                end_time = time.time()
                sleep_time = 120-(end_time-start_time)
                if sleep_time > 0:
                    print(f"Message(recent_matchid_by_puuids) : sleep {round(sleep_time,2)}sec due to request condition")
                    time.sleep(sleep_time)
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
            requestData = requests.get(url,headers=request_header)
            if cnt%100==0:
                start_time = time.time()
            cnt += 1
            if requestData.status_code == 200:
                matchids = list(requestData.json())     # 경기들 모두 append
                for matchid in matchids:
                    if not (matchid in matchid_list):
                        matchid_list.append([matchid])
            time.sleep(0.05)    # 1초에 20request 가능
        
        list2csv(matchid_list, 'MatchId_'+str(datetime.datetime.today().date()))
        
        return matchid_list
    
    else:
        print(f"Message(recent_matchid_by_puuids) : matchid list from '{data_path/file}'")
        return csv2list('MatchId_')
    
## get game data from match id
def gen_gamedata(matchid_list,my_api):
    file = ''
    for i in os.listdir(data_path):
        if 'gamedata_' in i:
            file = i
            break
    if len(file)==0:
        print("Message(gen_gamedata) : request to riot on process ")
        request_header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "https://developer.riotgames.com",
                        "X-Riot-Token": my_api
                    }
        gamedata = []
        cnt = 0
        start_time = time.time()
        for matchid in matchid_list:
            if cnt%100==0 and cnt!=0:   # 2분에 100request 가능
                end_time = time.time()
                sleep_time = 120-(end_time-start_time)
                if sleep_time > 0:
                    print(f"Message(gen_gamedata) : sleep {round(sleep_time,2)}sec due to request condition")
                    time.sleep(sleep_time)
            url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchid[0]}'
            requestData = requests.get(url,headers=request_header)
            if cnt%100==0:
                start_time = time.time()
            cnt += 1
            # info 데이터가 존재할 경우만 데이터 저장
            if requestData.status_code == 200:
                if requestData.json().get('info'):
                    userlist = requestData.json().get('info').get('participants')
                    for userinfo in userlist:
                        userdata = []
                        primarykey = ['summonerName', 'championName', 'win', 'kills', 'deaths', 'assists', 'totalDamageDealtToChampions']   # 중요 피쳐
                        userkeys = list(userinfo.keys())    # userinfo가 dict 형태가 아니면 에러
                        ## table 작성 초기면 각 feature의 title 저장
                        if len(gamedata)==0:
                            if 'challenges' in userkeys:
                                userkeys.remove('challenges')
                                title = primarykey + userkeys + list(userinfo.get('challenges').keys())
                                gamedata.append(title)
                        ## title이 저장되었다면 (title이 저장되기 전까지 데이터는 날림)
                        if len(gamedata)>0:
                            for k in title:
                                if k in userinfo.keys():
                                    userdata.append(userinfo.get(k))
                                else:
                                    if 'challenges' in userinfo.keys():
                                        userdata.append(userinfo.get('challenges').get(k))
                                    else:
                                        userdata.append(None)
                            gamedata.append(userdata)
            time.sleep(0.05)    # 1초에 20request 가능
        
        list2csv(gamedata, 'gamedata_'+str(datetime.datetime.today().date()))
        return gamedata
    
    else:
        print(f"Message(gen_gamedata) : game data from '{data_path/file}'")
        return csv2list('gamedata_')