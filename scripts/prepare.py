import pandas as pd
import os
from utils import print_df
import ast

def prepare_matches():
   
    df = pd.read_json('data/matches_data.json')

    df_challenges = pd.json_normalize(df['challenges'])
    df_challenges.rename(columns={
    'killingSprees':'challenges_killingSprees',
    'turretTakedowns':'challenges_turretTakedowns'
    }, inplace=True)
    df = df.drop(columns=['challenges']).join(df_challenges)

    df.drop(columns=[

        # not used

            # ambigous
            'playerSubteamId',
            'objectivesStolenAssists', # how is it calculated?
            'challenges_killingSprees',
            'challenges_turretTakedowns',
            'bountyLevel', # max / final ?
            'missions',
            'unrealKills',
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

            # aram/swarm/arena exclusive
            'killsOnRecentlyHealedByAramPack',
            'poroExplosions',
            'snowballsHit',
            'SWARM_DefeatAatrox',
            'SWARM_DefeatBriar',
            'SWARM_DefeatMiniBosses',
            'SWARM_EvolveWeapon',
            'SWARM_Have3Passives',
            'SWARM_KillEnemy',
            'SWARM_PickupGold',
            'SWARM_ReachLevel50',
            'SWARM_Survive15Min',
            'SWARM_WinWith5EvolvedWeapons',
            'playerAugment1',
            'playerAugment2',
            'playerAugment3',
            'playerAugment4',
            'playerAugment5',
            'playerAugment6',

            # ping usage
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

            # oddly specific / fun
            'championTransform', # kayn exclusive
            'dancedWithRiftHerald',
            'elderDragonMultikills',
            'getTakedownsInAllLanesEarlyJungleAsLaner',
            'fullTeamTakedown',
            'mejaisFullStackInTime',
            'outerTurretExecutesBefore10Minutes',
            'elderDragonKillsWithOpposingSoul',
            'killedChampTookFullTeamDamageSurvived',        
            'multiTurretRiftHeraldCount',
            'multikillsAfterAggressiveFlash',
            'takedownsInEnemyFountain',
            'twentyMinionsIn3SecondsCount',
            'epicMonsterStolenWithoutSmite',
            'earliestElderDragon',
            'earliestDragonTakedown',
            'twoWardsOneSweeperCount',
            'turretsTakenWithRiftHerald',
            'tookLargeDamageSurvived',
            'takedownOnFirstTurret',
            'survivedThreeImmobilizesInFight',
            'quickSoloKills',
            'playedChampSelectPosition',
            'perfectDragonSoulsTaken',
            'quickFirstTurret',
            'legendaryCount', # streak or items?
            'highestWardKills',
            'maxKillDeficit', # ?
            'hadOpenNexus',
            'timeCCingOthers', # ?
            'soloTurretsLategame',
            'firstTurretKilledTime',
            'multiKillOneSpell',
            'unseenRecalls',
            'acesBefore15Minutes',
            'alliedJungleMonsterKills',
            'baronBuffGoldAdvantageOverThreshold',
            'legendaryItemUsed',
            '12AssistStreakCount',
            'bountyGold', # earned?
            'largestCriticalStrike',
            'totalDamageDealt',
            'fistBumpParticipation',
            'largestMultiKill',
            'killsUnderOwnTurret',
            'pickKillWithAlly',
            'highestChampionDamage',
            'highestCrowdControlScore',
            'killsOnOtherLanesEarlyJungleAsLaner',
            'killsNearEnemyTurret',
            'killsWithHelpFromEpicMonster',
            'totalUnitsHealed',
            'killingSprees',
            'outnumberedKills',
            'knockEnemyIntoTeamAndKill',
            'perfectGame',
            'survivedSingleDigitHpCount',
            'outnumberedNexusKill',

            'largestKillingSpree',

            # player
            'profileIcon',
            'puuid',
            'riotIdGameName',
            'riotIdTagline',
            'summonerLevel',
            'summonerName',
            'participantId',
            'summonerId',

            # team
            'teamId',
            'turretsLost',
            'nexusLost',
            'inhibitorsLost',        
            'doubleAces',
            'shortestTimeToAceFromFirstTakedown',
            'teamBaronKills',
            'teamElderDragonKills',
            'teamRiftHeraldKills',
            'flawlessAces',
            'lostAnInhibitor',
            
            # map specific
            'HealFromMapSources',
            'takedownsInAlcove',
            'InfernalScalePickup',
            'blastConeOppositeOpponentCount',

            # item
            'item0',
            'item1',
            'item2',
            'item3',
            'item4',
            'item5',
            'item6',
            'fastestLegendary',
            'consumablesPurchased',
            'goldSpent',
            'itemsPurchased',

            # ability usage
            'spell1Casts',
            'spell2Casts',
            'spell3Casts',
            'spell4Casts',
            'abilityUses',
            
            # summoner spells
            'summoner1Id',
            'summoner2Id',
            'summoner1Casts',
            'summoner2Casts',

            # champion unrelated skill expression
            'quickCleanse',
            'takedownsAfterGainingLevelAdvantage',
            'skillshotsDodged',
            'skillshotsHit',
            'landSkillShotsEarlyGame',
            'dodgeSkillShotsSmallWindow',
            'epicMonsterKillsWithin30SecondsOfSpawn',

        # not used but with potential

            # high correlation with used / calculated from used
            'champExperience',
            'gameLength',
            'teamDamagePercentage',
            'damageSelfMitigated',
            'damageTakenOnTeamPercentage',
            'kills',
            'takedowns',
            'assists',
            'championId',
            'baronKills',
            'totalDamageShieldedOnTeammates',
            'nexusKills',
            'damageDealtToTurrets',
            'deathsByEnemyChamps',
            'damageDealtToObjectives',
            'goldEarned',
            'inhibitorKills',
            'assists',
            'turretKills',
            'dragonKills',
            'totalHealsOnTeammates',
            'visionScore',
            'totalHeal',
            'enemyChampionImmobilizations',

            # early game dominance
            'firstBloodKill',
            'firstBloodAssist',
            'jungleCsBefore10Minutes',
            'firstTowerAssist',
            'takedownsBeforeJungleMinionSpawn',
            'firstTowerKill',
            'firstTurretKilled',
            'turretPlatesTaken',
            'gameEndedInEarlySurrender',
            'gameEndedInSurrender',
            'kTurretsDestroyedBeforePlatesFall',
            'takedownsFirstXMinutes',
            'laneMinionsFirst10Minutes',
            'maxLevelLeadLaneOpponent',
            'maxCsAdvantageOnLaneOpponent',
            'teamEarlySurrendered',
            'laningPhaseGoldExpAdvantage',
            'earlyLaningPhaseGoldExpAdvantage',

            # wards
            'wardsGuarded',
            'wardTakedownsBefore20M',
            'wardTakedowns',
            'visionScoreAdvantageLaneOpponent',
            'stealthWardsPlaced',
            'visionWardsBoughtInGame',
            'controlWardsPlaced',
            'wardsPlaced',
            'detectorWardsPlaced',
            'wardsKilled',
            'sightWardsBoughtInGame',

            # multikills / solokills
            'pentaKills',
            'quadraKills',
            'multikills',
            'tripleKills',
            'doubleKills',
            'soloKills',
            
            # minions
            'totalMinionsKilled',
            'totalEnemyJungleMinionsKilled',
            'totalAllyJungleMinionsKilled',
            'neutralMinionsKilled',

            # jungle
            'scuttleCrabKills',
            'moreEnemyJungleThanOpponent',
            'soloBaronKills',
            'killsOnLanersEarlyJungleAsJungler',
            'junglerKillsEarlyJungle',
            'initialCrabCount',
            'initialBuffCount',
            'epicMonsterKillsNearEnemyJungler',
            'epicMonsterSteals',
            'buffsStolen',
            'enemyJungleMonsterKills',
            'objectivesStolen',
            'earliestBaron',
            'junglerTakedownsNearDamagedEpicMonster',

            # support
            'fasterSupportQuestCompletion',
            'completeSupportQuestInTime',

            # categorized damage
            'magicDamageDealt',
            'magicDamageDealtToChampions',
            'magicDamageTaken',
            'physicalDamageDealt',
            'physicalDamageDealtToChampions',
            'physicalDamageTaken',
            'trueDamageDealt',
            'trueDamageDealtToChampions',
            'trueDamageTaken',
            'totalDamageDealtToChampions',

            # time dead / alive
            'totalTimeSpentDead',
            'longestTimeSpentLiving',

            # building takedowns
            'inhibitorTakedowns',
            'nexusTakedowns',
            'turretTakedowns',

            # teamplay
            'saveAllyFromDeath',
            'immobilizeAndKillWithAlly',
            'killAfterHiddenWithAlly',

            # lane
            'individualPosition',
            'teamPosition',
            'lane',

    ], inplace=True)
    
    # df = pd.get_dummies(df, columns=['lane'])
    df.replace({True: 1, False: 0}, inplace=True)

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "prepared_matches_data.csv"), index=False)

