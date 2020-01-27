import ast
import importlib
import os
import time
import matplotlib.pyplot as plt
import mpld3
import pandas as pd
from flask import Flask, render_template, request, flash, make_response, jsonify
from hurry.filesize import size
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from yellowbrick.classifier import ClassPredictionError, ConfusionMatrix
from yellowbrick.features import Manifold
from yellowbrick.regressor import PredictionError, ResidualsPlot

app = Flask(__name__)
app.secret_key = 'super secret key'
dataframe = None
file_size = None
file_name = None
file_pathf = None
functions = None
model_def = None
toggle = False
ML_ALG = None
X_train = None
X_test = None
y_train = None
y_test = None
y_pred = None
# 0 for regression and 1 for classification ALG
ML_ALG_nr = None
Enc = None


# seperate js and html parts from generated html
def preprocess_html(html_list):
    all_htmls = []
    for html in html_list:
        js_html = {}
        index = html.find("<script>")
        up = html[:index]
        js_html["html"] = up
        index2 = html.find("</script>")
        down = html[index + 8:index2]
        js_html["js"] = down
        all_htmls.append(js_html)
    return all_htmls


# Generate Plots with yellowbrick and mpld3
def get_plots():
    all_plots = []
    # FEATURE Visualization

    # Instantiate the visualizer
    plt.figure(figsize=(3.5, 3.5))
    viz = Manifold(manifold="tsne")
    # Fit the data to the visualizer
    viz.fit_transform(X_train, y_train)
    # save to html
    fig = plt.gcf()
    some_htmL = mpld3.fig_to_html(fig)
    all_plots.append("<h4 align='center'>Manifold Visualization</h4>" + some_htmL)
    # clear plot
    plt.clf()

    if ML_ALG_nr == 1:
        # classification

        # Check if we can get the classes
        classes = None
        try:
            classes = list(Enc.inverse_transform(model_def.classes_))
        except ValueError as e:
            app.logger.info(e)

        if classes is not None:
            # Instantiate the classification model and visualizer
            visualizer = ClassPredictionError(DecisionTreeClassifier(), classes=classes)
            # Fit the training data to the visualizer
            visualizer.fit(X_train, y_train)
            # Evaluate the model on the test data
            visualizer.score(X_test, y_test)
            # save to html
            fig = plt.gcf()
            some_htmL = mpld3.fig_to_html(fig)
            all_plots.append("<h4 align='center'>Class Prediction Error</h4>" + some_htmL)
            # clear plot
            plt.clf()
            # The ConfusionMatrix visualizer taxes a model
            cm = ConfusionMatrix(model_def, classes=classes)
            cm = ConfusionMatrix(model_def, classes=classes)
            # Fit fits the passed model. This is unnecessary if you pass the visualizer a pre-fitted model
            cm.fit(X_train, y_train)
            # To create the ConfusionMatrix, we need some test data. Score runs predict() on the data
            # and then creates the confusion_matrix from scikit-learn.
            cm.score(X_test, y_test)
            # save to html
            fig = plt.gcf()
            some_htmL = mpld3.fig_to_html(fig)
            all_plots.append("<h4 align='center'>Confusion Matrix</h4>" + some_htmL)
            # clear plot
            plt.clf()

        return all_plots

    elif ML_ALG_nr == 0:
        # regression

        # Instantiate the linear model and visualizer
        visualizer = PredictionError(model_def, identity=True)
        visualizer.fit(X_train, y_train)  # Fit the training data to the visualizer
        visualizer.score(X_test, y_test)  # Evaluate the model on the test data
        # save to html
        fig = plt.gcf()
        some_htmL = mpld3.fig_to_html(fig)
        all_plots.append("<h4 align='center'>Prediction Error Plot</h4>" + some_htmL)
        # clear plot
        plt.clf()

        # Instantiate the model and visualizer
        visualizer = ResidualsPlot(model_def)
        visualizer.fit(X_train, y_train)  # Fit the training data to the visualizer
        visualizer.score(X_test, y_test)
        # save to html
        fig = plt.gcf()
        some_htmL = mpld3.fig_to_html(fig)
        all_plots.append("<h4 align='center'>Residuals Plot</h4>" + some_htmL)
        # clear plot
        plt.clf()

        return all_plots


