#!/usr/bin/env python
from database import *
import os.path as op
import os
import flask
from flask import json,abort,Flask,g, render_template,request,session,redirect,url_for,flash
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField,validators, ValidationError
from flask_sijax import sijax
from flask.json import jsonify
import math
from models import *
from forms import *
from models import *
from random import randint
import logging
import time
logging.basicConfig()
template ="email"
config=""
email=''
pwd=''
password=''
send_name=''
limit=30
#### send mail ####
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_TLS = False,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = email,
	MAIL_PASSWORD = pwd
	)
mail=Mail(app)
#####################
#Middleware
# header_image=random.choice (arr_header_image)
@app.context_processor
def inject_dict_for_all_templates():
    return dict(logined_name=request.cookies.get('blog_name'),template_name= template)
#========================================================
@auth.verify_token
def verify_token(token):
	user = UserMember.query.filter_by(email = request.cookies.get('blog_email'))
	if user.count()>0:
		for user_object in user:
			if user_object.verify_password(request.cookies.get('blog_password')):
				return True
	return False
@auth.error_handler
def goLoginPage():
	return redirect(url_for("admin_login"))
#================
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/login', methods=['POST', 'GET'])
@app.route('/login/', methods=['POST', 'GET'])
def admin_login():
	form = UserMemberForm()
	if request.method == 'POST':
		email_form = request.form['email']
		password_form = request.form['password']
		user = UserMember.query.filter_by(email=email_form)
		if user.count()>0:
				#"set session"
				check=0
				for user_object in user:
					#return "{}".format(user_object.verify_password(password_form))
					if user_object.verify_password(password_form):
						response = make_response(redirect('/email'))
						response.set_cookie("blog_id",str(user_object.id), expires=expire_date)
						response.set_cookie("blog_name",user_object.name, expires=expire_date)
						response.set_cookie("blog_email",user_object.email, expires=expire_date)
						response.set_cookie("blog_password",password_form, expires=expire_date)
					
						return response
					else:
						flash('Wrong user name or password !')
						return redirect(url_for("admin_login"))
		else:
			flash('Wrong user name or password !')
			return redirect(url_for("admin_login"))
	elif request.method == 'GET':
		#return str(request.cookies.get("blog_name"))
		if request.cookies.get("blog_name"):
			return redirect(url_for("admin_email"))
		return render_template('admin/form/login.html',form = form)
@app.route('/logout', methods=['POST', 'GET'])
@app.route('/logout/', methods=['POST', 'GET'])
# @auth.login_required
def logout():
	response = make_response(redirect('/login'))
	response.set_cookie("blog_id","", expires=0)
	response.set_cookie("blog_name","", expires=0)
	response.set_cookie("blog_email","", expires=0)
	response.set_cookie("blog_password","", expires=0)
	return response
@app.route('/register', methods=['POST', 'GET'])
@app.route('/register/', methods=['POST', 'GET'])
#@auth.login_required
def admin_register():
	form = UserMemberForm()
	if request.method == 'POST':
		user=UserMember(request.form['name'],request.form['email'],request.form['password'])
		user.hash_password(request.form['password'])
		try:
			status=UserMember.add(user)
			if not status:
				flash("User Added successfully")
				return redirect(url_for('admin_login'))
			else:
				flash("Error in adding user.")
				return redirect(url_for('admin_register'))	
		except Exception as e:
			flash("Error in adding User. "+e.message)
			return redirect(url_for('admin_register'))
	return render_template('admin/form/register.html', form = form)

@app.route('/recovery',methods=["POST","GET"])
@app.route('/recovery/',methods=["POST","GET"])
def verify_email():
	if request.method=="GET":
		return render_template('admin/verify-email.html')
	else:
		your_passowrd=''
		email_temp=request.form['email']
		users=UserMember.query.filter_by(email=email_temp)
		for usr in users:
			your_passowrd=usr.password2
			your_name=usr.name
		if your_passowrd!="":
			#send email
			try:
				global email
				#return email+":"+email_temp+":"+pwd
				msg = Message('Password recovery',sender=email,recipients=[email_temp])
				message_string='<div style="width:400px;border:2px solid blue;padding:10px;">Hello '+your_name+',<br/> Your password is: <b>'+your_passowrd+'</b></b> Thanks for choosing Amogli service.<br/></div>'
				msg.html = message_string
				mail.send(msg)				
				flash("Please check your email to recovery the password.")
				return redirect(url_for("admin_login"))
			except Exception as e:
				raise
				return str(e.message)
		else:
			#wrong email
			flash("Sorry, We couldn't find this email to recovery you password. It might wrong email address")
			return render_template('admin/verify-email.html')
			return "We couldn't find this email."

