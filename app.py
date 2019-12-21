import os

from flask import Flask, render_template, request, flash
import pandas as pd

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


app = CustomFlask(__name__)
# TODO new secret key
app.secret_key = 'super secret key'
dataframe = None


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        app.logger.info(request.form)
        file = request.files["file"]
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        # Check if csv
        if file.filename.lower().endswith('.csv'):
            global dataframe
            dataframe = pd.read_csv(file_path)
            app.logger.info('CSV WRITTEN INTO DATAFRAME')
            flash("Erfolgreich Hochgeladen", "csvsuc")
        elif file.filename.lower().endswith('.py'):
            app.logger.info('PY file uploaded')
            flash("Erfolgreich Hochgeladen", "pysuc")
        else:
            app.logger.info('Wrong file format')
            flash("Falsches Dateiformat", "errorfileformat")

        return render_template("home.html")
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
