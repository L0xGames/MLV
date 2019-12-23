import os

from flask import Flask, render_template, request, flash, make_response
import pandas as pd

app = Flask(__name__)
# TODO new secret key
app.secret_key = 'super secret key'
dataframe = None
file_size=None
file_name=None


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        data_upload=None
        code_upload=None
        #check which button is pressed by excepting keyerror
        try:
            data_upload = request.files["data_upload"]
            code_upload = request.files["code_upload"]
        except:
            app.logger.info("Some file uploaded")
        app.logger.info(data_upload)
        app.logger.info(code_upload)
        #Check which file is uplaoded
        if data_upload:
            #check with file extension for right file format (probaly the right)
            if data_upload.filename.lower().endswith('.csv'):
                #save file to uploads
                file_path = os.path.join("uploads", data_upload.filename)
                data_upload.save(file_path)
                #read file to dataframe
                global dataframe
                dataframe = pd.read_csv(file_path)
                app.logger.info('CSV WRITTEN INTO DATAFRAME')
                flash("Erfolgreich Hochgeladen", "csvsuc")
            else:
                #flash error for wrong file format
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
            else:
                # flash error for wrong file format
                app.logger.info('Wrong file format for CODE')
                flash("Falsches Dateiformat. Lade eine py Datei hoch!", "errorfileformatpy")

        return render_template("home.html")
    return render_template('home.html')

@app.route('/api/csv',methods=["GET"])
def get_cvs():
    return make_response("This is a test", 200)




if __name__ == '__main__':
    app.run()
