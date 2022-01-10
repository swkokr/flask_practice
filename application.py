from flask import Flask, json, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from datetime import datetime

import string, random, socket

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

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
    IPAddress = db.Column(db.String(100), nullable=False)
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
todos_schema = TodoSchema(many=True)

@app.route("/api")
def api():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return jsonify(json_list = [i.serialize for i in tasks])

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/rand", methods=['GET', 'POST'])
def rand():
    if request.method == 'POST':
        hostName = socket.gethostname()
        hostIP = socket.gethostbyname(hostName)

        generatedString = id_generator()

        newCode = RoomCode(IPAddress=hostIP, code=generatedString)

        try:
            db.session.add(newCode)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating your task"
    else:
        return "RAND GET Method"

@app.route("/ma")
def marshmallow():
    todos = Todo.query.order_by(Todo.date_created).all()
    return jsonify(todos_schema.dump(todos))

@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        RoomCodes = RoomCode.query.order_by(RoomCode.date_created).all()
        return render_template('index.html', tasks=tasks, RoomCodes=RoomCodes)

@app.route("/<int:id>", methods=['GET'])
def getTask(id):
    task_to_select = Todo.query.get_or_404(id)
    task = Todo.query.filter(Todo.id == task_to_select)
    return render_template('index.html', tasks=task)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method =='POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating your task"
    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host='0.0.0.0')

