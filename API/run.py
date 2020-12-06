from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
import models, resources
from flask_jwt_extended import JWTManager

app = Flask(__name__)

api = Api(app)

#map urls with functions
api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.Note, '/posts')
api.add_resource(resources.Habit, '/habits')



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SoftwareArchitecture'

db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = 'kjgh234jht4h5hgkh'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

#work with tokens
jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
