from flask import Flask, render_template, redirect, request, flash, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from password_generator import PasswordGenerator
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import json, requests, psycopg2, random, string, pytz

with open('import.json', 'r') as c:
    json = json.load(c)["jsondata"]

app = Flask(__name__)

app.secret_key = "jdjsdjJJJJjhi*(%#@-CGV-PORTAL-VERIFY-@)(&$%wer387jjhdsujs28729&&*(*&"
app.config['SQLALCHEMY_DATABASE_URI'] = json['databaseUri']
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'loginPage'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    subname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    users = db.relationship('Users', cascade = "all,delete", backref='user')
    certificates = db.relationship('Certificate', cascade = "all,delete", backref='student')


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    lastlogin = db.Column(db.String(50), nullable=False)
    createddate = db.Column(db.String(50), nullable=False)
    orgid = db.Column(db.Integer, db.ForeignKey('organization.id'))
    certificate = db.relationship('Certificate',cascade = "all,delete", backref='certificate')


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    coursename = db.Column(db.String(500), nullable=False)
    dateupdate = db.Column(db.String(50), nullable=False)
    createddate = db.Column(db.String(50), nullable=False)
    orgid = db.Column(db.Integer, db.ForeignKey('organization.id'))
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(50), nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(50), nullable=False)

IST = pytz.timezone('Asia/Kolkata')
x = datetime.now(IST)
time = x.strftime("%c")
host=bool(json["host_status"])
ipc = json["demo_ip"]

# @app.route('/test')
# def test_page():
#     entry = Organization(name="Vignesh Shetty", email='vigneshshetty.in@gmail.com', subname="Backend Technologies", phone="6362490109", date=time)
#     db.session.add(entry)
#     db.session.commit()
#     return redirect(url_for('loginPage'))

