import os

from flask import Flask, render_template, request, flash, make_response, jsonify
from hurry.filesize import size
import pandas as pd
import os, ast
import importlib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
import time

app = Flask(__name__)
# TODO new secret key
app.secret_key = 'super secret key'
dataframe = None
file_size = None
file_name = None
file_pathf = None
model_def = None
training_split = None
toggle = False
ML_ALG = None
X_train = None
X_test = None
y_train = None
y_test = None
y_pred=None


def extcsv_helper():
    # get headers and put them in dicts
    dicts = [dict(), dict(), dict(), dict(), dict()]
    headers = []
    for i in range(0, 5):
        for num, head in enumerate(dataframe.iloc[0].index):
            dicts[i][head] = str(dataframe.iloc[i][num])
    app.logger.info(dicts)
    return dicts


def parse_code():
    # Spezifikation Code: Der Code enthält 2 Funktionen: Einer zum preprocessen und der andere zur Modeldefinition
    # Die Reihenfolge ist: 1.testsplit 2.Modeldef
    # Dies ist wichtig da wir hier die Funktionen mit Hilfe des ast auslesen und von der Reihenfolge ausgehen
    # Außerdem kriegen die Funktionen folgene Parameter: Test_split(dataframe) und Modeldef(testsplit)
    # Folgende Rückgabewerte gibts für die Fkt.: Test_split=>dataframe und Modeldef=>modeldef type
    file = open(file_pathf, 'r')
    funcs = []
    text = file.read()
    p = ast.parse(text)
    node = ast.NodeVisitor()
    for node in ast.walk(p):
        if isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
    return funcs


def parse_file_name():
    file = open(file_pathf, 'r')
    # parse oput module name
    file_name = file.name
    nameslist = file_name.split(".")
    return nameslist[:1]


# GET fitting model
@app.route('/api/training', methods=["GET"])
def training():
    if (model_def is not None) and (isinstance(dataframe, pd.DataFrame)):
        ajax={}
        #training
        start_train = time.time()
        model_def.fit(X_train, y_train)
        stop_train = time.time()
        train_time=stop_train-start_train
        #testing
        start_test=time.time()
        y_pred = model_def.predict(X_test)
        stop_test = time.time()
        test_time=stop_test-start_test
        #accuracy
        result=r2_score(y_test, y_pred)
        app.logger.info(result)
        #pack everything to dict for sending back to frontend
        ajax["result"]=result
        ajax["train_time"]=train_time
        ajax["test_time"]=test_time
        return make_response(jsonify(ajax), 200)
    return make_response("wo",200)


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        app.logger.info(request.files)
        data_upload = None
        code_upload = None
        # check which button is pressed by excepting keyerror
        try:
            data_upload = request.files["data_upload"]
            code_upload = request.files["code_upload"]
        except:
            app.logger.info("Some file uploaded")
        app.logger.info(data_upload)
        app.logger.info(code_upload)
        # Check which file is uplaoded
        if data_upload:
            # check with file extension for right file format (probaly the right)
            if data_upload.filename.lower().endswith('.csv'):
                # save file to uploads
                file_path = os.path.join("uploads", data_upload.filename)
                data_upload.save(file_path)
                # save infos
                global file_size
                global file_name
                file_size = size(os.stat(file_path).st_size)
                file_name = data_upload.filename
                # read file to dataframe
                global dataframe
                dataframe = pd.read_csv(file_path)
                app.logger.info('CSV WRITTEN INTO DATAFRAME')
                flash("Erfolgreich Hochgeladen", "csvsuc")
            else:
                # flash error for wrong file format
                app.logger.info('Wrong file format for DATA')
                flash("Falsches Dateiformat. Lade eine csv Datei hoch!", "errorfileformatcsv")

        elif code_upload:
            # check with file extension for right file format (probaly the right)
            if code_upload.filename.lower().endswith('.py'):
                # save file to uploads
                file_path = os.path.join("uploads", code_upload.filename)
                code_upload.save(file_path)
                app.logger.info('CODE UPLOADED')
                flash("Erfolgreich Hochgeladen", "pysuc")
                global file_pathf
                file_pathf = file_path
            else:
                # flash error for wrong file format
                app.logger.info('Wrong file format for CODE')
                flash("Falsches Dateiformat. Lade eine py Datei hoch!", "errorfileformatpy")

        return render_template("home.html")
    return render_template('home.html')


