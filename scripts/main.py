import time
import pandas as pd
import kagglehub
import requests
import os
from ast import literal_eval
from enum import Enum
from typing import List, Dict
import numpy as np
import json
from dotenv import load_dotenv
import utils
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MATCHES_DATA_PATH = os.path.join(OUTPUT_DIR, "matches_data.json")


load_dotenv()
RIOT_KEY = os.getenv("RIOT_KEY")


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
        df.to_csv(os.path.join(OUTPUT_DIR, "champion_data.csv"), index=False)


def prepare_champions():

    df = pd.read_csv("data/champion_data.csv")

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

    df.to_csv(os.path.join(OUTPUT_DIR, "champion_data_prepared.csv"), index=False)


def make_request(url: str) -> requests.Response:
    while not can_make_request():
        time.sleep(0.1)
    response = requests.get(url)
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


def get_puuid(region: Puuid_region, gameName: str, tagLine: str) -> str | None:
    url = f"https://{region.name}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={RIOT_KEY}"
    response = make_request(url)
    if response.status_code == 200:
        return response.json().get("puuid")
    else:
        print("Error:", response.text)
        return None


def get_match_ids(
    region: Match_region,
    type: Match_type,
    puuid: str,
    start: int,
    count: int,
    match_ids: List[str],
) -> List[str]:
    count_param = count
    if count > 100:
        count_param = 100
    url = f"https://{region.name}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type={type.name.lower()}&start={start}&count={count_param}&api_key={RIOT_KEY}"
    if len(match_ids) < count:
        response = make_request(url)
        if response.status_code == 200:
            match_ids += response.json()
            match_ids = get_match_ids(
                region, type, puuid, start + count, count, match_ids
            )
        else:
            print("Error:", response.text)
            return match_ids
    return match_ids


def get_match_results(region: Match_region, match_ids: List[str], puuid: str) -> None:
    for match_id in match_ids:
        url = f"https://{region.name}.api.riotgames.com//lol/match/v5/matches/{match_id}?api_key={RIOT_KEY}"
        response = make_request(url)
        if response.status_code == 200:
            participants = response.json().get("info", {}).get("participants", [])
            for participant in participants:
                if participant.get("puuid") == puuid:
                    save_match_data(participant)
        else:
            print("Error:", response.text)


def save_match_data(match_data: Dict) -> None:

    if os.path.exists(MATCHES_DATA_PATH) and os.path.getsize(MATCHES_DATA_PATH) > 0:
        with open(MATCHES_DATA_PATH, "r") as f:
            all_data = json.load(f)
    else:
        all_data = []

    all_data.append(match_data)

    with open(MATCHES_DATA_PATH, "w") as f:
        json.dump(all_data, f, indent=4)


def download_matches_data(
    gameName: str,
    tagLine: str,
    start: int = 0,
    count: int = 99,
    match_type: Match_type = Match_type.RANKED,
    match_region: Match_region = Match_region.EUROPE,
    puuid_region: Puuid_region = Puuid_region.EUROPE,
):
    if os.path.exists(MATCHES_DATA_PATH):
        open(MATCHES_DATA_PATH, "w").close()
    puuid = get_puuid(region=puuid_region, gameName=gameName, tagLine=tagLine)
    match_ids = get_match_ids(
        region=match_region,
        type=match_type,
        puuid=puuid,
        start=start,
        count=count,
        match_ids=[],
    )
    get_match_results(region=match_region, match_ids=match_ids, puuid=puuid)


def prepare_matches():

    df = pd.read_json(MATCHES_DATA_PATH)

    df_challenges = pd.json_normalize(df["challenges"])
    df_challenges.rename(
        columns={
            "killingSprees": "challenges_killingSprees",
            "turretTakedowns": "challenges_turretTakedowns",
        },
        inplace=True,
    )
    df = df.drop(columns=["challenges"]).join(df_challenges)

    df.replace({True: 1, False: 0}, inplace=True)

    df.to_csv(os.path.join(OUTPUT_DIR, "matches_data_prepared.csv"), index=False)


def evaluate():

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

    df_ungrouped = df

    cols = [col for col in df.columns if col not in ["championName", "teamPosition"]]

    weights = utils.calculate_weights(
        df_ungrouped,
        group_by="teamPosition",
        target="win",
        excluded=["championName"],
    )
    # weights = pd.read_json("weights.json")

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
    df_grouped = df.groupby(["championName", "teamPosition"]).mean().reset_index()
    df_grouped = df_grouped.merge(games_count, on=["championName", "teamPosition"])

    champions = pd.read_csv("data/champion_data_prepared.csv")

    champions.drop(
        columns=[
            "Unnamed: 0",
            "client_positions",
            "external_positions",
            "id",
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
        ],
        inplace=True,
    )

    df["championName"] = df["championName"].str.lower()
    champions["apiname"] = champions["apiname"].str.lower()

    df.set_index("championName", inplace=True)
    champions.set_index("apiname", inplace=True)

    df.to_csv(os.path.join(OUTPUT_DIR, "matches_data_scored.csv"), index=False)

    df = champions.join(df[["score"]])

    df.reset_index(inplace=True)

    df.sort_values(by="score", ascending=False, inplace=True)
    df_grouped.sort_values(by="score", ascending=False, inplace=True)

    df.to_csv(os.path.join(OUTPUT_DIR, "champion_data_scored.csv"), index=False)
    df_grouped.to_csv(
        os.path.join(OUTPUT_DIR, "matches_data_scored_grouped.csv"), index=False
    )

    return df, df_grouped


def linear_regression():
    df = pd.read_csv("data/champion_data_scored.csv")
    df_role = pd.json_normalize(df["role"])
    df = df.drop(columns=["role"]).join(df_role)

    apiname = df["apiname"]
    df_features = df.drop(columns=["apiname"])

    df_features = pd.get_dummies(df_features)
    df_features.replace({True: 1, False: 0}, inplace=True)

    df = pd.concat([apiname, df_features], axis=1)

    df_unscored = df[df["score"].isna()].drop(columns=["score"])
    df_scored = df[df["score"].notna()].copy()

    y = df_scored["score"]
    X = df_scored.drop(columns=["score", "apiname"])

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

    X_unscored = df_unscored.drop(columns=["apiname"])
    X_unscored_scaled = scaler.transform(X_unscored)
    predicted_scores = model.predict(X_unscored_scaled)

    df_unscored["score"] = predicted_scores
    df_unscored["apiname"] = apiname[df_unscored.index]

    df_scored_grouped = df_scored.groupby("apiname").mean().reset_index()

    df = pd.concat([df_scored_grouped, df_unscored], axis=0)
    df.sort_values(by="score", ascending=False, inplace=True)

    df.to_csv(os.path.join(OUTPUT_DIR, "champion_data_predicted.csv"), index=False)

    return df


if __name__ == "__main__":

    # TODO - periodically?
    # download_champion_data(force_download=True)
    # prepare_champions()

    download_matches_data(gameName="julusia42069", tagLine="eune", count=200)
    prepare_matches()

    df, df_grouped = evaluate()
    print(df_grouped.head(50))

    df = linear_regression()
    utils.print_df(df[["apiname", "score"]])
