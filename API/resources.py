from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from datetime import timedelta
from flask import send_from_directory, jsonify, json
import models
import os
from datetime import datetime
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('username', help='This field cannot be blank', required=True)
auth_parser.add_argument('password', help='This field cannot be blank', required=True)

note_download_parser = reqparse.RequestParser()
note_download_parser.add_argument('title', help='This field cannot be blank', required=True)
note_download_parser.add_argument('body', help='This field cannot be blank', required=True)

note_date_parser = reqparse.RequestParser()
note_date_parser.add_argument('date', help='This field cannot be blank')

note_id_parser = reqparse.RequestParser()
note_id_parser.add_argument('id', help='This field cannot be blank')

note_edit_parser = reqparse.RequestParser()
note_edit_parser.add_argument('title')
note_edit_parser.add_argument('body')

habit_download_parser = reqparse.RequestParser()
habit_download_parser.add_argument('title', help='This field cannot be blank', required=True)

habit_complete_parser = reqparse.RequestParser()
habit_complete_parser.add_argument('id', help='This field cannot be blank', required=True)

habit_get_parser = reqparse.RequestParser()
habit_get_parser.add_argument('creation_date')
habit_get_parser.add_argument('completion_date')


class UserRegistration(Resource):
    def post(self):
        data = auth_parser.parse_args()
        access_token_expiration_time = timedelta(days=1)
        refresh_token_expiration_time = timedelta(days=1)

        if models.UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}

        new_user = models.UserModel(
            username=data['username'],
            password=models.UserModel.generate_hash(data['password'])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'], expires_delta=access_token_expiration_time)
            refresh_token = create_refresh_token(identity=data['username'], expires_delta=refresh_token_expiration_time)
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = auth_parser.parse_args()
        access_token_expiration_time = timedelta(minutes=5)
        refresh_token_expiration_time = timedelta(days=1)
        current_user = models.UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if models.UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'], expires_delta=access_token_expiration_time)
            refresh_token = create_refresh_token(identity=data['username'], expires_delta=refresh_token_expiration_time)
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = models.RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class Note(Resource):
    @jwt_required
    def post(self):
        data = note_download_parser.parse_args()
        current_user = models.UserModel.find_by_username(get_jwt_identity())

        note_title = data['title']
        note_body = data['body']
        

        if not note_body:
            return {'message': 'No note was found'}  # TODO Add HTTP error ID

        new_note = models.NoteModel(
            user_id=current_user.id,
            title=note_title,
            body=note_body,
            datetime = str(datetime.now()),
            edited=0
        )
        new_note.add()

        return {
            'message': 'Note with name "{}" was successfully saved for user {}'.format(note_title, current_user.username)
        }

    @jwt_required
    def get(self):
        note_id = note_id_parser.parse_args()['id']
        date = note_date_parser.parse_args()['date']
        if note_id:
            note = models.NoteModel.find_by_ids(note_id)
            current_user = models.UserModel.find_by_username(get_jwt_identity())

            if current_user.id == note.user_id:
                return {
                    'id' : note.id,
                    'title' : note.title,
                    'body' : note.body,
                    'datetime' : note.datetime,
                    'edited' : note.edited
                }
            else:
                return 'Permission denied .!.'
        elif date:

            return models.NoteModel.find_by_date(date, models.UserModel.find_by_username(get_jwt_identity()).username)
        else:
            return models.NoteModel.return_all(models.UserModel.find_by_username(get_jwt_identity()).username)


    @jwt_required
    def delete(self):
        note_id = note_id_parser.parse_args()['id']
        current_user = models.UserModel.find_by_username(get_jwt_identity())

        if current_user.id == models.NoteModel.find_by_ids(note_id).user_id:
            return models.NoteModel.delete_note(note_id)
        else:
            return 'Permission denied .!.'


    @jwt_required
    def patch(self):
        note_id = note_id_parser.parse_args()['id']
        current_user = models.UserModel.find_by_username(get_jwt_identity())
        title = note_edit_parser.parse_args()['title']
        text = note_edit_parser.parse_args()['body']

        if current_user.id == models.NoteModel.find_by_ids(note_id).user_id:
            note = models.NoteModel.find_by_ids(note_id)
            if not title:
                title = note.title
            if not text:
                text = note.body
            return models.NoteModel.edit_note(note_id, title, text)
        else:
            return 'Permission denied .!.'



class Habit(Resource):
    @jwt_required
    def post(self):
        habit_title = habit_download_parser.parse_args()['title']
        current_user = models.UserModel.find_by_username(get_jwt_identity())

        if not habit_title:
            return {'message' : 'No habit was found'}

        new_habit = models.HabitModel(
            user_id = current_user.id,
            title = habit_title,
            datetime = str(datetime.now()),
            completed = json.dumps([])
        )
        new_habit.add()

        return {
            'message': 'Habit with name "{}" was successfully saved for user {}'.format(habit_title,
                                                                                       current_user.username)
        }

    @jwt_required
    def get(self):
        creation = habit_get_parser.parse_args()['creation_date']
        completion = habit_get_parser.parse_args()['completion_date']

        if creation:
            return models.HabitModel.find_by_creation_date(creation, models.UserModel.find_by_username(get_jwt_identity()).username)
        elif completion:
            return models.HabitModel.find_by_completion_date(completion, models.UserModel.find_by_username(get_jwt_identity()).username)
        else:
            return models.HabitModel.return_all(models.UserModel.find_by_username(get_jwt_identity()).username)


    @jwt_required
    def patch(self):
        habit_id = habit_complete_parser.parse_args()['id']
        current_user = models.UserModel.find_by_username(get_jwt_identity())

        if current_user.id == models.HabitModel.find_by_ids(habit_id).user_id:
            habit = models.HabitModel.find_by_ids(habit_id)
            list = json.loads(habit.completed)
            date = str(datetime.now().date())
            if date in list:
                list.remove(date)
            else:
                list.append(date)
            completed = json.dumps(list)
            return models.HabitModel.add_completed_date(habit_id, completed)
        else:
            return 'Permission denied .!.'

    @jwt_required
    def delete(self):
        habit_id = habit_complete_parser.parse_args()['id']
        current_user = models.UserModel.find_by_username(get_jwt_identity())

        if current_user.id == models.HabitModel.find_by_ids(habit_id).user_id:
            return models.HabitModel.delete_habit(habit_id)
        else:
            return 'Permission denied .!.'


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = models.RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return models.UserModel.return_all()

    def delete(self):
        return models.UserModel.delete_all()

