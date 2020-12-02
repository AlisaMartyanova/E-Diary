from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests, json
import os
import shutil


app = Flask(__name__)

def send_post():
    post = {
        'date': 2,
        'name': 'my first post',
        'text': 'Hey! This is my first post to test the system.'
    }
    values = {
        'id': '2'
    }
    r = requests.post('http://localhost:5000/add_post', json=post, headers=values)
    return r.content

def view_posts():
    values = {
        'id': '2'
    }
    r = requests.get('http://localhost:5000/view_all_posts', headers=values)
    return r.json()


# send_post()
view_posts()