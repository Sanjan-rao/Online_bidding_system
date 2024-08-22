from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from routes import main as main_blueprint
from db import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
