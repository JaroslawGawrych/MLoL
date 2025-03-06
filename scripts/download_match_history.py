import requests
import os
from enum import Enum
from typing import List, Dict
import json

RIOT_KEY = os.getenv('RIOT_KEY')

class Puuid_region(Enum):
    AMERICAS = 1
    ASIA = 2
    ESPORTS = 3
    EUROPE = 4

class Match_region(Enum):
    AMERICAS = 1
    ASIA = 2
    EUROPE = 3
    SEA = 4

class Match_type(Enum):
    RANKED = 1
    NORMAL = 2
    TOURNEY = 3
    TUTORIAL = 4

def get_puuid(region: Puuid_region, gameName: str, tagLine: str) -> str|None:
    url = f'https://{region.name}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={RIOT_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return(response.json().get('puuid'))
    else:
        print('Error:', response.text)
        return None

def get_match_ids(region: Match_region, type: Match_type, puuid: str, start: int, count: int, limit: int, match_ids: List[str]) -> List[str]:
    if(len(match_ids)+count <= limit):
        url = f'https://{region.name}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type={type.name.lower()}&start={start}&count={count}&api_key={RIOT_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            match_ids += response.json()
            match_ids = get_match_ids(region, type, puuid, start+count, count, limit, match_ids)
        else:
            print('Error:', response.text)
            return match_ids
    return match_ids

def get_match_results(region: Match_region, match_ids: List[str], puuid: str) -> List[Dict]:
    match_results = []
    for match_id in match_ids:
        url = f'https://{region.name}.api.riotgames.com//lol/match/v5/matches/{match_id}?api_key={RIOT_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            participants = response.json().get('info', {}).get('participants', [])
            for participant in participants:
                if(participant.get('puuid') == puuid):
                    match_results.append(participant)
        else:
            print('Error:', response.text)
            return match_results
    return match_results

def save_raw_match_data(match_results: List[Dict]):
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "raw_matches_data.json"), 'w') as fp:
        json.dump(match_results, fp, indent=4)

if __name__ == '__main__':
    puuid = get_puuid(region=Puuid_region.EUROPE, gameName='julusia42069', tagLine='eune')
    match_ids = get_match_ids(region=Match_region.EUROPE, type=Match_type.RANKED, puuid=puuid, start=0, count=20, limit=40, match_ids=[])
    match_results = get_match_results(region=Match_region.EUROPE, match_ids=match_ids, puuid=puuid)
    save_raw_match_data(match_results=match_results)