@app.route('/forgot', methods = ['GET', 'POST'])
def forgot_password_page():
    if (request.method == 'POST'):
        email=request.form.get('email')
        post = Users.query.filter_by(email=email).first()
        name = post.name;
        if(post!=None):
            if(post.email==json["admin_email"]):
                flash("You can't reset password of administrator!", "danger")
            else:
                pwo = PasswordGenerator()
                password = pwo.generate()
                passwordemial = password
                post.password = sha256_crypt.hash(password)
                db.session.commit()
                subject = "New password generated at "+time
                content1 = '''<!DOCTYPE html><html lang="en" ><head><meta charset="UTF-8"><title>Register CGV</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"><h1 style="font-size:20px;margin:16px 0;color:#333;text-align:center">India’s Largest Online Verification Network</h1><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">Hey, ''' + str(name) + '''</p><div style="background:#f6f7f8;border-radius:3px"> <br><center><p style="font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;">Password : '''+str(passwordemial)+'''</p><center><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;margin-bottom:0;text-align:center"> <a href="'''
                content2 = json["site_url"] + '''/login" style="border-radius:3px;background:#3aa54c;color:#fff;display:block;font-weight:700;font-size:16px;line-height:1.25em;margin:24px auto 6px;padding:10px 18px;text-decoration:none;width:180px" target="_blank">Login Now!</a></p> <br><br></div><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
                content = content1 + content2
                message = Mail(
                    from_email=('forgot-password@cgv.in.net', 'Security Bot CGV'),
                    to_emails=email,
                    subject=subject,
                    html_content=content)
                try:
                    sg = SendGridAPIClient(json['sendgridapi'])
                    response = sg.send(message)
                    flash("You will receive a mail shortly. Password rested successfully!", "success")
                except Exception as e:
                    print(e.message)
        elif(post==None):
                flash("We didn't find your account!", "danger")
                return render_template('forgot-password.html', json=json)

    return render_template('forgot-password.html', json=json)

@app.route('/view/mail', methods = ['GET', 'POST'])
@login_required
def mail_page():
        if(request.method=='POST'):
            fromemail = request.form.get('username')
            name = request.form.get('name')
            fromemail = fromemail+'@cgv.in.net'
            toemail = request.form.get('toemail')
            subject = request.form.get('subject')
            content = request.form.get('editordata')
            html1 = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>CGV</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"> <strong><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">India’s Largest Online Verification Network</p></strong><div style="background:#f6f7f8;border-radius:3px">'''
            html2 = '''</div><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
            content = html1 + content + html2
            message = Mail(
                from_email=(fromemail, name),
                to_emails=toemail,
                subject=subject,
                html_content=content)
            try:
                sg = SendGridAPIClient(json['sendgridapi'])
                response = sg.send(message)
                flash("Email sent successfully!", "success")
            except Exception as e:
                print("Error")
                flash("Error while sending mail!", "danger")
        return render_template('mail.html', json=json, c_user_name= current_user.name)

@app.route('/')
def home_page():
    return render_template('index.html', json=json)

@app.route('/contact', methods = ['GET', 'POST'])
def contact_page():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('editordata')
        if(host==True):
            ip_address = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            ip_address = ipc;
        url = requests.get("http://ip-api.com/json/{}".format(ip_address))
        j = url.json()
        city = j["city"]
        country = j["country"]
        entry = Contact(name=name, phone=phone, message=message,ip=ip_address, city=city, country=country, date=time, email=email)
        db.session.add(entry)
        db.session.commit()
        flash("Thank you for contacting us – we will get back to you soon!", "success")
    return redirect('/#footer')

@app.route('/feedback', methods = ['GET', 'POST'])
def feedback_page():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        rating = request.form.get('rating')
        message = request.form.get('message')
        if (host == True):
            ip_address = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            ip_address = ipc;
        url = requests.get("http://ip-api.com/json/{}".format(ip_address))
        j = url.json()
        city = j["city"]
        country = j["country"]
        entry = Feedback(name=name, phone=phone, rating=rating, message=message,ip=ip_address, city=city, country=country, date=time, email=email)
        db.session.add(entry)
        db.session.commit()
        flash("Thank you for feedback – we will get back to you soon!", "success")
    return redirect('/#footer')

@app.route('/newsletter', methods = ['GET', 'POST'])
def newsletter_page():
    if (request.method == 'POST'):
        email = request.form.get('email')
        if (host == True):
            ip_address = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            ip_address = ipc;
        url = requests.get("http://ip-api.com/json/{}".format(ip_address))
        j = url.json()
        city = j["city"]
        country = j["country"]
        post = Newsletter.query.filter_by(email=email).first()
        if(post==None):
            entry = Newsletter(ip=ip_address, city=city, country=country, date=time, email=email)
            db.session.add(entry)
            db.session.commit()
            flash("Thank you for subscribing!", "success")
        else:
            flash("You have already subscribed!", "danger")
    return redirect('/#footer')

@app.route("/certificate/verify", methods=['GET', 'POST'])
def certificate_verify():
    if (host == True):
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
    else:
        ip_address = ipc;
    if(request.method=='POST'):
        certificateno = request.form.get('certificateno')
        postc = Certificate.query.filter_by(number=certificateno).first()
        if(postc!=None):
            posto = Organization.query.filter_by(id=postc.orgid).first()
            flash("Certificate Number Valid!", "success")
            return render_template('verify2.html', postc=postc, posto=posto, json=json, ip=ip_address)
        elif(postc==None):
            flash("No details found. Contact your organization!", "danger")
    return render_template('verify.html', json=json, ip=ip_address)

@app.route("/certificate/generate", methods=['GET', 'POST'])
def certificate_generate():
    if (host == True):
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
    else:
        ip_address = ipc;
    if(request.method=='POST'):
        certificateno = request.form.get('certificateno')
        postc = Certificate.query.filter_by(number=certificateno).first()
        if(postc!=None):
            posto = Organization.query.filter_by(id=postc.orgid).first()
            return render_template('certificate.html', postc=postc, posto=posto, json=json, ip=ip_address)
        elif (postc == None):
            flash("No details found. Contact your organization!", "danger")
    return render_template('generate.html', json=json, ip=ip_address)

@app.route("/certify/<string:number>", methods=['GET'])
def certificate_generate_string(number):
    postc = Certificate.query.filter_by(number=number).first()
    if(postc!=None):
        posto = Organization.query.filter_by(id=postc.orgid).first()
        return render_template('certificate.html', postc=postc, posto=posto, json=json)
    else:
        return redirect('/')

@app.route("/certifyd/<string:number>", methods=['GET'])
def certificate_generated_string(number):
    postc = Certificate.query.filter_by(number=number).first()
    if(postc!=None):
        posto = Organization.query.filter_by(id=postc.orgid).first()
        style="display: none;"
        return render_template('certificate.html', postc=postc, posto=posto, json=json, style=style)
    else:
        return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def loginPage():
    # TODO: Check for active session
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        response = Users.query.filter_by(email=email).first()
        if((response != None) and ( response.email == email ) and ( sha256_crypt.verify(password, response.password )==1) and (response.status==1)):
            updateloginTime = Users.query.filter_by(email=email).first()
            updateloginTime.lastlogin = time
            db.session.commit()
            if (host == True):
                ip_address = request.environ['HTTP_X_FORWARDED_FOR']
            else:
                ip_address = ipc;
            url = requests.get("http://ip-api.com/json/{}".format(ip_address))
            j = url.json()
            city = j["city"]
            country = j["country"]
            html_text1 = '''<!DOCTYPE html><html lang="en" ><head><meta charset="UTF-8"><title>Login Alert</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"><h1 style="font-size:20px;margin:16px 0;color:#333;text-align:center">Is that you?</h1><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">We noticed you logged in to your CGV account from a new device and a new location.</p> <br><div style="background:#f6f7f8;border-radius:3px"> <br> City : '''
            html_final = html_text1 + str(city) + '''<br><br> Country : '''+ str(country)+'''<br><br>Time : '''+str(time)+'''<br><br>IP : '''+str(ip_address)
            html_text2 = '''<br><p>Tip: To keep your account secured, please contact us to update your email id. Ignore if it’s already updated.</p></div><br><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
            html_final = html_final + html_text2
            subject = " New device login from "+str(city)+", "+str(country)+" detected."
            message = Mail(
                from_email=('login-alert@cgv.in.net', 'Security Bot CGV'),
                to_emails=email,
                subject=subject,
                html_content=html_final)
            try:
                sg = SendGridAPIClient(json['sendgridapi'])
                responsemail = sg.send(message)
            except Exception as e:
                print(e)
            login_user(response, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard_page'))
        else:
            flash("Invalid credentials or account not activated!", "danger")
            return render_template('login.html', json=json)
    else:
        return render_template('login.html', json=json)

@app.route('/register',methods = ['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if(password!=password2):
            flash("Password unmatched!", "danger")
            return render_template('register.html', json=json)
        else:
            password = sha256_crypt.hash(password)
            response = Users.query.filter_by(email=email).first()
            if(response==None):
                entry = Users(name=name, email=email, password=password,lastlogin=time, createddate=time, status=0, orgid=1)
                db.session.add(entry)
                db.session.commit()
                flash("Now contact your organization head for account activation!", "success")
                subject = "Welcome aboard " + name + "!"
                content1 = '''<!DOCTYPE html><html lang="en" ><head><meta charset="UTF-8"><title>Register CGV</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"><h1 style="font-size:20px;margin:16px 0;color:#333;text-align:center">India’s Largest Online Verification Network</h1><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">Hey, '''+str(name)+'''</p><div style="background:#f6f7f8;border-radius:3px"> <br><p style="font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;">Now contact your organization head for your account activation. Once activated click on link below to login.</p><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;margin-bottom:0;text-align:center"> <a href="'''
                content2 = json["site_url"]+'''/login" style="border-radius:3px;background:#3aa54c;color:#fff;display:block;font-weight:700;font-size:16px;line-height:1.25em;margin:24px auto 6px;padding:10px 18px;text-decoration:none;width:180px" target="_blank">Login Now!</a></p> <br><br></div><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
                content = content1 +content2
                message = Mail(
                    from_email=('register-user@cgv.in.net', 'Register Bot CGV'),
                    to_emails=email,
                    subject=subject,
                    html_content=content)
                try:
                    sg = SendGridAPIClient(json['sendgridapi'])
                    response = sg.send(message)
                except Exception as e:
                    print("Error!")
                    flash("Error while sending mail!", "danger")
            else:
                flash("User exist!", "danger")
                return render_template('register.html', json=json)

    return render_template('register.html', json=json)

@app.route('/dashboard')
@login_required
def dashboard_page():
        postc=len(Certificate.query.order_by(Certificate.id).all())
        postct=len(Contact.query.order_by(Contact.id).all())
        postf=len(Feedback.query.order_by(Feedback.id).all())
        postn=len(Newsletter.query.order_by(Newsletter.id).all())
        return render_template('dashboard.html', json=json, postc=postc, postct=postct, postf=postf, postn=postn, c_user_name= current_user.name)

@app.route("/view/org", methods = ['GET', 'POST'])
@login_required
def view_org_page():
        post=Organization.query.order_by(Organization.id).all()
        return render_template('org_table.html', post=post, json=json, c_user_name= current_user.name)

@app.route("/view/users", methods = ['GET', 'POST'])
@login_required
def view_users_page():
        if(current_user.email==json["admin_email"]):
            post = Users.query.order_by(Users.id).all()
            return render_template('users_table.html', post=post, json=json, c_user_name= current_user.name)
        else:
            return render_template('block.html',json=json, c_user_name= current_user.name)

@app.route("/view/certificates", methods = ['GET', 'POST'])
@login_required
def view_certificate_page():
        post = Certificate.query.order_by(Certificate.id).all()
        return render_template('certificate_table.html', post=post, json=json, c_user_name= current_user.name)

@app.route("/view/contacts", methods = ['GET', 'POST'])
@login_required
def view_contacts_page():
        post = Contact.query.order_by(Contact.id).all()
        return render_template('contact_table.html', post=post, json=json, c_user_name= current_user.name)

@app.route("/view/feedbacks", methods = ['GET', 'POST'])
@login_required
def view_feedbacks_page():
        post = Feedback.query.order_by(Feedback.id).all()
        return render_template('feedback_table.html', post=post, json=json, c_user_name= current_user.name)

@app.route("/view/newsletters", methods = ['GET', 'POST'])
@login_required
def view_newsletters_page():
        post = Newsletter.query.order_by(Newsletter.id).all()
        return render_template('newsletter_table.html', post=post, json=json, c_user_name= current_user.name)

@app.route("/view/messages/<string:id>", methods=['GET'])
@login_required
def view_message_page(id):
        post = Contact.query.filter_by(id=id).first()
        return render_template('view_message.html',post=post, json=json, c_user_name= current_user.name)

@app.route("/edit/certificates/<string:id>", methods = ['GET', 'POST'])
@login_required
def edit_certificates_page(id):
            if request.method == 'POST':
                name = request.form.get('name')
                letters = string.ascii_letters
                number = ''.join(random.choice(letters) for i in range(4))
                number = 'CGV'+name[0:4].upper()+number
                coursename = request.form.get('coursename')
                userid = current_user.id
                email = request.form.get('email')
                orgid = current_user.orgid
                dateupdate = time
                createddate = time
                if id=='0':
                    postcheck = Certificate.query.filter_by(number=number).first()
                    if(postcheck==None):
                        post = Certificate(name=name,number=number, email=email,coursename=coursename, userid=userid, orgid=orgid, dateupdate=dateupdate, createddate=createddate)
                        db.session.add(post)
                        db.session.commit()
                        subject = "Certificate Generated With Certificate Number : "+str(number)
                        content1 = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Certificate Download</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"><h1 style="font-size:20px;margin:16px 0;color:#333;text-align:center">India’s Largest Online Verification Network</h1><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">Hey, '''+str(name)
                        content2 = '''</p><div style="background:#f6f7f8;border-radius:3px"> <br><p>Congratulations! Your certificate has been issued successfully.</p><p>Certificate Number : '''+str(number)
                        content3 = '''</p><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;margin-bottom:0;text-align:center"> <a href="https://'''+json["site_url"]+'''/certify/'''+str(number)+'''" style="border-radius:3px;background:#3aa54c;color:#fff;display:block;font-weight:700;font-size:16px;line-height:1.25em;margin:24px auto 6px;padding:10px 18px;text-decoration:none;width:215px" target="_blank"> Download Certificate Here!</a><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;margin-bottom:0;text-align:center"> <a href="'''+json["site_url"]+'''/certificate/verify" style="border-radius:3px;background:#3aa54c;color:#fff;display:block;font-weight:700;font-size:16px;line-height:1.25em;margin:24px auto 6px;padding:10px 18px;text-decoration:none;width:215px" target="_blank"> E-Verify Certificate Here!</a></p> <br> <br></div><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
                        content = content1 +content2 +content3
                        message = Mail(
                            from_email=('certificate-generate@cgv.in.net', 'Certificate Generate Bot CGV'),
                            to_emails=email,
                            subject=subject,
                            html_content=content)
                        try:
                            sg = SendGridAPIClient(json['sendgridapi'])
                            response = sg.send(message)
                        except Exception as e:
                            print("Error!")
                            flash("Error while sending mail!", "danger")
                        flash("Certificate added successfully!", "success")
                    else:
                        flash("Certificate already exist!", "danger")
                else:
                    post = Certificate.query.filter_by(id=id).first()
                    post.name = name
                    post.coursename = coursename
                    post.email = email
                    post.userid = current_user.id
                    post.orgid = current_user.orgid
                    post.dateupdate = time
                    db.session.commit()
                    flash("Certificate edited successfully!", "success")
                    return redirect('/edit/certificates/'+id)
            posto = Organization.query.filter_by().all()
            postu = Users.query.filter_by().all()
            post = Certificate.query.filter_by(id=id).first()
            return render_template('add_edit_certificate.html', json=json, id=id, post=post, posto=posto, postu=postu, c_user_name= current_user.name)

@app.route("/edit/users/<string:id>", methods = ['GET', 'POST'])
@login_required
def edit_users_page(id):
            if request.method == 'POST':
                name = request.form.get('name')
                email = request.form.get('email')
                password = sha256_crypt.hash(request.form.get('password'))
                status = request.form.get('status')
                orgid = request.form.get('orgid')
                lastlogin = time
                createddate = time
                if id=='0':
                    postvalidate = Users.query.filter_by(email=email).first()
                    if(postvalidate==None):
                        post = Users(name=name,email=email, password=password, status=status, orgid=orgid, lastlogin=lastlogin, createddate=createddate)
                        db.session.add(post)
                        db.session.commit()
                        subject = "Welcome aboard " + name + "!"
                        content1 = '''<!DOCTYPE html><html lang="en" ><head><meta charset="UTF-8"><title>Register CGV</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"><h1 style="font-size:20px;margin:16px 0;color:#333;text-align:center">India’s Largest Online Verification Network</h1><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">Hey, ''' + str(name) + '''</p><div style="background:#f6f7f8;border-radius:3px"> <br><p style="font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;">Now contact your organization head for your account activation. Once activated click on link below to login.</p><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;margin-bottom:0;text-align:center"> <a href="'''
                        content2 = json["site_url"] + '''/login" style="border-radius:3px;background:#3aa54c;color:#fff;display:block;font-weight:700;font-size:16px;line-height:1.25em;margin:24px auto 6px;padding:10px 18px;text-decoration:none;width:180px" target="_blank">Login Now!</a></p> <br><br></div><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
                        content = content1 + content2
                        message = Mail(
                            from_email=('register-user@cgv.in.net', 'Register Bot CGV'),
                            to_emails=email,
                            subject=subject,
                            html_content=content)
                        try:
                            sg = SendGridAPIClient(json['sendgridapi'])
                            response = sg.send(message)
                        except Exception as e:
                            print("Error!")
                            flash("Error while sending mail!", "danger")
                        flash("User added successfully!", "success")
                    else:
                        flash("User exist!", "danger")
                else:
                    post = Users.query.filter_by(id=id).first()
                    if(post.email==json['admin_email']):
                        flash("You can't edit admin user details!", "danger")
                        return redirect('/view/users')
                    else:
                        post.name = name
                        post.email = email
                        post.password = password
                        post.status = status
                        post.orgid = orgid
                        post.lasylogin = time
                        db.session.commit()
                        flash("User edited successfully!", "success")
                        return redirect('/edit/users/'+id)
            posto = Organization.query.filter_by().all()
            post = Users.query.filter_by(id=id).first()
            return render_template('add_edit_users.html', json=json, id=id, post=post, posto=posto, c_user_name= current_user.name)

@app.route("/activate/users/<string:id>", methods = ['GET', 'POST'])
@login_required
def activate_users(id):
        activate = Users.query.filter_by(id=id).first()
        if(activate.email==json["admin_email"]):
            flash("Administrator account will always be active!", "warning")
            return redirect(url_for('view_users_page'))
        else:
            if(activate.status==1):
                activate.status = 0
                flash("User account deactivated!", "warning")
            else:
                activate.status = 1
                flash("User account activated!", "success")
            db.session.commit()
            return redirect(url_for('view_users_page'))

@app.route("/edit/org/<string:id>", methods = ['GET', 'POST'])
@login_required
def edit_org_page(id):
            if request.method == 'POST':
                name = request.form.get('name')
                subname = request.form.get('subname')
                email = request.form.get('email')
                phone = request.form.get('phone')
                date = time
                if id=='0':
                    post = Organization(name=name, subname=subname, email=email, phone=phone ,date=date)
                    db.session.add(post)
                    db.session.commit()
                    flash("Organization added Successfully!", "success")
                    subject = '''Welcome, '''+str(name)+'''!'''
                    content1 = '''<!DOCTYPE html><html lang="en" ><head><meta charset="UTF-8"><title>Register CGV</title></head><body><table cellspacing="0" cellpadding="0" border="0" style="color:#333;background:#fff;padding:0;margin:0;width:100%;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><tbody><tr width="100%"><td valign="top" align="left" style="background:#eef0f1;font:15px/1.25em 'Helvetica Neue',Arial,Helvetica"><table style="border:none;padding:0 18px;margin:50px auto;width:500px"><tbody><tr width="100%" height="60"><td valign="top" align="left" style="border-top-left-radius:4px;border-top-right-radius:4px;background: white; padding:10px 18px;text-align:center"> <img height="75" width="75" src="https://cdn.discordapp.com/attachments/708550144827719811/792008916451328010/android-chrome-512x512.png" title="CGV" style="font-weight:bold;font-size:18px;color:#fff;vertical-align:top" class="CToWUd"></td></tr><tr width="100%"><td valign="top" align="left" style="background:#fff;padding:18px"><h1 style="font-size:20px;margin:16px 0;color:#333;text-align:center">India’s Largest Online Verification Network</h1><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333;text-align:center">Hey, ''' + str(name) + '''</p><div style="background:#f6f7f8;border-radius:3px"> <br><p style="font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;">New organization created successfully! Now create user and activate user to generate certificates.</p><p style="font:15px/1.25em 'Helvetica Neue',Arial,Helvetica;margin-bottom:0;text-align:center"> <a href="'''
                    content2 = json["site_url"] + '''/register" style="border-radius:3px;background:#3aa54c;color:#fff;display:block;font-weight:700;font-size:16px;line-height:1.25em;margin:24px auto 6px;padding:10px 18px;text-decoration:none;width:180px" target="_blank">Create User Now!</a></p> <br><br></div><p style="font:14px/1.25em 'Helvetica Neue',Arial,Helvetica;color:#333"> <strong>What's CGV?</strong> We generate and verify certificates online which also includes a backend dashboard. Click to know more. <a href="https://cgvcertify.herokuapp.com" style="color:#306f9c;text-decoration:none;font-weight:bold" target="_blank">Learn more »</a></p></td></tr></tbody></table></td></tr></tbody></table></body></html>'''
                    content = content1 + content2
                    message = Mail(
                        from_email=('new-organization@cgv.in.net', 'Organization Bot CGV'),
                        to_emails=email,
                        subject=subject,
                        html_content=content)
                    try:
                        sg = SendGridAPIClient(json['sendgridapi'])
                        response = sg.send(message)
                    except Exception as e:
                        print(e.message)
                else:
                    post = Organization.query.filter_by(id=id).first()
                    if(post.email==json["admin_email"]):
                        flash("Default organization can't be edited!", "warning")
                    else:
                        post.name = name
                        post.subname = subname
                        post.phone = phone
                        post.email = email
                        post.date = date
                        db.session.commit()
                        flash("Organization edited Successfully!", "success")
                    return redirect('/edit/org/'+id)
            post = Organization.query.filter_by(id=id).first()
            return render_template('add_edit_org.html', json=json, post=post, id=id, c_user_name= current_user.name)

