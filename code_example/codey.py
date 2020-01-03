from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
#from sklearn.svm import SVC


# DATA PROCESSING
def pre_process(df):
    X_train, X_test, y_train, y_test = train_test_split(df.drop(df.columns[-1], axis=1), df.iloc[:, -1], random_state=42)
    imputer = SimpleImputer()
    scaler = StandardScaler()
    X_train = scaler.fit_transform(imputer.fit_transform(X_train))
    X_test = scaler.transform(imputer.transform(X_test))
    y_train = LabelEncoder().fit_transform(y_train)
    return  X_train, X_test, y_train, y_test


def create_model(X_train, X_test, y_train, y_test):
    #ANALYTICAL MODELING
    pipe = Pipeline([
      ('feature_selection', SelectFromModel(LinearSVC(max_iter=100000))),
      ('prediction', LinearRegression())
    ])
    #pipe=model_def = SVC(kernel='linear')

    return pipe
