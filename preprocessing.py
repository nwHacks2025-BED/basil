import json
import pandas as pd
import warnings
from sklearn.base import BaseEstimator, TransformerMixin
from lightgbm import LGBMClassifier

from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from pymongo_fastapi_crud.routes import MongoAPI

# Repress error from deprecation for sklearn
warnings.filterwarnings('ignore', category=FutureWarning)


# JSON_TRAIN_FILE_NAME = 'OLD.json'
# JSON_TEST_FILE_NAME = 'allJobs.json'


# def load_dataframe_from_json(file_path):
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#     return pd.DataFrame(data)


def remove_irrelevant_features(df):
    df.drop(columns=["placement_term", "position_type", "work_mode", "salary_currency", "salary",
                     "job_requirements", "citizenship_requirement", "targeted_co-op_programs",
                     "application_deadline", "application_procedure", "address_cover_letter_to",
                     "application_documents_required", "special_application_instructions", 'salary_range_$',
                     'position_start_date', 'position_end_date', 'probability', 'company', 'job_location'],
            inplace=True, errors='ignore')

    # update duration formatting to account for range
    df['duration_min'] = df['duration'].apply(lambda x : x.split(' or')[0] + ' months' if ' or' in x else x)
    df['duration_max'] = df['duration'].apply(lambda x: x.split('or ')[1] if 'or ' in x else x)
    df.drop(columns="duration", inplace=True)

    # update cover_letter_required to be binary feature
    df['cover_letter_required?'] = df['cover_letter_required?'].apply(lambda x: 1 if x == 'Yes' else 0)

    return df


def get_top_categories(df, categorical_features, n=10):
    top_categories = {}
    for feature in categorical_features:
        top_categories[feature] = (df[feature].value_counts().sort_values(ascending=False).head(n).index.tolist())
    return top_categories


def make_preprocessor():
    # assign feature categories
    categorical_features = ['country'] # removed company and job_location
    short_text_feature = ['job_title_']
    text_feature = ['job_description']
    ordinal_features = ["duration_min", "duration_max"]
    pass_feature = ['cover_letter_required?']
    drop_features = ['job_id', 'important_urls']

    # assign ordinal levels
    duration_levels = ["4 months", "8 months", "12 months", "16 months"]

    ordinal_transformer = OrdinalEncoder(categories=[duration_levels, duration_levels],
                                         dtype=int)

    categorical_transformer = make_pipeline(
        SimpleImputer(strategy="constant",
                      fill_value="https://scope.sciencecoop.ubc.ca/notLoggedIn.htm"),
        OneHotEncoder(handle_unknown="ignore",
                      sparse_output=False)
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

    return preprocessor


def train_model(preprocessor, X_train, y_train):
    X_train_trans = preprocessor.fit_transform(X_train)

    feature_names = preprocessor.get_feature_names_out()

    # print transformed features (sanity check)
    df_trans = pd.DataFrame(X_train_trans, columns=feature_names)
    # df_trans.to_csv('transformed_features.csv', index=False)
    # print("saved transformed features to transformed_features.csv")

    # train model
    params = {
        'objective': 'binary',
        'boosting_type': 'gbdt',
        'learning_rate': 0.05,

        # Handle imbalance
        'is_unbalance': True,  # or use scale_pos_weight

        # Prevent overfitting
        'max_depth': 5,  # limit tree depth
        'num_leaves': 20,  # reduce from default 31
        'min_data_in_leaf': 50,  # increase from default
        'feature_fraction': 0.8,  # use 80% of features in each iteration

        # Other parameters
        'metric': 'binary_logloss',
        'verbose': -1,
        'n_estimators': 100
    }

    model = LGBMClassifier(**params)
    model.fit(X_train_trans, y_train)

    return model


def model_predict(preprocessor, model, X_test):
    # transform testing data
    X_test_trans = preprocessor.transform(X_test)

    feature_names = preprocessor.get_feature_names_out()

    # print transformed features (sanity check)
    df_trans = pd.DataFrame(X_test_trans, columns=feature_names)
    # df_trans.to_csv('transformed_features_test.csv', index=False)
    # print("saved transformed features to transformed_features_test.csv")

    predictions = model.predict_proba(X_test_trans)

    # create predictions dataframe
    predictions_df = pd.DataFrame(predictions, columns=['prob-0', 'prob-1'])
    predictions_df.drop(columns='prob-0', inplace=True)
    predictions_df.rename(columns={'prob-1': 'probability'}, inplace=True)
    predictions_df['job_id'] = X_test['job_id'].to_list()

    return predictions_df


def main():
    # create preprocessor for features
    preprocessor = make_preprocessor()

    # load training data
    # train_df = load_dataframe_from_json(JSON_TRAIN_FILE_NAME)
    train_df = pd.DataFrame(MongoAPI.get_labelled_data())
    train_df = remove_irrelevant_features(train_df)

    X_train = train_df.drop(columns=["apply"])
    y_train = train_df["apply"]

    # train model
    model = train_model(preprocessor, X_train, y_train)

    # load testing data (no target values)
    # X_test = load_dataframe_from_json(JSON_TEST_FILE_NAME).head(10)
    X_test = pd.DataFrame(MongoAPI.get_unlabelled_data())
    X_test = remove_irrelevant_features(X_test)

    # predict test data
    predictions_df = model_predict(preprocessor, model, X_test)

    # return predictions as json
    json_object = json.loads(predictions_df.to_json(orient='records'))
    
    # print(json.dumps(json_object, indent=1))
    MongoAPI.update_probabilities(json_object)


if __name__ == "__main__":
    main()
