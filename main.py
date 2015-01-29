# -*- coding: utf-8 -*-
import os
from json import dumps
from flask_mail import Mail
from flask import Flask, url_for, render_template, jsonify
from flask.ext.login import current_user
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongorest import MongoRest
from flask.ext.mongorest.views import ResourceView
from flask.ext.mongorest.resources import Resource
from flask.ext.mongorest import operators as ops
from flask.ext.mongorest import methods
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_security.forms import RegisterForm
import wtforms


# config


app = Flask(__name__)
app.config.update(
    MONGODB_HOST = 'localhost',
    MONGODB_PORT = '27017',
    MONGODB_DB = 'motoparking',
)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = 'ytdjf.jk,upo8etsgdf,asdf34ttgewgq3g[q[epqogqjg;'
app.config['SECURITY_REGISTERABLE'] = True

db = MongoEngine(app)
api = MongoRest(app)

# After 'Create app'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'username'
app.config['MAIL_PASSWORD'] = 'password'
app.config['MAIL_SUPPRESS_SEND'] = True
mail = Mail(app)



# models


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    name = db.StringField(max_length=255)


# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)


class ExtendedRegisterForm(RegisterForm):
    name = wtforms.TextField('Name', [wtforms.validators.Required()])


security = Security(app, user_datastore,
         register_form=ExtendedRegisterForm)

# Create a user to test with
@app.before_first_request
def create_user():
    user_datastore.create_user(email='matt@nobien.net', password='123456')


class Parking(db.Document):
    title = db.StringField()
    lat_lng = db.PointField()
    status = db.IntField()
    user = db.ReferenceField(User)

# Parking(title="Парковка 1", lat_lng=[55.7622200, 37.6155600], ).save()


class Opinion(db.Document):
    parking = db.ReferenceField(Parking)
    user = db.ReferenceField(User)
    is_secure = db.IntField()
    is_moto = db.IntField()


# resources


class ParkingResource(Resource):
    document = Parking
    rename_fields = {
        'lat_lng': 'latLng',
    }

    def create_object(self, data=None, save=True, parent_resources=None):
        obj = super(ParkingResource, self).create_object(data, save=False, parent_resources=parent_resources)
        obj.user = current_user._get_current_object()
        if save:
            self._save(obj)
        return obj


class OpinionResource(Resource):
    document = Opinion
    filters = {
        'parkingId': [ops.Exact],
    }
    rename_fields = {
        'parking_id': 'parkingId',
    }
    readonly_fields = ["id", "userId"]

    def create_object(self, data=None, save=True, parent_resources=None):
        obj = super(OpinionResource, self).create_object(data, save=False, parent_resources=parent_resources)
        obj.user = current_user._get_current_object()
        if save:
            self._save(obj)
        return obj


class UserResource(Resource):
    document = User
    fields = ["id", "name", ]


# api views

@api.register(name='parkings', url='/api/parkings/')
class ParkingView(ResourceView):
    resource = ParkingResource
    methods = [methods.Create, methods.Fetch, methods.List, methods.Delete]


@api.register(name='opinions', url='/api/opinions/')
class CheckpointView(ResourceView):
    resource = OpinionResource
    methods = [methods.Create, methods.Fetch, methods.List, methods.Delete]


@api.register(name='users', url='/api/users/')
class UserView(ResourceView):
    resource = UserResource
    methods = [methods.Fetch, methods.List]


# other views


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Catch all"""
    return render_template('index.html', current_user_json_str=user_json(current_user))


# utils


def user_json(user):
    return dumps({
        "id": user.get_id()
    })


if __name__ == '__main__':
    app.debug = True
    app.run(
        # host="0.0.0.0"
    )