from ast import Dict
from typing import List
import pandas as pd
import os
from ydata_profiling import ProfileReport
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


def test_db(client):
    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