def prepare_champions():

    df = pd.read_csv('data/champion_data.csv')

    df['stats'] = df['stats'].apply(ast.literal_eval)
    df_stats = pd.json_normalize(df['stats'])
    df_stats.dropna(axis=1, inplace=True)
    df = df.drop(columns=['stats']).join(df_stats)

    df['client_positions'] = df['client_positions'].apply(ast.literal_eval)
    all_positions = set()
    for positions in df['client_positions']:
        if len(positions) == 1:
            all_positions.update(positions)

    df['external_positions'] = df['external_positions'].apply(ast.literal_eval)

    df_client_position = pd.DataFrame({
        client_position: df.apply(lambda row: client_position in row['client_positions'] or client_position in row['external_positions'], axis=1)
        for client_position in all_positions
    })

    df = df.join(df_client_position)

    df['role'] = df['role'].apply(ast.literal_eval)
    all_roles = set()
    for roles in df['role']:
        if len(roles) == 1:
            all_roles.update(roles)

    df_role = pd.DataFrame({
        role: df['role'].apply(lambda roles: role in roles)
        for role in all_roles
    })

    df = df.join(df_role)

    df.drop(columns=[
        'Unnamed: 0',
        'client_positions',
        'external_positions',
        'role',
        'id',
        'date',
        'title',
        'patch',
        'changes',
        'be',
        'rp',
        'skill_i',
        'skill_q',
        'skill_w',
        'skill_e',
        'skill_r',
        'skills',
        'fullname',
        'nickname',
    ], inplace=True)

    print_df(df.head(10).tail(5))
    
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "prepared_champion_data.csv"), index=False)

if __name__ == '__main__':
    prepare_matches()
    prepare_champions()