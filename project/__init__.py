from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#from models import db
#from SQLAlchemy import Column, ForeignKey, Integer, String, Float, Numeric
# DOES NOT CREATE DATABASE ON flask run
# init SQLAlchemy so we can use it later in our models

#db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my_random_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/db.sqlite'
    
    from .models import db
    db.init_app(app)
    
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    # blueprint for non-auth parts of app
    from .upload import upload as upload_blueprint
    app.register_blueprint(upload_blueprint)
    
    from .grade import grade as grade_blueprint
    app.register_blueprint(grade_blueprint)
    
    from .subpage import subpage as subpage_blueprint
    app.register_blueprint(subpage_blueprint)
    
    from .review import review as review_blueprint
    app.register_blueprint(review_blueprint)
    
    from .profile import prof as profile_blueprint
    app.register_blueprint(profile_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        #since the user_id is the primary key in our user table use it in the query for the user
        #TODO: MODIFY THIS TO WORK WITH THE NETID
        return User.query.get(int(user_id))

    return app
