from flask import Flask, render_template, url_for
from flask import request, jsonify
from pymongo import MongoClient
import bson.json_util as json_util
import json, datetime
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
import hashlib

from pymongo.common import clean_node


class DotDictWrapper:
    def __init__(self, d):
        self.d = d

    def __getattr__(self,key):
        try:
            return self.d[key]
        except KeyError.err:
            raise AttributeError(key)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'


_id = 1
#connecting to mongodb
client = MongoClient('localhost', 27017)
db_name = "database"
# client.drop_database(db_name)
mydb = client[db_name]


def authenticate(username, password):
    user = mydb["users"].find_one({'username':username, 'password': hashlib.md5(password.encode()).hexdigest()})
    if user:
        info = parse_json(user)
        return DotDictWrapper(info)
    return None


def identity(payload):
    user_id = payload['identity']
    u = mydb["users"].find({'id': user_id})
    if u:
        info = parse_json(u)
        return info
    return None

jwt = JWT(app, authenticate, identity)

# users = mydb["users"]

post = [
    {
        'author': 'P1',
        'title': 'Blog Post 1',
        'content': 'First note',
        'date_posted': '30 November, 2020'
    },
    {
        'author': 'P2',
        'title': 'Blog Post 2',
        'content': 'Second note',
        'date_posted': '31 November, 2020'
    }
]

@app.route('/')
@app.route('/home')
def hello_world():
    return render_template('home.html', posts=post)

@app.route('/about')
def about():
    return render_template('about.html', title='Good')


def add_user(username, password, _id):
    # user = {"id": id, "username": username, "DoB": dob}
    # db = client[db_name]
    col = mydb["users"]
    user = {"id": _id, "username": username, 'password': password, "posts":[]}
    col.insert_one(user)

@app.route('/add_post', methods=["POST"])
def add_user_post():
    file = request.files['file']
    post = parse_json(file)
    user_id = request.headers['id']
    mydb['users'].find_one_and_update({'id': int(user_id)}, {'$set': { 'posts': post} })
    return 'Post was successfully uploaded'

@app.route('/view_all_posts', methods=['GET'])
def view_all_posts():
    user_id = request.headers['id']
    document = mydb['users'].find({'id': int(user_id)})
    posts = []
    for i in document['posts']:
        posts.append(i)

    return jsonify(posts)


def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/users', methods=['GET'])
def get_users_list():
    users = []
    for document in mydb["users"].find({}):
        info = parse_json(document)
        info['_id'] = info['_id']['$oid']
        users.append(info)
        # document['_id'] = document['_id'].toString()
        # users.append(document)

    return jsonify(users)

# @app.route('/posts', methods=['GET'])
# def get_users_posts():
    

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

@app.route('/register', methods=["POST"])
def register():
    global _id
    username = request.json['username']
    password = request.json['password']
    h = hashlib.md5(password.encode()).hexdigest()

    add_user(username, h, _id)
    _id += 1

    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)