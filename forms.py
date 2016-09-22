#!/usr/bin/env python
from flask_wtf import Form
from wtforms import DateTimeField,TextField,FileField,PasswordField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField,validators, ValidationError
from flaskckeditor import CKEditor
class UserMemberForm(Form):
   name = TextField("Name",[validators.Required("Please enter your name.")])
   email = TextField("Email",[validators.Required("Please enter your email.")])
   password = PasswordField("Password",[validators.Required("Please enter your password.")])
   submit = SubmitField("Login")
class GroupForm(Form):
    name = TextField("Group Name")
class MemberForm(Form):
  name = TextField("Name",[validators.Required("Please enter your member's name.")])
  feature_image = FileField("Feature Image")
  possition = TextField("Position")
  detail = TextAreaField("Detail")
