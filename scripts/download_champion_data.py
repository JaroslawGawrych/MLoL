import os
import pandas as pd
import kagglehub

def download_champion_data():
    path = kagglehub.dataset_download(
        'laurenainsleyhaines/25-s1-3-league-of-legends-champion-data-2025'
        # , force_download=True
        )
    print('Path to dataset files:', path)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    for file_name in os.listdir(path):
        df = pd.read_csv(os.path.join(path, file_name))
        df.to_csv(os.path.join(output_dir, "champion_data.csv"), index=False)

if __name__ == '__main__':
    download_champion_data()