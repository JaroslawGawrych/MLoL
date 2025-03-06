import pandas as pd
import os
import numpy as np

def prepare():
    df = pd.read_json('processed_data/raw_matches_data.json')
    df.drop(columns=[

        # exclusion of ping usage data
        'allInPings',
        'assistMePings',
        'basicPings',
        'commandPings',
        'enemyMissingPings',
        'enemyVisionPings',
        'holdPings',
        'getBackPings',
        'needVisionPings',
        'onMyWayPings',
        'pushPings',
        'dangerPings',
        'retreatPings',

        # exclusion of kayn exclusive data
        'championTransform', 

        # exclusion of item data
        'item0',
        'item1',
        'item2',
        'item3',
        'item4',
        'item5',
        'item6',
        'consumablesPurchased',
        
        # exclusion of fun data 
        'largestCriticalStrike',

        # exclusion of player data
        'profileIcon',
        'puuid',
        'riotIdGameName',
        'riotIdTagline',
        'summonerLevel',
        'summonerName',
        'participantId',
        'summonerId',

        # exclusion of team data
        'teamId',
        
        # exclusion of ambigous data
        'playerSubteamId',
        'missions',
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
        'role',
        'subteamPlacement',
        'placement',

        # exclusion of arena exclusive data
        'playerAugment1',
        'playerAugment2',
        'playerAugment3',
        'playerAugment4',
        'playerAugment5',
        'playerAugment6',
        
        # exclusion of high correlation data
        'champExperience',
        'championId',
        'individualPosition',
        'teamPosition',
        
        # exclusion of ability usage data
        'spell1Casts',
        'spell2Casts',
        'spell3Casts',
        'spell4Casts',
        
        # exclusion of summoner spell data
        'summoner1Id',
        'summoner2Id',
        'summoner1Casts',
        'summoner2Casts'
        
    ], inplace=True)

    '''
    TODO:
    drop irrelevant data
    evaluate performance across multiple metrics and come up with overall score
    assign weights to champion specifications based on evaluations
    '''

    df = pd.get_dummies(df, columns=['lane'])
    df.replace({True: 1, False: 0}, inplace=True)
    df_challenges = pd.json_normalize(df['challenges']).add_prefix('challenges_')
    df = df.drop(columns=['challenges']).join(df_challenges)
    df.drop(columns=[

        # exclusion of swarm exclusive data
        'challenges_SWARM_DefeatAatrox',
        'challenges_SWARM_DefeatBriar',
        'challenges_SWARM_DefeatMiniBosses',
        'challenges_SWARM_EvolveWeapon',
        'challenges_SWARM_Have3Passives',
        'challenges_SWARM_KillEnemy',
        'challenges_SWARM_PickupGold',
        'challenges_SWARM_ReachLevel50',
        'challenges_SWARM_Survive15Min',
        'challenges_SWARM_WinWith5EvolvedWeapons',

        # exclusion of item usage data
        'challenges_legendaryItemUsed',

        # exclusion of map specific data
        'challenges_HealFromMapSources',
        'challenges_InfernalScalePickup',

        # exclusion of ability usage data
        'challenges_abilityUses',

        # exclusion of fun data
        'challenges_blastConeOppositeOpponentCount',
        'challenges_dancedWithRiftHerald',
        'challenges_dodgeSkillShotsSmallWindow',
        'challenges_doubleAces',
        'challenges_quickCleanse',
        'challenges_fistBumpParticipation',
        
        # exclusion of aram specific data
        'challenges_killsOnRecentlyHealedByAramPack',
        'challenges_poroExplosions',
        'challenges_snowballsHit',
        
        # exclusion of team data
        'challenges_teamBaronKills',
        'challenges_teamElderDragonKills',
        'challenges_teamRiftHeraldKills'

    ], inplace=True)
    df = df.groupby(['championName']).mean().reset_index()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.T)
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "prepared_matches_data.csv"), index=False)

if __name__ == '__main__':
    prepare()