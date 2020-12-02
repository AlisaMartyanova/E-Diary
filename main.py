from flask import Flask, render_template, url_for
from flask import request, jsonify
from pymongo import MongoClient
import bson.json_util as json_util
import json, datetime

from pymongo.common import clean_node

app = Flask(__name__)

id = 0
#connecting to mongodb
client = MongoClient('localhost', 27017)
db_name = "database"

mydb = client[db_name]
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

def init_db():
   #  db = client[db_name]
    client.drop_database(db_name)
    mydb = client[db_name]
    return "24\n"

def add_user(username, dob):
    # user = {"id": id, "username": username, "DoB": dob}
    # db = client[db_name]
    col = mydb["users"]
    user = {"username": username, "DoB": dob, "posts":[]}
    col.insert_one(user)

@app.route('/add_post', methods=["POST"])
def add_user_post():
    file = request.files['file']
    post = json.load(file)
    user_id = request.headers['id']
    mydb['users'].update_one({'_id': user_id}, {'$push': { 'posts': post} })
    return 'Post was successfully uploaded'

@app.route('/view_all_posts', methods=['GET'])
def view_all_posts():
    user_id = request.headers['id']
    document = mydb['users'].find({'_id': user_id})
    posts = []
    for i in document['posts']:
        posts.append(i)

    return jsonify(posts)


def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/users', methods=['GET'])
def get_users_list():
    init_db()

    add_user("Alisa", "12")
    add_user("Alena", "13")
    users = []
    for document in mydb["users"].find({}):
        # obj_id = print(parse_json(document))
        # users.append(parse_json(document))
        document['_id'] = document['_id'].toString()
        users.append(document)

    return jsonify(users)

# @app.route('/posts', methods=['GET'])
# def get_users_posts():
    

if __name__ == '__main__':
    app.run(debug=True)