import pandas as pd
import utils

def evaluate():
    df = pd.read_csv('data/prepared_matches_data.csv')
    utils.print_df(df)    

if __name__ == '__main__':
    evaluate()