import requests
import os

RIOT_KEY = os.getenv('RIOT_KEY')

def get_puuid(region, gameName, tagLine):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={RIOT_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return(response.json().get('puuid'))
    else:
        print("Error:", response.text)
        return None

def get_match_ids(region, puuid, start, count, limit, match_ids):

    if(start < limit):
            
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&api_key={RIOT_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            match_ids += response.json()
            match_ids = get_match_ids(region, puuid, start+count, count, limit, match_ids)
        else:
            print("Error:", response.text)
            return match_ids
        
    return match_ids

def get_match_info(region, match_ids):
    match_info = []
    for x in match_ids:

        url = f"https://{region}.api.riotgames.com//lol/match/v5/matches/{x}?api_key={RIOT_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            print(response.json())
            match_info += response.json()
        
    return match_info

if __name__ == "__main__":
    puuid = get_puuid("europe", "julusia42069", "EUNE")
    match_ids = get_match_ids("europe", puuid, 0, 1, 1, [])
    match_info = get_match_info("europe", match_ids)
    print(match_ids)
