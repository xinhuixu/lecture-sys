from sqlite3 import connect
import hashlib

f = 'Data/general.db'

    
def add_user(username,password,user_type,email):

    if username == '' or password == '' or user_type == '' or email == '' or username == None or password == None or user_type == None or email == None:
        return False

    db = connect(f)
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username STRING, password STRING, user_type STRING, email STRING, user_id INTEGER, class_ids STRING)')
    
    if len(c.execute('SELECT * FROM users WHERE username==\"%s\"' % (username)).fetchall()) >= 1:
        return False

    
    max_id = c.execute('SELECT MAX(user_id) FROM users').fetchall()[0][0]
    if max_id == None:
        max_id = -1
    hash_obj = hashlib.sha256()
    hash_obj.update(password)
    hash_p = hash_obj.hexdigest()
    c.execute('INSERT INTO users VALUES(\"%s\",\"%s\",\"%s\",\"%s\",%d,\"")' % (username,hash_p,user_type,email,max_id+1))
    db.commit()
    db.close()
    return True

def login(username,password):
    db = connect(f)
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username STRING, password STRING, user_type STRING, email STRING, user_id INTEGER, class_ids STRING)')
    success = False
    res = c.execute('SELECT * FROM users WHERE username==\"%s\"' % (username)).fetchall()
    if len(res) > 0:
        hash_obj = hashlib.sha256()
        hash_obj.update(password)
        hash_p = hash_obj.hexdigest()
        if hash_p == res[0][1]:
            success = True
    db.close()
    return success

