from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
# from sklearn.svm import SVC


# DATA PROCESSING
def pre_process(df):
    X_train, X_test, y_train, y_test = train_test_split(df.drop(df.columns[-1], axis=1), df.iloc[:, -1],
                                                        random_state=42)
    Enc = LabelEncoder()
    y_train = Enc.fit_transform(y_train)
    y_test = Enc.fit_transform(y_test)

    return X_train, X_test, y_train, y_test, Enc


def create_model(X_train, X_test, y_train, y_test):
    # ANALYTICAL MODELING
    pipe = Pipeline([
        ('feature_selection', SelectFromModel(LinearSVC(max_iter=10000))),
        ('prediction', LinearRegression())
    ])
    # pipe=model_def = SVC(kernel='linear')

    # 0:regression and 1:classification
    return pipe, 0