###########SEND MAIL##############
@app.route('/email/sending')
@app.route('/email/sending/')
@app.route('/email/sending/<id>/<action>', methods = ['GET', 'POST'])
@app.route('/email/sending/<id>/<action>/', methods = ['GET', 'POST'])
@app.route('/email/sending/<pagination>')
@app.route('/email/sending/<pagination>/')
def sendingList(id=0,action='none',pagination=1):
	email_to_send = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count()
	if action=='delete':
		try:
			if int(id)==0:
				try:
					arr_email=str(request.form['emails']).split(";")
					print str(arr_email)
					for e in arr_email:
						print str(e)
						obj=EmailList.query.filter_by(id=int(e)).filter_by(user_id=request.cookies.get('blog_id')).first()
						status = EmailList.delete(obj)
					return jsonify({'success':"Ok" })
				except Exception as e:
					return jsonify({'success':"Error:"+e.message })
			else:
				ob=EmailList.query.filter_by(id=id).filter_by(user_id=request.cookies.get('blog_id')).first()
				status = EmailList.delete(ob)
				if not status:
					flash("Email deleted from sending list successfully")
				else:
					flash("Error in deleting email from sending list !")
		except Exception as e:
			print e.message
	sendnigEmails = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).limit(limit).offset(int(int(int(pagination)-1)*limit))
	pagin=math.ceil((EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count())/limit)
	if((EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count())%limit != 0 ):
		pagin=int(pagin+1)
	return render_template('/admin/emailsending.html',current_pagin=int(pagination),pagin=int(pagin),email_to_send=email_to_send,emails=sendnigEmails)
@app.route('/email/group', methods = ['GET', 'POST'])
@app.route('/email/group/', methods = ['GET', 'POST'])
# @app.route('/admin/email/group/<slug>', methods = ['GET', 'POST'])
# @app.route('/admin/email/group/<slug>/', methods = ['GET', 'POST'])
@app.route('/email/group/<slug>/<action>', methods = ['GET', 'POST'])
@app.route('/email/group/<slug>/<action>/', methods = ['GET', 'POST'])
@auth.login_required
def admin_mail_group(slug='',action=''):
	#slug is group name
	form = GroupForm()
	groups=Group.query.filter_by(user_id=request.cookies.get('blog_id')).order_by(Group.id.desc())
	email_to_send = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count()
	if slug=='':
		if request.method=="GET":
			return render_template("admin/form/mailgroup.html",email_to_send=email_to_send,name=slug,form=form,groups=groups)
		else:
			try:
				name = request.form['name']
				grp=Group(name,request.cookies.get('blog_id'))
				status=Group.add(grp)
				if not status:
					flash("Group Added successfully")
					return redirect(url_for('admin_mail_group'))
				else:
					flash("Error in adding Group !")
					return redirect(url_for('admin_mail_group'))
			except Exception as e:
				flask(e.message)
				return redirect(url_for("admin_mail_group"))
	else:
		#edit or delete
		if action=="edit":
			if request.method=="GET":
				return render_template("admin/form/mailgroup.html",email_to_send=email_to_send,form=form,groups=groups,name=slug)
			else:
				try:
					obj=Group.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(name=slug)
					obj.update({"name" : request.form['name'] })
					status = db.session.commit()
					#status = obj.update({"name":request.form['name']})
					if not status:
						flash("Group updated successfully")
						return redirect(url_for('admin_mail_group'))
					else:
						flash("Error in updating group !")
						return redirect(url_for('admin_mail_group'))
				except Exception as e:
					flash(e.message)
					return redirect(url_for("admin_mail_group"))
		elif action=='view':
			allEmailsInGroup = Emailgroup.query.join(Email).filter(Emailgroup.user_id==request.cookies.get('blog_id')).filter(Emailgroup.group_id==slug)
			# for e in allEmailsInGroup:
			# 	return str(e.id)
			group = Group.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(id=slug)
			return render_template("admin/emailInGroup.html",group_object=group,allEmailsInGroup=allEmailsInGroup,groups=groups)
		else:
			#delete group
			try:
				obj=Group.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(name=slug).first()
				status = Group.delete(obj)
				if not status:
					flash("Group deleted successfully")
					return redirect(url_for('admin_mail_group'))
				else:
					flash("Error in deleting group !")
					return redirect(url_for('admin_mail_group'))
			except Exception as e:
				flash(e.message)
				return redirect(url_for('admin_mail_group'))
