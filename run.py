from hemerotecaApp import app

app.config.from_pyfile('config.py')

app.run('0.0.0.0')