@app.route("/delete/org/<string:id>", methods = ['GET', 'POST'])
@login_required
def delete_org_page(id):
        delete_org_page = Organization.query.filter_by(id=id).first()
        if(delete_org_page.email==json["admin_email"]):
            flash("Default organization can't be deleted!", "danger")
        else:
            db.session.delete(delete_org_page)
            db.session.commit()
            flash("Organization deleted successfully!", "success")
        return redirect('/view/org')

@app.route("/delete/users/<string:id>", methods = ['GET', 'POST'])
@login_required
def delete_users_page(id):
        delete_users_page = Users.query.filter_by(id=id).first()
        if(delete_users_page.email!=json["admin_email"]):
            db.session.delete(delete_users_page)
            db.session.commit()
            flash("User deleted successfully!", "success")
        else:
            flash("You can't delete administrator!", "danger")
            return redirect('/view/users')
        return redirect('/view/users')

@app.route("/delete/certificates/<string:id>", methods = ['GET', 'POST'])
@login_required
def delete_certificates_page(id):
        delete_certificates_page = Certificate.query.filter_by(id=id).first()
        db.session.delete(delete_certificates_page)
        db.session.commit()
        flash("Certificate deleted successfully!", "success")
        return redirect('/view/certificates')

@app.route("/delete/contact/<string:id>", methods = ['GET', 'POST'])
@login_required
def delete_contact_page(id):
        delete_contact_page = Contact.query.filter_by(id=id).first()
        db.session.delete(delete_contact_page)
        db.session.commit()
        flash("Contact response deleted successfully!", "success")
        return redirect('/view/contacts')

@app.route("/delete/feedback/<string:id>", methods = ['GET', 'POST'])
@login_required
def delete_feedback_page(id):
        delete_feedback_page = Feedback.query.filter_by(id=id).first()
        db.session.delete(delete_feedback_page)
        db.session.commit()
        flash("Feedback response deleted successfully!", "success")
        return redirect('/view/feedbacks')

@app.route("/delete/newsletter/<string:id>", methods = ['GET', 'POST'])
@login_required
def delete_newsletter_page(id):
        delete_newsletter_page = Newsletter.query.filter_by(id=id).first()
        db.session.delete(delete_newsletter_page)
        db.session.commit()
        flash("Newsletter response deleted successfully!", "success")
        return redirect('/view/newsletters')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out Successfully!', 'success')
    return redirect(url_for('loginPage'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
