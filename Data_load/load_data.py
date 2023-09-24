import functions as fn
import time
from dotenv import dotenv_values
from pathlib import Path

env_path = Path(__file__).parent / '.env'
s = time.time()

## 현재 내 riot api (24시간마다 갱신필요)
config = dotenv_values(env_path)
my_api = config.get("API")

# ## 챌린저 [소환사명, puuid] csv파일 생성
user_list = fn.gen_challenger_userlist(my_api)
e1 = time.time()
# time.sleep(120)

## user_list에서 puuid_list 뽑기
puuid_list = []
for i in user_list[1:]:
    if i[1]:
        puuid_list.append(i[1])

## puuid_list로 matchid_list 받아오기
matchid_list = fn.recent_matchid_by_puuids(100,puuid_list,my_api)
e2 = time.time()
# time.sleep(120)

## gamedata table 만들기
challenger_gamedata = fn.gen_gamedata(matchid_list[1:1000],my_api)

e = time.time()
# print(f'get challenger puuid time taken   : {(e1-s)//60}min {(e1-s)%60//1}sec')
# print(f'get matchid by puuid time taken   : {(e2-e1-120)//60}min {(e2-e1-120)%60//1}sec')
# print(f'get gamedata by matchid time taken: {(e-e2-120)//60}min {(e-e2-120)%60//1}sec')
# print(f'total time taken                  : {(e-s-240)//60}min {(e-s-240)%60//1}sec')