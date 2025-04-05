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
from sklearn.metrics import mean_squared_error, mean_absolute_error

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


def download_champion_data(force_download: bool = False):

    path = kagglehub.dataset_download(
        "laurenainsleyhaines/25-s1-3-league-of-legends-champion-data-2025",
        force_download=force_download,
    )
    print("Path to dataset files:", path)

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    for file_name in os.listdir(path):
        df = pd.read_csv(os.path.join(path, file_name))
        df.to_csv(os.path.join(output_dir, "champion_data.csv"), index=False)


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

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "champion_data_prepared.csv"), index=False)


def get_puuid(region: Puuid_region, gameName: str, tagLine: str) -> str | None:
    url = f"https://{region.name}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={RIOT_KEY}"
    response = requests.get(url)
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
    limit: int,
    match_ids: List[str],
) -> List[str]:
    if len(match_ids) + count <= limit:
        url = f"https://{region.name}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type={type.name.lower()}&start={start}&count={count}&api_key={RIOT_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            match_ids += response.json()
            match_ids = get_match_ids(
                region, type, puuid, start + count, count, limit, match_ids
            )
        else:
            print("Error:", response.text)
            return match_ids
    return match_ids


def get_match_results(
    region: Match_region, match_ids: List[str], puuid: str
) -> List[Dict]:
    match_results = []
    for match_id in match_ids:
        url = f"https://{region.name}.api.riotgames.com//lol/match/v5/matches/{match_id}?api_key={RIOT_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            participants = response.json().get("info", {}).get("participants", [])
            for participant in participants:
                if participant.get("puuid") == puuid:
                    match_results.append(participant)
        else:
            print("Error:", response.text)
            return match_results
    return match_results


def save_match_data(match_results: List[Dict]) -> None:
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "matches_data.json"), "w") as f:
        json.dump(match_results, f, indent=4)


# TODO - more than 100 requests
def download_matches_data(
    gameName: str,
    tagLine: str,
    start: int = 0,
    count: int = 100,
    limit: int = 100,
    match_type: Match_type = Match_type.RANKED,
    match_region: Match_region = Match_region.EUROPE,
    puuid_region: Puuid_region = Puuid_region.EUROPE,
):
    puuid = get_puuid(region=puuid_region, gameName=gameName, tagLine=tagLine)
    match_ids = get_match_ids(
        region=match_region,
        type=match_type,
        puuid=puuid,
        start=start,
        count=count,
        limit=limit,
        match_ids=[],
    )
    match_results = get_match_results(
        region=match_region, match_ids=match_ids, puuid=puuid
    )
    save_match_data(match_results)


def prepare_matches():

    df = pd.read_json("data/matches_data.json")

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

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "matches_data_prepared.csv"), index=False)


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

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    df_grouped.to_csv(
        os.path.join(output_dir, "matches_data_scored_grouped.csv"), index=False
    )

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

    df.to_csv(os.path.join(output_dir, "matches_data_scored.csv"), index=False)

    df = df[["score"]].join(champions)

    df.reset_index(inplace=True)

    df.sort_values(by="score", ascending=False, inplace=True)
    df_grouped.sort_values(by="score", ascending=False, inplace=True)

    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "champion_data_scored.csv"), index=False)

    return df, df_grouped


def linear_regression():
    df = pd.read_csv("data/champion_data_scored.csv")
    df_role = pd.json_normalize(df["role"])
    df = df.drop(columns=["role"]).join(df_role)

    # df_championName = df[["championName"]]
    df = pd.get_dummies(df.drop(columns=["championName"]))
    # df = pd.concat([df_championName, df], axis=1)

    df.replace({True: 1, False: 0}, inplace=True)

    y = df["score"]
    X = df.drop(columns=["score"])

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


if __name__ == "__main__":

    # TODO - periodically?
    download_champion_data(force_download=True)
    prepare_champions()

    # download_matches_data(gameName="julusia42069", tagLine="eune")
    # prepare_matches()

    df, df_grouped = evaluate()
    print(df_grouped.head(50))

    linear_regression()
