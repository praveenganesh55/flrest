from flask_sqlalchemy import SQLAlchemy
from package import app
import os



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
