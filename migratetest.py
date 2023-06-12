from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5433/testing'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Add a new column to the User model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    # age = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<user {self.name}>"

@app.route('/')
def execute_query():
    query_string = text(
        '''
        SELECT *
        FROM users
        WHERE id > 1
        '''
    )
    result = db.session.execute(query_string)
    # Process the result as needed
    response = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email
        } for u in result
    ]

    return {'data': response}

# def perform_migration():
#     with app.app_context():
#         migrate.init_app(app)
#         migrate.migrate()
#         migrate.upgrade()

# perform_migration()

if __name__ == '__main__':
    app.run(debug=True)