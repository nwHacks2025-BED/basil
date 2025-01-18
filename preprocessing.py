import json
import pandas as pd


def load_dataframe_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def main():
    df = load_dataframe_from_json('OLD.json')
    df = df.loc[:, ['job_id', 'company', 'job_title_', 'duration', 'job_location', 'country',
                    'job_description', 'cover_letter_required?', 'important_urls']]
    df.to_csv('data.csv', header=df.columns.to_list(), index=False)



if __name__ == "__main__":
    main()
