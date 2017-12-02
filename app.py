from flask import Flask, render_template, request, session, url_for
from utils import auth, class_manager
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def mainpage(): 
    if 'username' in session:
        if auth.get_user_type() == 'student':
            return render_template('student_home.html', user = session['username'])
        elif auth.get_user_type() == 'teacher':
            return render_template('teacher_home.html', user = session['username'])
        else:
            return 'Error';
    else:
        return render_template('login.html')

@app.errorhandler(404)
def page_not_found(e):
    return "Error"

@app.route('/register/', methods = ['Get','Post'])
def register_page():
    if request.method == 'GET':
            return render_template('register.html')
            
    username = form.request['username'] 
    email = form.request['email']
    user_type = form.request['usertype']
    password = form.request['password']
    
    if auth.add_user(username, password, user_type, email):
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
    if request.method == 'POST':
            return render_template('register.html')
        
    class_data = render_template(class_data.html)
    class_home = render_template(class_home.html)
    edit_class = render_template(edit_class.html) 
    


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)




@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
    
    

if __name__ == '__main__':
    app.debug = False
    app.run()
