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

@app.route('/users/')
def get_users():
    return jsonify([
        {
            '_id':user.public_id, 'name':user.name, 'email':user.email,
            'is_admin':user.is_admin
        } for user in User.query.all()            
    ])

@app.route('/users/<id>/')
def get_user(id):
    print(id)
    user = User.query.filter_by(public_id=id).first_or_404()
    return {
        'id':user.public_id, 'name':user.name,
        'email':user.email, 'is_admin':user.is_admin
    }

@app.post('/users/')
def create_user():
    data = request.get_json()
    if not 'name' in data or not 'email' in data:
        return jsonify({
            'error':'Bad Request',
            'message':'Masukkan name dan email!'
        }), 400
    if len(data['name']) < 3 or len(data['email']) <6:
        return jsonify({
            'error':'Bad Request',
            'message':'Nama dan email harus memiliki minimal 3 karakter!'
        }), 400
    u = User(
        name = data['name'],
        email=data['email'],
        is_admin = data['is_admin', False],
        public_id = str(uuid.uuid4())
    )
    db.session.add(u)
    db.session.commit()
    return {
        'id':u.public_id, 'name':u.name,
        'email':u.email, 'is_admin':u.is_admin
    }, 201

# @app.put('/users/<id>/')
# def update_user(id):
#     data = request.get_json()
#     if 'name' not in data:
#         return jsonify({
#             'error':'Bad Request',
#             'message':'Masukkan nama!'
#         }), 400
#     user = User.query.filter_by()

if __name__ == '__main__':
    app.run(debug=True)