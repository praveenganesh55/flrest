from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from newsapi import NewsApiClient
import os

app = Flask(__name__)

app.config['SECRET KEY']=os.environ.get("SECRETKEY")
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:test123@localhost/flrest'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class News(db.Model):
   news_id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(200))
   title =  db.Column(db.String(500))
   description =  db.Column(db.String(500))
   url =  db.Column(db.String(500))
   content = db.Column(db.String(1000))
   category = db.Column(db.String(200))
   date = db.Column(db.DateTime())


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
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    data = request.get_json(force=True)
    #return {"message": data}
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created!'})

@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user,public_id):
   if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

   user = User.query.filter_by(public_id=public_id).first()

   if not user:
        return jsonify({'message' : 'No user found!'})

   user.admin = True
   db.session.commit()

   return jsonify({'message' : 'The user has been promoted!'})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted!'})

@app.route('/login')
def login():
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

@app.route('/collect',methods=['GET'])
@token_required
def collect(current_user):
    if not current_user.admin:
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

@app.route('/category/<int:num>',methods=['GET'])
def category(num):
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
    a = (num * 10) - 9
    b = (num * 10) + 1
    return jsonify({"message": output[a:b]})


   
if __name__=='__main__':
    app.run(debug=True)