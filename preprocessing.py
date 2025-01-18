import json
import pandas as pd


def load_dataframe_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def main():
    df = load_dataframe_from_json('OLD.json')
    print(df.head())
    df.to_csv('test.csv', header=False, index=False)


if __name__ == "__main__":
    main()