import collections
@app.route('/mail/setgroup/', methods = ['GET', 'POST'])
@app.route('/mail/setgroup', methods = ['GET', 'POST'])
@auth.login_required
def addEmailsToGroups():
	try:
		arr_group=str(request.form['groups']).split(";")
		arr_email=str(request.form['emails']).split(";")
		for grp in arr_group:
			for e in arr_email:
				temp = Emailgroup.query.filter_by(email_id=e).filter_by(group_id=grp).filter_by(user_id=request.cookies.get('blog_id'))
				# print str(temp.count())
				if temp.count()<=0:
					try:
						print 'save: email='+str(e)+";group="+str(grp)
						obj = Emailgroup(int(e),int(grp),request.cookies.get('blog_id'))
						status2 = Emailgroup.add(obj)
					except Exception as e:
						print e.message

		# return jsonify({'groups':str(request.form['groups']),'emails':str(request.form['emails'])})
		return jsonify({'success':"Ok" })
	except Exception as e:
		return jsonify({'success':"error:"+e.message })

@app.route('/mail/<id>/group/', methods = ['GET', 'POST'])
@app.route('/mail/<id>/group', methods = ['GET', 'POST'])
@auth.login_required
def getEmailByGroupId(id):
	emails = Emailgroup.query.join(Email,Emailgroup.email_id == Email.id).filter(Emailgroup.group_id==id).filter(Emailgroup.user_id==request.cookies.get('blog_id')).all()
	objects_list = []
	for row in emails:
	    d = collections.OrderedDict()
	    d['id'] = row.id
	    d['email'] = Email.query.filter_by(id=row.email_id).filter_by(user_id=request.cookies.get('blog_id')).first().email
	    d['group_id'] = row.group_id
	    d['email_id'] = row.email_id
	    objects_list.append(d)
	 
	j = json.dumps(objects_list)
	return j
	# for email_temp in emails:
	# 	return str(email_temp.id)
	# return jsonify({'emails':jsontify(emails)})
