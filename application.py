from flask import Flask, json, render_template, url_for, request, redirect, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from datetime import datetime

import string, random, socket

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret!!"

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
    ip_address = db.Column(db.String(100), nullable=False)
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

def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/code", methods=['POST', 'GET', 'DELETE'])
def code():
    hostName = socket.gethostname()
    #hostIP = socket.gethostbyname(hostName)
    if request.method == 'POST':


        try:
            generatedString = request.form['code']
            hostIP = request.form['hostIP']
        except:
            #remove in the future
            generatedString = code_generator()
            hostIP = socket.gethostbyname(hostName)

        newCode = RoomCode(ip_address=hostIP, code=generatedString)
 
        isIPExisting = bool(RoomCode.query.filter(RoomCode.ip_address == hostIP).first())
        if isIPExisting:
            flash("the IP exists")
            #abort(error="IP exists")
            code_to_delete = RoomCode.query.filter(RoomCode.ip_address == hostIP).first()
            print("delete")
            print(code_to_delete)

            try:
                db.session.delete(code_to_delete)
                db.session.commit()
            except:
                abort()



        try:
            db.session.add(newCode)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue posting your code"
    elif request.method == 'GET':
        _code = request.args['code']
        query_data = RoomCode.query.filter(RoomCode.code == _code).first()
        ip_address = query_data.ip_address
        return ip_address

    else:
        return "Wrong Method for CODE"

@app.route('/deleteCode', methods=['POST'])
def deleteCode():
    if request.method == 'POST':
        code = request.form['code']
        code_to_delete = RoomCode.query.filter(RoomCode.code == code).first()

        print(code)
        print(code_to_delete)

        try:
            db.session.delete(code_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem deleting that task'


@app.route('/deleteCode/<string:code>')
def deleteCodeFromstring(code):
    code_to_delete = RoomCode.query.filter(RoomCode.code == code).first()

    print(code_to_delete)

    try:
        db.session.delete(code_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/deleteCode/<int:id>')
def deleteCodeByID(id):
    code_to_delete = RoomCode.query.get_or_404(id)

    try:
        db.session.delete(code_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

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

@app.route('/updateCode/<int:id>', methods=['GET', 'POST'])
def updateCode(id):
    code = RoomCode.query.get_or_404(id)

    if request.method =='POST':
        code.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating your task"
    else:
        return render_template('update.html', task=code)


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


#
# for testing
#
@app.route("/score")
def scoreTest():
    return jsonify(10)

@app.route("/ma")
def marshmallow():
    todos = Todo.query.order_by(Todo.date_created).all()
    return jsonify(todos_schema.dump(todos))

@app.route("/mountain")
def helloWorld():
    tasks = Todo.query.order_by(Todo.content).all()
    return render_template('index.html', tasks=tasks)

@app.route("/create")
def createTable():
    return db.create_all()

@app.route("/api")
def api():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return jsonify(json_list = [i.serialize for i in tasks])


if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host='0.0.0.0')