# GET basic csv info like filename,file size rows and cols
@app.route('/api/csvinfo', methods=["GET"])
def get_csvinfo():
    if not (isinstance(dataframe, pd.DataFrame)):
        return make_response("No dataframe available", 404)
    rows, cols = dataframe.shape
    return make_response(jsonify([file_name, file_size, rows, cols]), 200)


# GET extended CSV infos: first 5 elements
@app.route('/api/csvtable', methods=["GET"])
def get_csvtable():
    if not (isinstance(dataframe, pd.DataFrame)):
        return make_response("No dataframe available", 404)
    result = extcsv_helper()
    return make_response(jsonify(result), 200)


# POST:set the global toggle
@app.route('/api/toggle', methods=['POST'])
def toggle():
    js_string = str(request.data)
    global toggle
    if (js_string.find("t") >= 0):
        toggle = True
    else:
        toggle = False
    app.logger.info(str(toggle))
    return make_response("worked", 200)


# POST:get the selected ML ALgorithm
@app.route('/api/mlalg', methods=['POST'])
def algorithm():
    global ML_ALG
    ML_ALG = int(request.data)
    app.logger.info("User selected ML Algorithm nr : " + str(ML_ALG))
    return make_response("worked", 200)


@app.route('/api/def', methods=['POST'])
def defining():
    app.logger.info("start training")
    # check if dataframe exists
    if isinstance(dataframe, pd.DataFrame):
        global model_def
        global X_train, X_test, y_train, y_test
        if (toggle):
            # split original dataframe to tessplit and choose one of ML Algorithms depending on user selection
            #preprocess
            X_train, X_test, y_train, y_test = train_test_split(dataframe.drop(dataframe.columns[-1], axis=1), dataframe.iloc[:, -1], random_state=42)
            imputer = SimpleImputer()
            scaler = StandardScaler()
            X_train = scaler.fit_transform(imputer.fit_transform(X_train))
            X_test = scaler.transform(imputer.transform(X_test))
            y_train = LabelEncoder().fit_transform(y_train)
            if ML_ALG is not None:
                if ML_ALG == 0:
                    model_def = SVC(kernel='linear')
                    return make_response("finished", 200)
                elif ML_ALG == 1:
                    model_def = LinearRegression(normalize=True)
                    return make_response("finished", 200)
                elif ML_ALG == 2:
                    model_def = MLPClassifier(hidden_layer_sizes=(13, 13, 13), max_iter=10000)
                    return make_response("finished", 200)
                elif ML_ALG == 3:
                    model_def = DecisionTreeClassifier()
                    return make_response("finished", 200)
                elif ML_ALG == 4:
                    model_def = RandomForestRegressor(n_estimators=1000, random_state=42)
                    return make_response("finished", 200)
                else:
                    app.logger.error("ML ALG Code unknown")
                    return make_response("ML ALG Code unknown", 404)
        else:
            # parse funcs from code
            functions = parse_code()
            # parse filename
            module_name = parse_file_name()
            # import module by filename (module_name)
            my_module = importlib.import_module(module_name)
            importlib.invalidate_caches()
            # call preprocess method with name as a string from functions list functions[0]=preprocess
            # functions[1]=model def.
            training_splitter = getattr(my_module, functions[0])
            # save resulting training split in global var training_split
            X_train, X_test, y_train, y_test = training_splitter(dataframe)
            # Use second function for model definition functions[1]=model def.
            model_init = getattr(my_module, functions[1])
            # save resulting model definition in global var model_def
            model_def = model_init(training_split)
            return make_response("finished", 200)
    return make_response("no df",404)


if __name__ == '__main__':
    app.run()
