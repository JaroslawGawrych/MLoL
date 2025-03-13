from typing import List
import pandas as pd
import os
from ydata_profiling import ProfileReport
import numpy as np
import json


def eda(file_path: str) -> None:
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    if file_extension == ".csv":
        df = pd.read_csv(file_path)
    elif file_extension == ".json":
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format.")

    profile_report = ProfileReport(df)

    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{file_name}_eda.html")
    profile_report.to_file(file_path)


def print_df(df):
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(df)


def weighted_mean_std(series, weights):
    mean = np.average(series, weights=weights)
    variance = np.average((series - mean) ** 2, weights=weights)
    std = np.sqrt(variance)
    return mean, std


def calculate_weights(df, group_by: str, target: str, excluded: List[str] = []):

    excluded += [group_by, target]

    cols = [col for col in df.columns if col not in excluded]

    weights = {}

    groups = df[group_by].unique()

    for group in groups:

        group_df = df[df[group_by] == group]

        correlations = group_df[cols].corrwith(group_df[target])

        correlations = correlations.fillna(0)

        correlations = (correlations - correlations.min()) / (
            correlations.max() - correlations.min()
        )

        weights[group] = correlations.to_dict()

    with open("correlation_based_weights.json", "w") as f:
        json.dump(weights, f, indent=4)

    return weights
