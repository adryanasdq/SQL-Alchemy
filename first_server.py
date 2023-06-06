from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5433/sqlalchemy-intro'
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column(db.String(20), nullable=False)
	email = db.Column(db.String(28), nullable=False, unique=True)
	public_id = db.Column(db.String, nullable=False)
	is_admin = db.Column(db.Boolean, default=False)
	todos=db.relationship('Todo', backref='owner', lazy='dynamic')

	def __repr__(self):
		return f'User <{self.email}>'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    public_id = db.Column(db.String, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'Todo <{self.name}>'

@app.get('/users')
def get_users():
    return jsonify([
        {
            '_id':user.public_id,
            'name':user.name,
            'email':user.email,
            'is_admin':user.is_admin
        } for user in User.query.all()            
    ])

@app.post('/users')
def create_user():
    name = request.json.get('name')
    email = request.json.get('email')
    is_admin = request.json.get('is_admin', False)
    if not name or not email:
        return jsonify({'error': 'Bad Request', 'message': 'Name or email not provided.'}), 400
    u = User(
        name=name,
        email=email,
        is_admin=is_admin,
        public_id=str(uuid.uuid4())
    )
    db.session.add(u)
    db.session.commit()
    return {
        'id': u.public_id,
        'name': u.name,
        'email': u.email,
        'is_admin': u.is_admin
    }, 201

@app.route('/users/<id>', methods=['GET', 'PUT', 'DELETE'])
def update_user(id):
    user = User.query.filter_by(public_id=id).first_or_404()

    if request.method == 'GET':
        return jsonify({
            'id': user.public_id, 
            'name': user.name,
            'is_admin': user.is_admin,
            'email': user.email
            })
    
    elif request.method == 'PUT':
        data = request.get_json()
        if 'name' not in data:
            return {
                'error': 'Bad Request',
                'message': 'Name field needs to be present'
            }, 400
        user.name = data['name']
        if 'is_admin' in data:
            user.is_admin=data['is_admin']
        db.session.commit()
        return jsonify({
            'id': user.public_id, 
            'name': user.name,
            'is_admin': user.is_admin,
            'email': user.email
            })
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return {
            'success' : 'data has been deleted'
        }

@app.get('/todos')
def get_todos():
    return jsonify([
        {
            'id': todo.public_id,
            'name_todo': todo.name,
            'is_completed':todo.is_completed,
            'owner': {
                'name': todo.owner.name,
                'email': todo.owner.email,
                'public_id': todo.owner.public_id
            }
        } for todo in Todo.query.all()
    ])

@app.post('/todos')
def create_todo():
    name = request.json.get('name')
    email = request.json.get('email')
    is_completed = request.json.get('is_completed', False)
    if not name or not email:
        return jsonify({
            'error':'Bad Request',
            'message':'Name or Email not given'
        }), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return {
            'error': 'Bad Request',
            'message': 'Invalid email, no user with that email'
        }
    todo = Todo(
        name = name,
        user_id = user.id,
        is_completed = is_completed,
        public_id = str(uuid.uuid4())
    )
    db.session.add(todo)
    db.session.commit()
    return {
        'id': todo.public_id,
        'name': todo.name,
        'is_completed': todo.is_completed,
        'owner': {
            'name':todo.owner.name,
            'email': todo.owner.email,
            'is_admin': todo.owner.is_admin
        }
    }, 201

@app.route('/todos/<id>', methods=['GET', 'PUT', 'DELETE'])
def get_todo(id):
    todo = Todo.query.filter_by(public_id=id).first_or_404()

    if request.method == 'GET':
        return jsonify(
            {
                'id': todo.public_id,
                'name': todo.name,
                'owner': {
                    'name': todo.owner.name,
                    'email': todo.owner.email,
                    'public_id': todo.owner.public_id
                }
            })
    
    elif request.method == 'PUT':
        name = request.json.get('name')
        is_completed = request.json.get('is_completed')
        if not name:
            return {
                'error': 'Bad Request',
                'message': 'Name not given'
            }
        todo.name = name
        if is_completed:
            todo.is_completed = is_completed
        db.session.commit()
        return jsonify(
            {
                'id': todo.public_id,
                'name': todo.name,
                'is_completed': todo.is_completed,
                'owner': {
                    'name': todo.owner.name,
                    'email': todo.owner.email,
                    'public_id': todo.owner.public_id
                }
            }), 201
    
    elif request.method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()
        return {
            'success':'Data has been deleted'
        }

if __name__ == '__main__':
    app.run(debug=True)