from flask_mail import *
from flask import Flask
app=Flask(__name__)
mail=Mail(app)
with open('config.json','r') as m:
    params=json.load(f)[]
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']=
app.config['MAIL_PASSWORD']=
app.config['MAIL_USE_TLS ']=False
app.config['MAIL_USE_SSL ']=True


