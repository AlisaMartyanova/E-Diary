from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests, json
import os
import shutil


app = Flask(__name__)

def send_post():
    file = {'date': 2, 'name': 'my first post', 'text': 'Hey! This is my first post to test the system.'}
    with open('data.json', 'w') as output:
        json.dump(file, output)
    files = {'file': 'data.json'}
    values = {'id': '1'}
    r = requests.post('http://localhost:5000/add_post', files=files, headers=values)


def view_posts():
    values = {'id': '1'}
    r = requests.post('http://localhost:5000/view_all_posts', headers=values)


send_post()
view_posts()