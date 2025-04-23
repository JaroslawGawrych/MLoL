import time
import pandas as pd
import kagglehub
from pymongo import UpdateOne
import requests
import os
from ast import literal_eval
from enum import Enum
from typing import List
import numpy as np
import json
from dotenv import load_dotenv
import utils
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MATCHES_DATA_PATH = os.path.join(OUTPUT_DIR, "matches_data.json")


load_dotenv()
RIOT_KEY = os.getenv("RIOT_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USERNAME = os.getenv("DB_USERNAME")

URI = (
    f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@mlol.29bxhx8.mongodb.net/?appName=MLOL"
)

CLIENT = MongoClient(URI, server_api=ServerApi("1"))

DB = CLIENT["MLOL"]
MATCHES = DB["Matches"]
CHAMPIONS = DB["Champions"]
SCORES = DB["Scores"]


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


REQUESTS_HISTORY_FILE = "requests_history.json"

MATCHES_DATA = []


def load_request_history() -> List[float]:
    if os.path.exists(REQUESTS_HISTORY_FILE):
        with open(REQUESTS_HISTORY_FILE, "r") as f:
            return json.load(f)
    else:
        return []


def save_request_history() -> None:
    with open(REQUESTS_HISTORY_FILE, "w") as f:
        json.dump(REQUESTS_HISTORY, f)


REQUESTS_HISTORY = load_request_history()
MAX_REQUESTS_PER_SECOND = 20
MAX_REQUESTS_PER_2_MINUTES = 100


def download_champion_data(force_download: bool = False):

    path = kagglehub.dataset_download(
        "laurenainsleyhaines/25-s1-3-league-of-legends-champion-data-2025",
        force_download=force_download,
    )
    print("Path to dataset files:", path)

    for file_name in os.listdir(path):
        df = pd.read_csv(os.path.join(path, file_name))

    df["stats"] = df["stats"].apply(literal_eval)
    df_stats = pd.json_normalize(df["stats"])
    df_stats.dropna(axis=1, inplace=True)
    df = df.drop(columns=["stats"]).join(df_stats)

    df["client_positions"] = df["client_positions"].apply(literal_eval)
    all_positions = set()
    for positions in df["client_positions"]:
        if len(positions) == 1:
            all_positions.update(positions)

    df["external_positions"] = df["external_positions"].apply(literal_eval)

    df_client_position = pd.DataFrame(
        {
            client_position: df.apply(
                lambda row: client_position in row["client_positions"]
                or client_position in row["external_positions"],
                axis=1,
            )
            for client_position in all_positions
        }
    )

    df = df.join(df_client_position)

    df["role"] = df["role"].apply(literal_eval)
    all_roles = set()
    for roles in df["role"]:
        if len(roles) == 1:
            all_roles.update(roles)

    df_role = pd.DataFrame(
        {role: df["role"].apply(lambda roles: role in roles) for role in all_roles}
    )

    df = df.join(df_role)

    df.drop(
        columns=[
            "Unnamed: 0",
            "client_positions",
            "external_positions",
            "date",
            "title",
            "patch",
            "changes",
            "be",
            "rp",
            "skill_i",
            "skill_q",
            "skill_w",
            "skill_e",
            "skill_r",
            "skills",
            "fullname",
            "nickname",
            "selection_radius",
            "pathing_radius",
            "selection_height",
        ],
        inplace=True,
    )

    df["apiname"] = df["apiname"].str.lower()

    df_role = pd.json_normalize(df["role"])
    df = df.drop(columns=["role"]).join(df_role)

    operations = []
    for record in df.to_dict("records"):
        operations.append(
            UpdateOne(
                {"id": record["id"]},
                {"$set": record},
                upsert=True,
            )
        )

    if operations:
        CHAMPIONS.bulk_write(operations)


def make_request(url: str) -> requests.Response | None:
    print("Waiting...")
    while not can_make_request():
        time.sleep(0.5)
    try:
        print("Fetching...")
        response = requests.get(url)
        print("Fetched")
    except:
        print("An exception occurred during fetch")
        pass
        return None
    REQUESTS_HISTORY.append(time.time())
    save_request_history()
    return response


def can_make_request() -> bool:
    now = time.time()
    REQUESTS_HISTORY[:] = [
        timestamp for timestamp in REQUESTS_HISTORY if now - timestamp < 120
    ]
    if len(REQUESTS_HISTORY) >= MAX_REQUESTS_PER_2_MINUTES:
        return False
    if (
        len([timestamp for timestamp in REQUESTS_HISTORY if now - timestamp < 1])
        >= MAX_REQUESTS_PER_SECOND
    ):
        return False
    return True


def get_puuid(
    gameName: str, tagLine: str, region: Puuid_region = Puuid_region.EUROPE
) -> str | None:
    url = f"https://{region.name}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={RIOT_KEY}"
    response = make_request(url)
    if response.status_code == 200:
        return response.json().get("puuid")
    else:
        print("Response:", response.text)
        return None


def get_matches(
    region: Match_region,
    type: Match_type,
    puuid: str,
    start: int,
    count: int,
    match_ids_count: int = 0,
) -> None:
    count_param = count
    if count >= 100:
        count_param = 100
    url = f"https://{region.name}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type={type.name.lower()}&start={start}&count={count_param}&api_key={RIOT_KEY}"
    if match_ids_count < count:
        response = make_request(url)
        if response:
            match_ids = response.json()
            match_ids_count += len(match_ids)
            get_match_results(region=region, match_ids=match_ids)
            get_matches(
                region, type, puuid, start + count_param, count, match_ids_count
            )


def get_match_results(region: Match_region, match_ids: List[str]) -> None:
    for match_id in match_ids:
        if MATCHES.find_one({"metadata.matchId": match_id}):
            continue
        url = f"https://{region.name}.api.riotgames.com//lol/match/v5/matches/{match_id}?api_key={RIOT_KEY}"
        response = make_request(url)
        if response.status_code == 200:
            match_data = response.json()
            MATCHES.insert_one(match_data)
        else:
            print("Response:", response.text)


def download_matches_data(
    gameName: str,
    tagLine: str,
    start: int = 0,
    count: int = 100,
    match_type: Match_type = Match_type.RANKED,
    match_region: Match_region = Match_region.EUROPE,
    puuid_region: Puuid_region = Puuid_region.EUROPE,
):

    count -= int(count / MAX_REQUESTS_PER_2_MINUTES)

    puuid = get_puuid(region=puuid_region, gameName=gameName, tagLine=tagLine)
    get_matches(
        region=match_region,
        type=match_type,
        puuid=puuid,
        start=start,
        count=count,
    )


def evaluate(gameName, tagLine):
    puuid = get_puuid(gameName, tagLine)
    cursor = list(
        MATCHES.aggregate(
            [
                {"$match": {"info.participants.puuid": puuid}},
                {
                    "$project": {
                        "participant": {
                            "$arrayElemAt": [
                                {
                                    "$filter": {
                                        "input": "$info.participants",
                                        "as": "p",
                                        "cond": {"$eq": ["$$p.puuid", puuid]},
                                    }
                                },
                                0,
                            ]
                        }
                    }
                },
            ]
        )
    )

    df = pd.DataFrame([doc["participant"] for doc in cursor if "participant" in doc])

    df_challenges = pd.json_normalize(df["challenges"])
    df_challenges.rename(
        columns={
            "killingSprees": "challenges_killingSprees",
            "turretTakedowns": "challenges_turretTakedowns",
        },
        inplace=True,
    )
    df = df.drop(columns=["challenges"], inplace=True)

    df = pd.read_csv("data/matches_data_prepared.csv")
    df["champLevelPerMinute"] = df["champLevel"] / (df["timePlayed"] / 60)
    df["damageDealtToBuildingsPerMinute"] = df["damageDealtToBuildings"] / (
        df["timePlayed"] / 60
    )
    df["neutralObjectivesTakedowns"] = (
        df["riftHeraldTakedowns"]
        + df["dragonTakedowns"]
        + df["voidMonsterKill"]
        + df["baronTakedowns"]
    )
    df["effectiveHealAndShieldingPerMinute"] = df["effectiveHealAndShielding"] / (
        df["timePlayed"] / 60
    )
    df["totalTimeCCDealtPerMinute"] = df["totalTimeCCDealt"] / (df["timePlayed"] / 60)
    df["damageTakenPerDeath"] = df["totalDamageTaken"] / np.where(
        df["deaths"] > 0, df["deaths"], 1
    )
    df["quadraKills"] -= df["pentaKills"]
    df["tripleKills"] -= df["quadraKills"]
    df["doubleKills"] -= df["tripleKills"]

    df = df[
        [
            "championId",
            "championName",
            "win",
            "kda",
            "doubleKills",
            "tripleKills",
            "quadraKills",
            "pentaKills",
            "damagePerMinute",
            "goldPerMinute",
            "earlyLaningPhaseGoldExpAdvantage",
            "killParticipation",
            "champLevelPerMinute",
            "damageDealtToBuildingsPerMinute",
            "neutralObjectivesTakedowns",
            "effectiveHealAndShieldingPerMinute",
            "totalTimeCCDealtPerMinute",
            "damageTakenPerDeath",
            "visionScorePerMinute",
            "teamPosition",
        ]
    ]

    df.dropna(axis=0, inplace=True)

    cols = [
        col
        for col in df.columns
        if col not in ["championName", "teamPosition", "championId"]
    ]

    weights = utils.calculate_weights(
        df,
        group_by="teamPosition",
        target="win",
        excluded=["championName", "championId"],
    )

    df["score"] = 0.0
    for index, row in df.iterrows():
        for col in cols:
            if not pd.isna(row[col]):
                teamPosition = row["teamPosition"]
                if teamPosition == "TOP":
                    weight = weights["TOP"].get(col, 1.0)
                elif teamPosition == "JUNGLE":
                    weight = weights["JUNGLE"].get(col, 1.0)
                elif teamPosition == "MIDDLE":
                    weight = weights["MIDDLE"].get(col, 1.0)
                elif teamPosition == "BOTTOM":
                    weight = weights["BOTTOM"].get(col, 1.0)
                elif teamPosition == "UTILITY":
                    weight = weights["UTILITY"].get(col, 1.0)
                else:
                    weight = 1.0
                df.at[index, "score"] += row[col] * weight

    games_count = df[["championName", "teamPosition"]].value_counts().reset_index()
    df = df.groupby(["championName", "teamPosition"]).mean().reset_index()
    df = df.merge(games_count, on=["championName", "teamPosition"])

    cursor = list(CHAMPIONS.aggregate([]))

    champions = pd.json_normalize(cursor)

    df.set_index("championId", inplace=True)
    champions.set_index("id", inplace=True)

    df = champions.join(df)

    df.reset_index(inplace=True)

    df["count"] = df["count"].fillna(0)

    operations = []
    for record in df.to_dict("records"):
        operations.append(
            UpdateOne(
                {"puuid": puuid, "championId": record["id"]},
                {
                    "$set": {
                        "score": record["score"],
                        "count": record["count"],
                    }
                },
                upsert=True,
            )
        )

    if operations:
        SCORES.bulk_write(operations)


def linear_regression(gameName, tagLine):

    puuid = get_puuid(gameName, tagLine)

    cursor = list(
        SCORES.aggregate(
            [
                {"$match": {"puuid": puuid}},
                {
                    "$lookup": {
                        "from": "Champions",
                        "localField": "championId",
                        "foreignField": "id",
                        "as": "result",
                    }
                },
            ]
        )
    )
    df = pd.DataFrame(cursor)

    df.drop(columns="_id", inplace=True)

    df["result"] = df["result"].apply(
        lambda x: x[0] if isinstance(x, list) and x else {}
    )

    result_df = pd.json_normalize(df["result"])
    df = pd.concat([df.drop(columns=["result"]), result_df], axis=1)

    df.drop(columns=["_id", "id"], inplace=True)

    metadata = df[["puuid", "apiname"]]
    df_features = df.drop(columns=["puuid", "apiname"])

    df_features = pd.get_dummies(df_features)
    df_features = df_features.replace({True: 1, False: 0})
    df = pd.concat([metadata, df_features], axis=1)

    df_unscored = df[df["score"].isna()].drop(columns=["score"])
    df_scored = df[df["score"].notna()].copy()

    y = df_scored["score"]
    X = df_scored.drop(columns=["score", "apiname", "championId", "puuid"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE: {mae:.4f}")

    X_unscored = df_unscored.drop(columns=["apiname", "championId", "puuid"])

    X_unscored_scaled = scaler.transform(X_unscored)
    predicted_scores = model.predict(X_unscored_scaled)

    df_unscored["score"] = predicted_scores

    operations = []
    for record in df_unscored.to_dict("records"):
        operations.append(
            UpdateOne(
                {"puuid": puuid, "championId": record["championId"]},
                {
                    "$set": {
                        "score": record["score"],
                        "count": 0,
                    }
                },
                upsert=True,
            )
        )

    if operations:
        SCORES.bulk_write(operations)


def test_db():
    try:
        CLIENT.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


def get_scores(gameName, tagLine):
    puuid = get_puuid(gameName, tagLine)

    cursor = list(
        SCORES.aggregate(
            [
                {"$match": {"puuid": puuid}},
                {
                    "$lookup": {
                        "from": "Champions",
                        "localField": "championId",
                        "foreignField": "id",
                        "as": "result",
                    }
                },
            ]
        )
    )

    df = pd.DataFrame(cursor)

    df.drop(columns="_id", inplace=True)

    df["result"] = df["result"].apply(
        lambda x: x[0] if isinstance(x, list) and x else {}
    )

    result_df = pd.json_normalize(df["result"])
    df = pd.concat([df.drop(columns=["result"]), result_df], axis=1)

    df = df[["apiname", "score", "count"]]

    df.sort_values(by="score", ascending=False, inplace=True)

    return df


if __name__ == "__main__":

    # test_db()

    # TODO - periodically?
    # download_champion_data(force_download=True)

    # download_matches_data(gameName="julusia42069", tagLine="eune", count=100)

    # evaluate(gameName="julusia42069", tagLine="eune")

    # linear_regression(gameName="julusia42069", tagLine="eune")

    utils.print_df(get_scores(gameName="julusia42069", tagLine="eune"))

    # test_db()
