from flask import Flask, json, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import os
import string, random, socket

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test-steam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

def scheduler():
    print("Scheduler")


@app.route("/")
def Hello():
    return "hello, flask"

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        schedule = BackgroundScheduler()
        schedule.add_job(scheduler, 'cron', second=0)
        schedule.start()

    app.run(debug=True, port=5001)
    #app.run(host='0.0.0.0')


#
# for testing
#

#@app.route("/ma")
#def marshmallow():
#    todos = Todo.query.order_by(Todo.date_created).all()
#    return jsonify(todos_schema.dump(todos))

#@app.route("/mountain")
#def helloWorld():
#    tasks = Todo.query.order_by(Todo.content).all()
#    return render_template('index.html', tasks=tasks)

#@app.route("/create")
#def createTable():
#    return db.create_all()

#@app.route("/api")
#def api():
#    tasks = Todo.query.order_by(Todo.date_created).all()
#    return jsonify(json_list = [i.serialize for i in tasks])