# Helper function to get the first 5 rows from the dataframe
def extcsv_helper():
    # get headers and put them in dicts
    dicts = [dict(), dict(), dict(), dict(), dict()]
    headers = []
    for i in range(0, 5):
        for num, head in enumerate(dataframe.iloc[0].index):
            if isinstance(dataframe.iloc[i][num], str):
                dicts[i][head] = str(dataframe.iloc[i][num])
            else:
                dicts[i][head] = str(round(dataframe.iloc[i][num], 2))
    app.logger.info(dicts)
    return dicts


# Parse code from file and get func names
def parse_code():
    # Spezifikation Code: Der Code enthält 2 Funktionen: Einer zum preprocessen und der andere zur Modeldefinition
    # Die Reihenfolge ist: 1.testsplit 2.Modeldef
    # Dies ist wichtig da wir hier die Funktionen mit Hilfe des ast auslesen und von der Reihenfolge ausgehen
    # Außerdem kriegen die Funktionen folgene Parameter: Test_split(dataframe) und Modeldef(X_train, X_test, y_train, y_test)
    # Folgende Rückgabewerte gibts für die Fkt.: Test_split=>dataframe,Encoder und Modeldef=>modeldef,int: Klassifikationstyp
    file = open(file_pathf, 'r')
    funcs = []
    text = file.read()
    p = ast.parse(text)
    # Create AST
    node = ast.NodeVisitor()
    # GET funcs with AST
    for node in ast.walk(p):
        if isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
    return funcs


# simple helper function to get filename
def parse_file_name():
    base = os.path.basename(file_pathf)
    os.path.splitext(base)
    return os.path.splitext(base)[0]


# Route to fit the model and send back the results (actual model training)
@app.route('/api/training', methods=["GET"])
def training():
    global y_pred
    # Check if model_def and dataframe available
    if (model_def is not None) and (isinstance(dataframe, pd.DataFrame)):
        f1 = None
        ajax = {}
        # model fitting
        start_train = time.time()
        try:
            model_def.fit(X_train, y_train)
        except ValueError as e:
            app.logger.info(e)
            return make_response("Error", 404)
        stop_train = time.time()
        train_time = stop_train - start_train
        # testing
        start_test = time.time()
        y_pred = model_def.predict(X_test)
        stop_test = time.time()
        test_time = stop_test - start_test
        # accuracy
        result = r2_score(y_test, y_pred)
        app.logger.info(result)
        # if Classification alg: Add f1score
        if ML_ALG_nr == 1:
            f1 = f1_score(y_test, y_pred, average='weighted')
            app.logger.info(f1)
        # get all plots for visualization
        htmls = get_plots()
        # preprocess htmls
        preprocessed_html = preprocess_html(htmls)
        # pack everything to dict for sending back to frontend
        ajax["f1"] = f1
        ajax["htmls"] = preprocessed_html
        ajax["result"] = result
        ajax["train_time"] = train_time
        ajax["test_time"] = test_time
        return make_response(jsonify(ajax), 200)
    return make_response("wo", 200)


# Home ROUTE
@app.route('/', methods=["GET", "POST"])
def hello_world():
    global toggle
    toggle = False
    if request.method == "POST":
        app.logger.info(request.files)
        data_upload = None
        code_upload = None
        # check which button is pressed by excepting keyerror
        try:
            data_upload = request.files["data_upload"]
        except KeyError:
            app.logger.info("Not a data file uploaded")

        try:
            code_upload = request.files["code_upload"]
        except KeyError:
            app.logger.info("not a code file uploaded")
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
                global file_pathf
                file_pathf = file_path
                # parse funcs from code
                global functions
                try:
                    functions = parse_code()
                except:
                    app.logger.info("There was an error in your uploaded Code. Please check...")
                    flash("There was an error in your uploaded Code. Please check...", "errorfileformatpy")
                    return render_template("home.html")
                flash("Erfolgreich Hochgeladen", "pysuc")
            else:
                # flash error for wrong file format
                app.logger.info('Wrong file format for CODE')
                flash("Falsches Dateiformat. Lade eine py Datei hoch!", "errorfileformatpy")

        return render_template("home.html")
    return render_template('home.html')


