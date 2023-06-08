from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5433/testing'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Add a new column to the User model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)

def perform_migration():
    with app.app_context():
        migrate.init_app(app)
        migrate.migrate()
        migrate.upgrade()

perform_migration()