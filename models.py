#!/usr/bin/env python
from database import *
from sqlalchemy.orm import relationship
from slugify import slugify
from wtforms.widgets import * #TextArea
from wtforms import * #TextField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField,validators, ValidationError
import wtforms.widgets.core
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
class UserMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100),nullable=True,unique=True)
    password = db.Column(db.String(600))
    password2=db.Column(db.String(200))
    created_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    emails=db.relationship('Email', backref="user_member", lazy='dynamic')
    groups=db.relationship('Group', backref="user_member", lazy='dynamic')
    emaillists=db.relationship('EmailList', backref="user_member", lazy='dynamic')
    def verify_password(self, password):
        #return custom_app_context.encrypt(password) == self.password
        return custom_app_context.verify(password, self.password)
    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.password2 = password
    def add(user):
        db.session.add(user)
        return db.session.commit()
    def update(self):
        return session_commit()
    def delete(user):
        db.session.delete(user)
        return session_commit()
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = UserMember.query.get(data['id'])
        return user
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    firstname  = db.Column(db.String(255), nullable=True)
    lastname  = db.Column(db.String(255), nullable=True)
    published_at = db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    emailgroup=db.relationship('Emailgroup', backref="email", lazy='dynamic')
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'),nullable=True)
    def __str__(self):
        return self.name
    def update(self):
        return session_commit()
    def to_Json(self):
        return dict(id=self.id,
            email=self.email,
            name=self.name
            )
    def __init__(self, email,firstname,lastname,user_id):
        self.email = email
        self.firstname =firstname
        self.lastname = lastname
        self.user_id = user_id
    def add(email):
        db.session.add(email)
        return db.session.commit()
    def delete(email):
        db.session.delete(email)
        return db.session.commit()
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(255))
    published_at = db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    emailgroups=db.relationship('Emailgroup', backref='"group"', lazy='dynamic')
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'),nullable=True)
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            name=self.name
            )
    def __init__(self,name,user_id):
        self.name =name
        self.user_id=user_id
    def add(group):
        db.session.add(group)
        return db.session.commit()
    def delete(group):
        db.session.delete(group)
        return db.session.commit()
class Emailgroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id  = db.Column(db.Integer,db.ForeignKey('email.id'),nullable=True)
    group_id  = db.Column(db.Integer,db.ForeignKey("group.id"),nullable=True)
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'),nullable=True)
    def __str__(self):
        return self.email_id
    def to_Json(self):
        return dict(id=self.id,
            email_id=self.email_id,
            group_id=self.group_id
            )
    def __init__(self,email_id,group_id,user_id):
        self.email_id =email_id,
        self.group_id =group_id
        self.user_id = user_id
    def add(emailgroup):
        db.session.add(emailgroup)
        return db.session.commit()
    def delete(emailgroup):
        db.session.delete(emailgroup)
        return db.session.commit()
class EmailList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(255))
    email  = db.Column(db.String(255))
    subject = db.Column(db.String(1000))
    description = db.Column(db.Text)
    reply_to = db.Column(db.String(255))
    sending_email = db.Column(db.String(255))
    sending_password = db.Column(db.String(255))
    sending_name    = db.Column(db.String(255))
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'),nullable=True)
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            name=self.name,
            email=self.email,
            subject = self.subject,
            description = self.description,
            reply_top = self.reply_to,
            sending_email=self.sending_email,
            sending_password=self.sending_password,
            sending_name=self.sending_name,
            user_id  = self.user_id
            )
    def __init__(self,name,email,subject,description,reply_to,sending_email,sending_password,sending_name,user_id):
        self.name =name,
        self.email =email,
        self.subject = subject,
        self.description = description,
        self.reply_to = reply_to,
        self.sending_email=sending_email,
        self.sending_password=sending_password,
        self.sending_name=sending_name,
        self.user_id = user_id
    def add(messagelist):
        db.session.add(messagelist)
        return db.session.commit()
    def delete(messagelist):
        db.session.delete(messagelist)
        return db.session.commit()
if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.config['DEBUG'] = True
    # app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    manager.run()
    app.run()