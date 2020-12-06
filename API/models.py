from passlib.hash import pbkdf2_sha256 as sha256
from run import db
import shutil
import os
from flask import send_from_directory, jsonify, json


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}


    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class NoteModel(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, name='user_id')
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    datetime = db.Column(db.String(30), nullable=True)
    edited = db.Column(db.Integer, nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_ids(cls, id):
        return db.session.query(cls).filter(cls.id == id).first()

    @classmethod
    def find_by_date(cls, date, username):
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'body': x.body,
                'datetime': x.datetime,
                'edited' : x.edited
            }

        user_id = UserModel.find_by_username(username).id
        return {
            "{}'s notes for {}".format(username, date): list(
                map(lambda x: to_json(x), db.session.query(cls).filter(cls.datetime.contains(date), cls.user_id == user_id).all())
            )
        }


    @classmethod
    def return_all(cls, username):
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'body': x.body,
                'datetime': x.datetime,
                'edited' : x.edited
            }

        user_id = UserModel.find_by_username(username).id

        return {
            "{}'s notes".format(username): list(
                map(lambda x: to_json(x), db.session.query(cls).filter(cls.user_id == user_id).all())
            )
        }


    @classmethod
    def delete_note(cls, id):
        note = db.session.query(cls).filter(cls.id == id).first()
        db.session.delete(note)
        db.session.commit()
        return {'message': 'Note was successfully deleted'}

    @classmethod
    def edit_note(cls, id, title, text):
        db.session.query(cls).filter(cls.id == id).\
            update({'title': title, 'body': text, 'edited': 1})
        db.session.commit()
        return {'message': 'Note was successfully edited'}

class HabitModel(db.Model):
    __tablename__ = 'habits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, name='user_id')
    title = db.Column(db.String(30), nullable=False)
    datetime = db.Column(db.String(30), nullable=False)
    completed = db.Column(db.Text, nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_creation_date(cls, date, username):
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'datetime': x.datetime,
                'completed': x.completed
            }

        user_id = UserModel.find_by_username(username).id
        return {
            "{}'s created habits for {}".format(username, date): list(
                map(lambda x: to_json(x),
                    db.session.query(cls).filter(cls.datetime.contains(date), cls.user_id == user_id).all())
            )
        }

    @classmethod
    def find_by_completion_date(cls, date, username):
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'datetime': x.datetime,
                'completed': x.completed
            }

        user_id = UserModel.find_by_username(username).id
        list = []
        for habit in db.session.query(cls).filter(cls.user_id == user_id).all():
            completed = json.loads(habit.completed)
            if date in completed:
                list.append(to_json(habit))

        jsonify(list)

        return {
            "{}'s completed habits for {}".format(username, date): list
        }

    @classmethod
    def find_by_ids(cls, id):
        return db.session.query(cls).filter(cls.id == id).first()


    @classmethod
    def return_all(cls, username):
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'datetime': x.datetime,
                'completed': x.completed
            }

        user_id = UserModel.find_by_username(username).id

        return {
            "{}'s habits".format(username): list(
                map(lambda x: to_json(x), db.session.query(cls).filter(cls.user_id == user_id).all())
            )
        }

    @classmethod
    def add_completed_date(cls, id, date):
        db.session.query(cls).filter(cls.id == id).update({'completed': date})
        db.session.commit()
        return {'message': 'Habit was completed'}

    @classmethod
    def delete_habit(cls, id):
        habit = db.session.query(cls).filter(cls.id == id).first()
        db.session.delete(habit)
        db.session.commit()
        return {'message': 'Note was successfully deleted'}
