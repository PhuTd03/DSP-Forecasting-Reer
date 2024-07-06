import os
import pandas as pd

if __name__ == '__main__':
    for file in os.listdir('raw_data'):
        print(file)
        df = pd.read_csv('raw_data/' + file)
        print(df.describe())