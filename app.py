from flask import Flask, render_template, request, session, url_for, redirect
from utils import auth
from utils import class_manager as cm
import sqlite3
import os, datetime

app = Flask(__name__)
app.secret_key = os.urandom(64)
DIR = os.path.dirname(__file__) or '.'
DIR += '/'

@app.route('/')
def mainpage():

    if 'username' in session:
        print "IN SESSION NOW: " + session['username']
        if auth.get_user_type(session['username']) == 'student':
            return redirect('student_home')
        elif auth.get_user_type(session['username']) == 'teacher':
            return redirect('teacher_home')
        else:
            return 'Error'
    else:
        return render_template('login.html')

@app.errorhandler(404)
def page_not_found(e):
    return "this is the page not found error"

@app.route('/register/', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form['username'] 
    email = request.form['email']
    user_type = request.form['usertype']
    password = request.form['password']
    print "ON REGISTER PAGE...." + username
    
    if auth.add_user(username, password, user_type, email):
        print "REGISTERED: " + username 
        return redirect('login')
    return render_template('register.html')



@app.route('/student_home/',methods=['GET','POST'])
def student_home():
    if 'username' not in session:
        return redirect('/')

    user = session['username']
    if request.method == 'POST':
        course_id = request.form['magic_code']
        cm.user_join_class(auth.get_id_from_username(user), course_id)
        print "class joined: "+course_id

    courses = cm.get_user_classes(auth.get_id_from_username(user))
    course_names = {c:cm.get_class_info(c)['class_name'] for c in courses}
    print course_names            
    return render_template('student_home.html', user=user, course_names = course_names)


@app.route('/teacher_home/')
def teacher_home():
    if 'username' not in session:
        return redirect('/')
    user = session['username']
    courses = cm.get_user_classes(auth.get_id_from_username(user))
    course_names = {c:cm.get_class_info(c)['class_name'] for c in courses}
    print course_names
    return render_template('teacher_home.html', user=user, course_names=course_names)

@app.route('/review/<class_id>', methods=['GET','POST'])
def review(class_id):
    if 'username' not in session:
        return redirect('/');

    cats = cm.get_categories(int(class_id)) #list of categories
    
    if request.method == "GET":
        info = cm.get_class_info(int(class_id))
        info['days'] = '-'.join(d for d in info['days'])
        return render_template('review.html', info=info, live=cm.is_class_in_session(int(class_id)), categories=cats, cid=class_id);
    else:
        #build dictionary of scores for each category
        scores = {}
        for c in cats:
            scores[c] = int(request.form[c])
        comment = request.form["comment"] or ""
        user_id = auth.get_id_from_username(session["username"])
        cm.add_review(int(class_id),scores,comment,user_id)
        return redirect(url_for('student_home'))
        

#teacher only!
@app.route('/class_home/<class_id>')
def class_home(class_id):
    if 'username' not in session:
        return redirect('/');
    '''
    info['class_name'] = res[0]
    info['instructor_name'] = res[1]
    info['days'] = res[2].split(',')
    info['time_start'] = res[3]
    info['time_end'] = res[4]
    info['categories'] = res[5].split(',')
    info['code'] = res[6]
    '''
    info = cm.get_class_info(int(class_id))    
    return render_template('class_home.html', info=info, cid=class_id, live=cm.is_class_in_session(int(class_id)));

@app.route('/add_course/', methods=['GET','POST'])
def add_course():
    if 'username' not in session:
        return redirect('/')
    
    if request.method == 'POST':
            
        name = request.form['coursename']
        start = request.form['start_time']
        end = request.form['end_time']
        days = request.form.getlist("days")
        cm.create_class(name, session['username'], days, start, end)
        print 'class created'
        return redirect('/')
    else:
        return render_template('add_course.html')

@app.route('/class_data/<class_id>',methods=['GET','POST'])
def class_data(class_id):
    if 'username' not in session:
        return redirect('/')
    info = cm.get_class_info(int(class_id))
    cats = cm.get_categories(int(class_id)) #list of categories

    if request.method == 'GET':
        date = str(datetime.datetime.now().date())
    else:
        date = request.form['date']

    data_month = cm.get_reviews(int(class_id),date,'month')
    #data_week = [e for e in date_month[0] if e['date'] <= '%s %s' % (str(cm.get_first_class_date(date,info['days']).date()),info['time_start'])]
    #data_today = [e for e in date_week[0] if e['date'] <= '%s %s' % (date,info['time_start'])]

   # data_week = (data_week,{e['score'] for e in data_week)
    data_week = cm.get_reviews(int(class_id),date,'week')
    data_day = cm.get_reviews(int(class_id),date,'day')
                 
        
    return render_template('class_data.html', info=info, cid=class_id, categories=cats,data_day=data_day,data_week=data_week,data_month=data_month,date=date);
    

@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if auth.login(username, password) == True:            
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', msg="Invalid login.", good=False)
    return render_template('login.html')




@app.route('/logout/')
def logout():
    if 'username' not in session:
        return redirect('/')
    session.pop('username')
    return redirect('/')

    
    

if __name__ == '__main__':
    app.debug = True
    app.run()
