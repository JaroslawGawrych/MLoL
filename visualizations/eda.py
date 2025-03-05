from ydata_profiling import ProfileReport
import pandas as pd
import os

def eda():
    directory = 'visualizations'
    df = pd.read_csv('processed_data/champion_data.csv')
    profile = ProfileReport(df)
    file_path = os.path.join(directory, 'EDA.html')
    profile.to_file(file_path)

if __name__ == '__main__':
    eda()