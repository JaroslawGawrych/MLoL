import pandas as pd
import numpy as np
from scipy.stats import zscore


def evaluate():

    df = pd.read_csv("data/prepared_matches_data.csv")
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

    df.drop(
        columns=[
            "timePlayed",
            "champLevel",
            "baronTakedowns",
            "voidMonsterKill",
            "dragonTakedowns",
            "riftHeraldTakedowns",
            "totalDamageTaken",
            "deaths",
            "damageDealtToBuildings",
            "effectiveHealAndShielding",
            "totalTimeCCDealt",
        ],
        inplace=True,
    )

    # TODO - games played
    df = df.groupby(["championName"]).mean().reset_index()

    cols = [col for col in df.columns if col != "championName"]
    df[cols] = df[cols].apply(zscore)

    champions = pd.read_csv("data/champion_data.csv")

    df["score"] = 0
    for col in df[cols]:
        df["score"] += df[col]

    df.set_index("championName", inplace=True)
    champions.set_index("apiname", inplace=True)

    champions = champions.join(df["score"])

    champions.sort_values(by="score", ascending=False, inplace=True)

    print(champions.head())


if __name__ == "__main__":
    evaluate()
