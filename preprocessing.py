import json
import pandas as pd
# from lightgbm import LGBMClassifier

from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, FunctionTransformer

CSV_FILE_NAME = "data.csv"
JSON_FILE_NAME = 'OLD.json'


def load_dataframe_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def save_relevant_features_to_csv(df):
    df = df.loc[:, ['job_id', 'company', 'job_title_', 'duration', 'job_location', 'country',
                    'job_description', 'cover_letter_required?', 'important_urls']]

    # update duration formatting to account for range
    df['duration_min'] = df['duration'].apply(lambda x : x.split(' or')[0] + ' months' if ' or' in x else x)
    df['duration_max'] = df['duration'].apply(lambda x: x.split('or ')[1] if 'or ' in x else x)
    df.drop(columns="duration", inplace=True)

    # update cover_letter_required to be binary feature
    df['cover_letter_required?'] = df['cover_letter_required?'].apply(lambda x: 1 if x == 'Yes' else 0)

    df.to_csv(CSV_FILE_NAME, header=df.columns.to_list(), index=False)


def preprocess_from_csv():
    df = pd.read_csv(CSV_FILE_NAME)

    # assign feature categories
    categorical_features = ['company', 'job_location', 'country']
    # TODO deal with job location and country -> want to make them have only certain categories (top places)
    short_text_feature = ['job_title_']
    text_feature = ['job_description']
    # TODO figure out how to transform text data
    ordinal_features = ["duration_min", "duration_max"]
    pass_feature = ['cover_letter_required?']
    drop_features = ['job_id', 'important_urls']

    # assign ordinal levels
    duration_levels = ["4 months", "8 months", "12 months", "16 months"]

    ordinal_transformer = OrdinalEncoder(categories=[duration_levels, duration_levels], dtype=int)

    categorical_transformer = make_pipeline(
        SimpleImputer(strategy="constant", fill_value="missing"),
        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
    )

    # Create text transformers that can handle DataFrame input
    def text_transformer_wrapper(transformer):
        return FunctionTransformer(
            lambda x: transformer.fit_transform(x.iloc[:, 0]).toarray()
        )

    short_text_transformer = make_pipeline(
        text_transformer_wrapper(CountVectorizer(max_features=500))
    )

    text_transformer = make_pipeline(
        text_transformer_wrapper(TfidfVectorizer(max_features=1000))
    )

    preprocessor = make_column_transformer(
        (ordinal_transformer, ordinal_features),
        (categorical_transformer, categorical_features),
        (short_text_transformer, short_text_feature),
        (text_transformer, text_feature),
        ("passthrough", pass_feature),
        ("drop", drop_features),
    )

    X_trans = preprocessor.fit_transform(df)
    # print(preprocessor.get_feature_names_out())
    print(X_trans)
    # pipe = make_pipeline(preprocessor, LGBMClassifier())


def main():
    full_df = load_dataframe_from_json(JSON_FILE_NAME)
    save_relevant_features_to_csv(full_df)

    # preprocess features
    preprocess_from_csv()


if __name__ == "__main__":
    main()
