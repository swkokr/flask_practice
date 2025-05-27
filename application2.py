from flask import Flask, json, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

import os
import string, random, socket

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test-steam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

def scheduler():
    print("old data deleted")
    _deleteOldData()

### MODELS ###
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

    @property
    def serialize(self):
        return {
            'id'        :   self.id,
            'content'   :   self.content,
            'completed' :   self.completed,
            'date_created'  :   self.date_created
        }

class RoomCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)
    #lobby_id = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id

### SCHEMAS ###
class TodoSchema(ma.Schema):
    class Meta:
        fields = ("id", "content", "completed", "date_created")
        #Model = Todo
        #include_fk = True
    
todo_schema = TodoSchema()

@app.route("/", methods=['POST', 'GET'])
def hello():
    tasks = Todo.query.order_by(Todo.date_created).all()
    RoomCodes = RoomCode.query.order_by(RoomCode.date_created).all()
    return render_template('index.html', tasks=tasks, RoomCodes=RoomCodes)

@app.route("/delete", methods=['POST'])
def deleteOldData():
    if request.method == 'POST':
        dataToDelete = RoomCode.query.filter(RoomCode.date_created > (datetime.now() - timedelta(days=30))).all()
        for data in dataToDelete:
            db.session.delete(data) 

        db.session.commit()

    return 'old data deleted successfully', 200

def _deleteOldData():
    dataToDelete = RoomCode.query.filter(RoomCode.date_created > (datetime.now() - timedelta(days=30))).all()
    for data in dataToDelete:
        db.session.delete(data) 

    db.session.commit()

    return 'old data deleted successfully', 200




if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        schedule = BackgroundScheduler()
        schedule.add_job(scheduler, 'cron', second=2)
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


