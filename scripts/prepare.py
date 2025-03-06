import pandas as pd
import os
import utils

def prepare():
    df = pd.read_json('data/raw_matches_data.json')
    df.drop(columns=[

        # ping usage data
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
        'visionClearedPings',

        # kayn exclusive data
        'championTransform', 

        # item data
        'item0',
        'item1',
        'item2',
        'item3',
        'item4',
        'item5',
        'item6',
        'consumablesPurchased',
        'goldSpent',
        'itemsPurchased',
        'visionWardsBoughtInGame',
        
        # fun data 
        'largestCriticalStrike',
        'totalDamageDealt',

        # player data
        'profileIcon',
        'puuid',
        'riotIdGameName',
        'riotIdTagline',
        'summonerLevel',
        'summonerName',
        'participantId',
        'summonerId',

        # team data
        'teamId',
        'turretsLost',
        'nexusLost',
        
        # ambigous data
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
        'eligibleForProgression',
        'placement',

        # arena exclusive data
        'playerAugment1',
        'playerAugment2',
        'playerAugment3',
        'playerAugment4',
        'playerAugment5',
        'playerAugment6',
        
        # high correlation data
        'champExperience',
        'championId',
        'individualPosition',
        'teamPosition',
        'damageDealtToTurrets',
        'damageDealtToObjectives',
        
        # ability usage data
        'spell1Casts',
        'spell2Casts',
        'spell3Casts',
        'spell4Casts',
        
        # summoner spell data
        'summoner1Id',
        'summoner2Id',
        'summoner1Casts',
        'summoner2Casts',
        
        # categorized damage data
        'magicDamageDealt',
        'magicDamageDealtToChampions',
        'magicDamageTaken',
        'physicalDamageDealt',
        'physicalDamageDealtToChampions',
        'physicalDamageTaken',
        'trueDamageDealt',
        'trueDamageDealtToChampions',
        'trueDamageTaken'

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

        # swarm exclusive data
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

        # item usage data
        'challenges_legendaryItemUsed',

        # map specific data
        'challenges_HealFromMapSources',
        'challenges_InfernalScalePickup',

        # ability usage data
        'challenges_abilityUses',

        # fun data
        'challenges_blastConeOppositeOpponentCount',
        'challenges_dancedWithRiftHerald',
        'challenges_doubleAces',
        'challenges_quickCleanse',
        'challenges_fistBumpParticipation',
        'challenges_elderDragonKillsWithOpposingSoul',
        'challenges_elderDragonMultikills',
        'challenges_fullTeamTakedown',
        'challenges_mejaisFullStackInTime',
        'challenges_multiTurretRiftHeraldCount',
        'challenges_multikillsAfterAggressiveFlash',
        'challenges_outerTurretExecutesBefore10Minutes',
        'challenges_shortestTimeToAceFromFirstTakedown',
        'challenges_takedownsInAlcove',
        'challenges_takedownsInEnemyFountain',
        'challenges_twentyMinionsIn3SecondsCount',


        # champion unrelated data
        'challenges_takedownsAfterGainingLevelAdvantage',
        'challenges_skillshotsDodged',
        'challenges_skillshotsHit',
        'challenges_landSkillShotsEarlyGame',
        'challenges_dodgeSkillShotsSmallWindow',
        'challenges_multiKillOneSpell',
        'challenges_epicMonsterKillsWithin30SecondsOfSpawn',

        # high correlation data
        'challenges_epicMonsterStolenWithoutSmite',

        # aram specific data
        'challenges_killsOnRecentlyHealedByAramPack',
        'challenges_poroExplosions',
        'challenges_snowballsHit',
        
        # team data
        'challenges_teamBaronKills',
        'challenges_teamElderDragonKills',
        'challenges_teamRiftHeraldKills',
        'challenges_flawlessAces',
        'challenges_lostAnInhibitor'

    ], inplace=True)
    df = df.groupby(['championName']).mean().reset_index()
    utils.print_df(df)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "prepared_matches_data.csv"), index=False)

if __name__ == '__main__':
    prepare()