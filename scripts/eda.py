import pandas as pd
import os
from ydata_profiling import ProfileReport

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

    output_dir = 'visualizations'
    file_path = os.path.join(output_dir, f'{file_name}_eda.html')
    profile_report.to_file(file_path)

if __name__ == '__main__':
    eda(file_path='processed_data/champion_data.csv')
    eda(file_path='processed_data/prepared_matches_data.csv')