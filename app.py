from flask import Flask, render_template, request, session, url_for, redirect
from utils import auth
from utils import class_manager as cm
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(64)
DIR = os.path.dirname(__file__) or '.'
DIR += '/'

@app.route('/')
def mainpage():

    if 'username' in session:
        print "IN SESSION NOW: " + session['username']
        if auth.get_user_type(session['username']) == 'student':
            user = session['username']
            courses = cm.get_user_classes(auth.get_id_from_username(user))
            course_names = {c:cm.get_class_info(c)['class_name'] for c in courses}
            return render_template('student_home.html', user=user, course_names = course_names)
        
        elif auth.get_user_type(session['username']) == 'teacher':
            user = session['username']
            courses = cm.get_user_classes(auth.get_id_from_username(user))
            print str(courses)
            course_names = {c:cm.get_class_info(c)['class_name'] for c in courses}
            return render_template('teacher_home.html', user=user, course_names=course_names)
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



@app.route('/user/<username>/student')
def studentPage():    
    return render_template('student_home.html', user = session['username'])

@app.route('/user/<username>/teacher')
def teacherPage():
    return render_template('teacher_home.html', user = session['username'])


@app.route('/review/<class_id>')
def review():
    return render_template('review.html', course = class_id);        


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




@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
    
    

if __name__ == '__main__':
    app.debug = False
    app.run()