@app.route('/mail', methods = ['GET', 'POST'])
@app.route('/mail/', methods = ['GET', 'POST'])
@app.route('/mail/<id>/<action>', methods = ['GET', 'POST'])
@app.route('/mail/<id>/<action>/', methods = ['GET', 'POST'])
@app.route('/mail/<pagination>', methods = ['GET', 'POST'])
@app.route('/mail/<pagination>/', methods = ['GET', 'POST'])
@auth.login_required
def admin_mail(id=0,action='',pagination=1):
	email_to_send = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count()
	emails=Email.query.filter_by(user_id=request.cookies.get('blog_id')).order_by(Email.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
	groups=Group.query.filter_by(user_id=request.cookies.get('blog_id')).order_by(Group.id.desc())
	pagin=math.ceil((Email.query.filter_by(user_id=request.cookies.get('blog_id')).count())/limit)
	if(math.ceil(Email.query.filter_by(user_id=request.cookies.get('blog_id')).count())%limit != 0 ):
		pagin=int(pagin+1)
	try:
		if action=="delete_json":
			try:
				arr_email=str(request.form['emails']).split(";")
				for e in arr_email:
					try:
						obj=Email.query.filter_by(id=int(e)).filter_by(user_id=request.cookies.get('blog_id')).first()
						status = Email.delete(obj)
					except Exception as e:
						print e.message
				return jsonify({'success':"Ok" })
			except Exception as e:
				return jsonify({'success':"Error:"+e.message})
		elif action=='edit':
			if request.method=='GET':
				email=Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(id=id)
				return render_template("admin/form/maillist.html",current_pagin=int(pagination),pagin=int(pagin),email_to_send=email_to_send,email_object=email,groups=groups,emails=emails)
			else:
				obj = Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(id=id)
				obj.update({"firstname" : request.form['firstname'],"lastname" : request.form['lastname'],'email':request.form['email']})
			   	status = db.session.commit()
			   	if not status:
					flash("Email updated successfully")
					return redirect(url_for('admin_mail'))
				else:
					flash("Error in updating email !")
					return redirect(url_for('admin_mail'))
		elif action=='delete':
			obj=Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(id=id).first()
			status = Email.delete(obj)
			if not status:
				flash("Email deleted successfully")
				return redirect(url_for('admin_mail'))
			else:
				flash("Error in deleting email !")
				return redirect(url_for('admin_mail'))
		elif request.method=="GET":
			search=''
			if request.args.has_key('q'):
				search=(str(request.args['q']))#.split()
				search=search.replace(" ",'+')
				emails=Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter((Email.firstname).match("'%"+search+"%'")).order_by(Email.id.desc()).all()
				
				pagin=math.ceil((Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter((Email.firstname).match("'%"+search+"%'")).count())/limit)
				if(math.ceil(Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter((Email.firstname).match("'%"+search+"%'")).count())%limit != 0 ):
					pagin=int(pagin+1)
			return render_template("admin/form/maillist.html",search=search,current_pagin=int(pagination),pagin=int(pagin),email_to_send=email_to_send,groups=groups,emails=emails)
		else:
			obj=Email(request.form['email'],request.form['firstname'],request.form['lastname'],request.cookies.get('blog_id'))
	   		status=Email.add(obj)
			if not status:
				flash("Email added successfully")
				return redirect(url_for('admin_mail'))
			else:
				flash("Error in adding email !")
				return redirect(url_for('admin_mail'))	
		
			return redirect(url_for('admin_mail'))
	except Exception as e:
		flash("Error:"+e.message)
		return redirect(url_for('admin_mail'))	
email_count=0
subject=''
description=''
group_send=[]
sched = Scheduler()
@app.route('/import/<pagination>', methods = ['GET', 'POST'])
@app.route('/import/<pagination>/', methods = ['GET', 'POST'])
@app.route('/import/', methods = ['GET', 'POST'])
@app.route('/import', methods = ['GET', 'POST'])
@auth.login_required
def importContact(pagination=1):
	count = 0
	email_to_send = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count()
	emails=Email.query.filter_by(user_id=request.cookies.get('blog_id')).order_by(Email.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
	pagin=math.ceil((Email.query.filter_by(user_id=request.cookies.get('blog_id')).count())/limit)
	if(math.ceil(Email.query.filter_by(user_id=request.cookies.get('blog_id')).count())%limit != 0 ):
		pagin=int(pagin+1)
	# emails=Email.query.order_by(Email.id.desc())
	groups = Group.query.filter_by(user_id=request.cookies.get('blog_id')).all()
	if request.method == 'GET':
		return render_template('admin/form/import.html',email_to_send=email_to_send,current_pagin=int(pagination),pagin=int(pagin),count=count,groups=groups,emails=emails)
	else:
		#add upload and add new email list
		now = str(datetime.now())
		now= now.replace(':',"",10).replace(' ','',4).replace('.','',5).replace('-','',5)
   		
		group_id=request.form['category_id']
		file_csv = request.files['contact_file']
		csv=secure_filename(file_csv.filename)
		# return group+"-"+csv
		filename = now+"_"+csv
		if csv!="":
			file_csv.save(os.path.join(app.config['UPLOAD_FOLDER_CONTACT'], filename))
			with open('static/files/contacts/'+filename,'r') as f:
				config=str(f.read())
				# config=config.replace('"\n','"')
				data=config.split('\n')
				help2=1
				for all_rows in data:
					if help2>1:
						try:
							data_row=all_rows.split(",")
							contact_email = data_row[28].replace("\r",'');
							# return str(len(data_row))
							firstname = data_row[1]
							lastname=data_row[3]
							if firstname=="":
								firstname=data_row[0]
							if firstname=="":
								firstname = contact_email.split("@")[0]
							if contact_email!="":
								obj=Email.query.filter_by(email=contact_email).filter_by(user_id=request.cookies.get('blog_id')).limit(1)
								if obj.count()<=0:
									obj=Email(contact_email,firstname,lastname,request.cookies.get('blog_id'))
			   						status=Email.add(obj)
			   						count = count + 1
			   						if not status:
										#if success,add user to default group
										temp = Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(email=contact_email)
										for tmp in temp:
											obj = Emailgroup(tmp.id,group_id,request.cookies.get('blog_id')
												)
											status2 = Emailgroup.add(obj)
								# print "===>"+str(help2)+":"+contact_email+" : "+firstname+":"+lastname+":"+str(group_id)+"-->"
								
							# else:
							# 	print "============================="

						except Exception as e:
							set_error=0
							print e.message
					help2 = help2 + 1
			if count ==0:
				flash("No email added")
			elif count == 1:
				flash(str(count)+" email add successfully")
			else:
				flash(str(count)+" emails add successfully")
		else:
			print "CSV file is null."		
		return redirect(url_for("importContact"))
#after send need to clear variables
def sendEmail():
	with app.app_context():
		random_time = randint(0,240)
		print '======>>> time to send = '+str((int(120+random_time))/60)
		time.sleep(random_time)
		global email_count
		global subject
		global description
		global group_send
		obj=EmailList.query.distinct(EmailList.user_id).limit(1000)
		if obj.count()>0:
			email_count=email_count+1
			for ob in obj:
				#send email
				app.config.update(
					DEBUG=True,
					#EMAIL SETTINGS
					MAIL_SERVER='smtp.gmail.com',
					MAIL_PORT=465,
					MAIL_USE_SSL=True,
					MAIL_USERNAME = ob.sending_email,
					MAIL_PASSWORD = ob.sending_password
					)
				mail=Mail(app)
				print ob.name
				try:
					description = ob.description
					subject = ob.subject
					subject_send=subject.replace("{{name}}",ob.name)
					description_send = description.replace("{{name}}",ob.name)
					
					subject_send=subject_send.replace("{{email}}",ob.email)
					description_send = description_send.replace("{{email}}",ob.email)
					msg = Message(subject_send,sender=(ob.sending_name,ob.sending_email),recipients=[ob.email],reply_to=ob.reply_to)
					message_string=str(description_send)
					msg.html = message_string
					mail.send(msg)	
					#remove email from email list after send
					EmailList.delete(ob)
				except Exception as e:
					print "Error: "+e.message
		else:
			# Shutdown your cron thread if the web process is stopped
			sched.shutdown(wait=False)

			
			#clear variables
			email_count=0
			subject=''
			description=''
			group_send=[]
@app.route('/email', methods = ['GET', 'POST'])
@app.route('/email/', methods = ['GET', 'POST'])
@auth.login_required
def admin_email():

	email_to_send = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count()
	if request.method=="GET":
		groups=Group.query.filter_by(user_id=request.cookies.get('blog_id')).order_by(Group.id.desc())
		return render_template("admin/form/sendmail.html",name=request.cookies.get("blog_name"),email=request.cookies.get("blog_email"),password=request.cookies.get("blog_password"),email_to_send=email_to_send,groups=groups)
	else:
		global subject
		global description
		global group_send
		global sched
		sched = Scheduler()
		subject = request.form['subject']
		description = request.form['description']
		reply_to = request.form['reply_to']
		groups = request.form.getlist('groups')
		sending_email= request.form['send_from']
		sending_password= request.form['password']
		sending_name= request.form['name']
		# return 'dd'
		if reply_to=="":
			reply_to = email
		for group in groups:
			print str(group)+"========="
			group_send.append(int(group))
			# obj=Emailgroup.query.join(Email,Emailgroup.email_id==Email.id).filter(Emailgroup.group_id==int(group))
			obj=Emailgroup.query.filter_by(user_id=request.cookies.get('blog_id')).filter(Emailgroup.group_id==int(group))
			for o in obj:
				tmp=Email.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(id=o.email_id)
				for t in tmp:
					#add to email list to send 
					try:
						help=EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(email=t.email)
						if help.count()<=0:
							temp_object = EmailList(t.firstname,t.email,subject,description,reply_to,sending_email,sending_password,sending_name,request.cookies.get('blog_id'))
							EmailList.add(temp_object)
						# else:
						# 	print "Email already exists."
					except Exception as e:
						print e.message
		email_to_send = EmailList.query.filter_by(user_id=request.cookies.get('blog_id')).count()
		sched.add_interval_job(sendEmail, seconds=120) #120 seconds
		sched.start()
		flash("Your Email will be sent successfully.")
		groups = Group.query.filter_by(user_id=request.cookies.get('blog_id')).all()
		return render_template("admin/form/sendmail.html",email=email,password=pwd,email_to_send=email_to_send,groups=groups)

@app.route('/checkemail/<email_id>/<group_id>/<action>/', methods=['POST', 'GET'])
@app.route('/checkemail/<email_id>/<group_id>/<action>', methods=['POST', 'GET'])
def check_email(email_id,group_id,action):
	email_id=int(email_id)
	group_id=int(group_id)
	if action=="check":
		obj=Emailgroup.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(email_id=email_id).filter_by(group_id=group_id)
		if obj.count()>0:
			return jsonify({'status':True })
		else:
			return jsonify({'status':False })
	elif action=="remove":
		obj=Emailgroup.query.filter_by(user_id=request.cookies.get('blog_id')).filter_by(email_id=email_id).filter_by(group_id=group_id).first()
		Emailgroup.delete(obj)
		return jsonify({'status':'success'})
	elif action=="add":
		emailgroup = Emailgroup(email_id,group_id,request.cookies.get('blog_id'))
    	status = Emailgroup.add(emailgroup)
        if not status:
            return jsonify({'status':'success' })
       	else:
       		return jsonify({'status':'fail' })
#############End personalize email####################
#End Middleware
#client
@app.errorhandler(404)
def page_not_found(e):
	return render_template("admin/404.html")

if __name__ == '__main__':
	 app.run(debug = True,host='0.0.0.0')
#replace white space:
#http://docs.python-requests.org/en/master/user/quickstart/