# ROUTE GET basic csv info like filename,file size rows and cols
@app.route('/api/csvinfo', methods=["GET"])
def get_csvinfo():
    if not (isinstance(dataframe, pd.DataFrame)):
        return make_response("No dataframe available", 404)
    rows, cols = dataframe.shape
    return make_response(jsonify([file_name, file_size, rows, cols]), 200)


# ROUTE GET extended CSV infos: first 5 elements
@app.route('/api/csvtable', methods=["GET"])
def get_csvtable():
    if not (isinstance(dataframe, pd.DataFrame)):
        return make_response("No dataframe available", 404)
    result = extcsv_helper()
    return make_response(jsonify(result), 200)


# ROUTE POST:set the global toggle for automatic/manual switch
@app.route('/api/toggle', methods=['POST'])
def toggle():
    js_string = str(request.data)
    global toggle
    if js_string.find("t") >= 0:
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


# ROUTE to define model and preprocess data
@app.route('/api/def', methods=['POST'])
def defining():
    app.logger.info("start training")
    app.logger.info(toggle)
    # check if dataframe exists
    if isinstance(dataframe, pd.DataFrame) or True:
        global model_def
        global X_train, X_test, y_train, y_test
        global ML_ALG_nr
        global Enc
        if toggle:
            # split original dataframe to tessplit and choose one of ML Algorithms depending on user selection
            if ML_ALG is not None:
                if ML_ALG == 0:
                    ML_ALG_nr = 1
                    model_def = SVC(kernel='linear')
                elif ML_ALG == 1:
                    ML_ALG_nr = 0
                    model_def = LinearRegression(normalize=True)
                elif ML_ALG == 2:
                    ML_ALG_nr = 1
                    model_def = MLPClassifier(hidden_layer_sizes=(13, 13, 13), max_iter=10000)
                elif ML_ALG == 3:
                    ML_ALG_nr = 1
                    model_def = DecisionTreeClassifier()
                elif ML_ALG == 4:
                    ML_ALG_nr = 0
                    model_def = RandomForestRegressor(n_estimators=1000, random_state=42)
                else:
                    app.logger.error("ML ALG Code unknown")
                    return make_response("ML ALG Code unknown", 404)
            # preprocess
            X_train, X_test, y_train, y_test = train_test_split(dataframe.drop(dataframe.columns[-1], axis=1),
                                                                dataframe.iloc[:, -1], random_state=42)
            Enc = LabelEncoder()
            y_train = Enc.fit_transform(y_train)
            y_test = Enc.fit_transform(y_test)
            return make_response("finished", 200)
        else:
            if (os.path.exists(file_pathf) and functions is not None):
                # parse filename
                module_name = parse_file_name()
                # import module by filename and path (module_name)
                spec = importlib.util.spec_from_file_location(module_name, file_pathf)
                my_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(my_module)
                # my_module = importlib.import_module(module_name)
                importlib.invalidate_caches()
                # call preprocess method with name as a string from functions list functions[0]=preprocess
                # functions[1]=model def.
                training_splitter = getattr(my_module, functions[0])
                # save resulting training split in global vars
                X_train, X_test, y_train, y_test, Enc = training_splitter(dataframe)
                # Use second function for model definition functions[1]=model def.
                model_init = getattr(my_module, functions[1])
                # save resulting model definition in global var model_def
                model_def, ML_ALG_nr = model_init(X_train, X_test, y_train, y_test)
                return make_response("finished", 200)
    return make_response("no df", 404)


if __name__ == '__main__':
    app.run()
