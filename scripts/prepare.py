import pandas as pd
import os
import json

def prepare():
    df = pd.read_json('processed_data/raw_matches_data.json')
    df.drop(columns=[
        'allInPings',
        'assistMePings',
        'commandPings',
        'championTransform',
        'consumablesPurchased',
        'challenges',
        'enemyMissingPings',
        'enemyVisionPings',
        'holdPings',
        'getBackPings',
        'individualPosition',
        'item0',
        'item1',
        'item2',
        'item3',
        'item4',
        'item5',
        'item6',
        'largestCriticalStrike',
        'missions',
        'needVisionPings',
        'onMyWayPings',
        'participantId',
        'PlayerScore0',
        'PlayerScore1',
        'PlayerScore2',
        'PlayerScore3',
        'PlayerScore4',
        'PlayerScore5',
        'PlayerScore6',
        'PlayerScore7',
        'PlayerScore8',
        'PlayerScore9',
        'PlayerScore10',
        'PlayerScore11',
        'perks',
        'pushPings',
        'profileIcon',
        'puuid',
        'riotIdGameName',
        'riotIdTagline',
        'summonerLevel',
        'summonerName',
        'teamId',
        'dangerPings',
        'playerAugment1',
        'playerAugment2',
        'playerAugment3',
        'playerAugment4',
        'playerAugment5',
        'playerAugment6',
        'playerSubteamId',
        'retreatPings',
        'summonerId',
        'champExperience',
        'basicPings'
        ], inplace=True)
    
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "prepared_matches_data.csv"), index=False)

if __name__ == '__main__':
    prepare()