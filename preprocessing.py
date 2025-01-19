import json
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from lightgbm import LGBMClassifier

from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
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


def get_top_categories(df, categorical_features, n=10):
    top_categories = {}
    for feature in categorical_features:
        top_categories[feature] = (df[feature].value_counts().sort_values(ascending=False).head(n).index.tolist())
    return top_categories


def preprocess_from_csv():
    df = pd.read_csv(CSV_FILE_NAME)

    # assign feature categories
    categorical_features = ['company', 'job_location', 'country']
    short_text_feature = ['job_title_']
    text_feature = ['job_description']
    ordinal_features = ["duration_min", "duration_max"]
    pass_feature = ['cover_letter_required?']
    drop_features = ['job_id', 'important_urls']

    # assign ordinal levels
    duration_levels = ["4 months", "8 months", "12 months", "16 months"]
    top_categories = get_top_categories(df, categorical_features)

    ordinal_transformer = OrdinalEncoder(categories=[duration_levels, duration_levels],
                                         dtype=int)

    categorical_transformer = make_pipeline(
        SimpleImputer(strategy="constant",
                      fill_value="https://scope.sciencecoop.ubc.ca/notLoggedIn.htm"),
        OneHotEncoder(handle_unknown="ignore",
                      categories=[top_categories[feat] for feat in categorical_features],
                      sparse_output=False),
    )

    class Count_Vectorizer(BaseEstimator, TransformerMixin):
        def __init__(self, max_features=50, stop_words='english'):
            self.max_features = max_features
            self.stop_words = stop_words
            self.vectorizer = CountVectorizer(
                max_features=max_features,
                stop_words=stop_words
            )

        def fit(self, X, y=None):
            # Extract the text series from the DataFrame
            self.vectorizer.fit(X.iloc[:, 0])
            return self

        def transform(self, X):
            # Extract the text series from the DataFrame
            return self.vectorizer.transform(X.iloc[:, 0]).toarray()

        def get_feature_names_out(self, feature_names=None):
            return self.vectorizer.get_feature_names_out()


    class Tfidf_Vectorizer(BaseEstimator, TransformerMixin):
        def __init__(self, max_features=300, stop_words='english'):
            self.max_features = max_features
            self.stop_words = stop_words
            self.vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words=stop_words
            )

        def fit(self, X, y=None):
            self.vectorizer.fit(X.iloc[:, 0])
            return self

        def transform(self, X):
            return self.vectorizer.transform(X.iloc[:, 0]).toarray()

        def get_feature_names_out(self, feature_names=None):
            return self.vectorizer.get_feature_names_out()

    short_text_transformer = make_pipeline(
        Count_Vectorizer(max_features=50, stop_words='english')
    )

    text_transformer = make_pipeline(
        Tfidf_Vectorizer(max_features=300, stop_words='english')
    )

    preprocessor = make_column_transformer(
        (ordinal_transformer, ordinal_features),
        (categorical_transformer, categorical_features),
        (short_text_transformer, short_text_feature),
        (text_transformer, text_feature),
        ("passthrough", pass_feature),
        ("drop", drop_features),
    )

    return preprocessor, df


def train_model(preprocessor, df):
    df_trans = preprocessor.fit_transform(df)
    feature_names = preprocessor.get_feature_names_out()
    # TODO - feature names are using pipelines (but functional)
    X = pd.DataFrame(df_trans, columns=feature_names)

    # train model
    model = LGBMClassifier()
    model.fit(X)
    return model


def main():
    full_df = load_dataframe_from_json(JSON_FILE_NAME)
    save_relevant_features_to_csv(full_df)

    # preprocess features
    preprocessor, df = preprocess_from_csv()

    # train model
    train_model(preprocessor, df)


if __name__ == "__main__":
    main()
