from package import app
from flask import Flask, request, jsonify, make_response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from newsapi import NewsApiClient
from flask.views import MethodView
from .models import User,News,db
import os


def validation(str):
    if len(str)<7 or len(str)>20:
        return jsonify ({"message":"Validation error"})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
            global ca
            ca=current_user.admin
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

class Getone(MethodView):
        @token_required


        def get(self, ca, public_id):

            if not ca:
                return jsonify({'message': 'Cannot perform that function!'})

            user = User.query.filter_by(public_id=public_id).first()

            if not user:
                return jsonify({'message': 'No user found!'})

            user_data = {}
            user_data['public_id'] = user.public_id
            user_data['name'] = user.name
            user_data['password'] = user.password
            user_data['admin'] = user.admin

            return jsonify({'user': user_data})


class Cuser(MethodView):
    #@token_required
    def post(self):
        #if not ca:
         #   return jsonify({'message' : 'Cannot perform that function!'})

        data = request.get_json(force=True)
        if len(data['password'])<6 or len(data['password'])>20:
            return jsonify({'message':'validation error'})
        if len(data['name'])<6 or len(data['name'])>20:
            return jsonify({'message':'validation error'})

        hashed_password = generate_password_hash(data['password'], method='sha256')

        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message' : 'New user created!'})

class Edituser(MethodView):
    @token_required
    def get(self, ca):

        if not ca:
            return jsonify({'message': 'Cannot perform that function!'})

        users = User.query.all()

        output = []

        for user in users:
            user_data = {}
            user_data['public_id'] = user.public_id
            user_data['name'] = user.name
            user_data['password'] = user.password
            user_data['admin'] = user.admin
            user_data['age'] = user.age
            user_data['gender'] = user.gender
            output.append(user_data)

        return jsonify({'users': output})
    @token_required
    def put(self):

        token = request.headers['x-access-token']
        data = jwt.decode(token, app.config['SECRET KEY'])
        current_user = User.query.filter_by(public_id=data['public_id']).first()

        if not current_user:
            return jsonify({'message': 'No user found!'})
        data = request.get_json(force=True)

        current_user.admin = True
        current_user.age = data["age"]
        current_user.gender = data["gender"]
        db.session.commit()

        return jsonify({'message': 'The user has been promoted!'})

    @token_required
    def delete(self, ca, public_id):
        if not ca:
            return jsonify({'message': 'Cannot perform that function!'})

        user = User.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({'message': 'No user found!'})

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'The user has been deleted!'})


class Login(MethodView):
 def get(self):
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({"message":"Could not Verify"})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return jsonify({"message":"Could not Verify"})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return jsonify({"message":"Could not Verify"})

class Collect(MethodView):
        @token_required
        def get(self,ca):
            if not ca:
                return jsonify({'message': 'Cannot perform that function!'})
            newsapi = NewsApiClient(api_key=os.environ.get("APIKEY"))
            lis=["sports","business","technology","entertainment"]
            for k in lis:
             for i in range(1,4):
                    top_headlines = newsapi.get_top_headlines(category=k,country='in', page=i)
                    articles=top_headlines['articles']
                    for i in range(len(articles)):
                         myarticle=articles[i]
                         new_article = News(author=myarticle['author'],title=myarticle['title'],description=myarticle['description'],url=myarticle['url'],content=myarticle['content'],category=k,date=datetime.date.today())
                         db.session.add(new_article)
            db.session.commit()



            return jsonify({"message": "Successfully stored in Database"})

class Category(MethodView):
        @token_required
        def get(self,page):
            page=request.args['page']
            cate=request.args['cate']
            newss=News.query.filter_by(category=cate,date=datetime.date.today())
            output=[]
            for news in newss:
                news_data={}
                news_data['author'] = news.author
                news_data['title'] = news.title
                news_data['description'] = news.description
                news_data['url'] = news.url
                news_data['content'] = news.content
                output.append(news_data)
            page=int(page)
            a = (page * 10) - 9
            b = (page * 10) + 1
            return jsonify({"message": output[a:b]})


