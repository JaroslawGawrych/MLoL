import pandas as pd
import os
from utils import print_df

def prepare():
   
    df = pd.read_json('data/raw_matches_data.json')

    df_challenges = pd.json_normalize(df['challenges']).add_prefix('')
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
            'championId',
            'baronKills',
            'totalDamageShieldedOnTeammates',
            'individualPosition',
            'teamPosition',
            'nexusKills',
            'damageDealtToTurrets',
            'deathsByEnemyChamps',
            'damageDealtToObjectives',
            'kda',
            'goldEarned',
            'inhibitorKills',
            'assists',
            'turretKills',
            'dragonKills',
            'totalHealsOnTeammates',
            'visionScore',

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

    ], inplace=True)
    
    df = pd.get_dummies(df, columns=['lane'])
    df.replace({True: 1, False: 0}, inplace=True)

    df['damageDealtToBuildingsPerMinute'] = df['damageDealtToBuildings'] / (df['timePlayed'] / 60)

    df = df.groupby(['championName']).mean().reset_index()
    print_df(df)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "prepared_matches_data.csv"), index=False)

if __name__ == '__main__':
    prepare()