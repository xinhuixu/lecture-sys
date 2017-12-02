from sqlite3 import connect
import datetime, random, string

def get_new_class_id():
    db = connect('Data/general.db')
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS class_ids(id INTEGER)')
    res = c.execute('SELECT MAX(id) from class_ids').fetchall()[0][0]
    if res == None:
        return 0
    return res+1


def update_max_class_ids(new_id):
    db = connect('Data/general.db')
    c = db.cursor()
    c.execute('UPDATE class_ids SET id=%d WHERE id==%d' % (new_id,new_id-1))
    db.commit()
    db.close()

#assuming days is a list of the single letter days
def create_class(class_name,instructor_name,days,time_start,time_end):

    if class_name == '' or days == '' or time_start == '' or time_end == '':
        return False

    new_id = get_new_class_id()
    days = ','.join(d for d in days)
    code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))
    
    db = connect('Data/%d.db' % (new_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    c.execute('INSERT INTO info VALUES(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"\",\"%s\")' % (class_name,instructor_name,days,time_start,time_end,code))
    db.commit()    
    db.close()
    update_max_class_ids(new_id)

    db = connect('Data/general.db')
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS codes(class_id INTEGER, class_code STRING)')
    c.execute('INSERT INTO codes VALUES(%d,\"%s\")' % (new_id,code))
    res = c.execute('SELECT class_ids from users WHERE username==\"%s\"' % (instructor)).fetchall()

    if len(res) == 0:
        return 'Error'

    if res[0][0] == '':
        new_class_ids = '%d:%d' % (new_id,-1)
    else:
        new_class_ids = res[0][0] + ',%d:%d' % (new_id,-1)
    
    db.commit()
    db.close()
    

def get_categories(class_id):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    res = c.execute('SELECT categories from info').fetchall()
    if len(res) == 0:
        return None
    return res[0][0]

def add_review_category(class_id,category):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    res = c.execute('SELECT categories from info').fetchall()
    if len(res) == 0:
        return False
    res = res[0][0]
    if res == '':
        new_categories = category
    else:
        new_categories = res + ',%s' % (category)
    c.execute('UPDATE info SET categories=\"%s\" WHERE categories==\"%s\"' % (new_categories,res))
    db.commit()
    db.close()
    return True

def delete_review_category(class_id,category):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    res = c.execute('SELECT categories from info').fetchall()
    if len(res) == 0:
        return False
    res = res[0][0]
    category_list = res.split(',')
    new_categories = ','.join(c for c in category_list if str(c) != category)
    c.execute('UPDATE info SET categories=\"%s\" WHERE categories==\"%s\"' % (new_categories,res))
    db.commit()
    db.close()
    return True

def get_class_info(class_id):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    res = c.execute('SELECT * from info').fetchall()[0]
    info = {}
    info['class_name'] = res[0]
    info['instructor_name'] = res[1]
    info['days'] = res[2].split(',')
    info['time_start'] = res[3]
    info['time_end'] = res[4]
    info['categories'] = res[5].split(',')
    info['code'] = res[6]
    return info

def is_class_in_session(class_id):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    res =  c.execute('SELECT time_start, time_end from info').fetchall()
    if len(res) == 0:
        return None
    return res[0][0] <= str(datetime.datetime.now.time()) and res[0][1] >= str(datetime.datetime.now.time())
    
       
def get_user_classes(user_id):
    db = connect('Data/general.db')
    c = db.cursor()
    res = c.execute('SELECT class_ids from users WHERE user_id==%d' % (user_id)).fetchall()
    if len(res) == 0:
        return None
    classes = {}
    split_info = res[0].split(',')
    for c in split_info:
        kv_split = c.split(':')
        classes[kv_split[0]] = kv_split[1]
    return classes


def user_join_class(user_id,class_code):
    db = connect('Data/general.db')
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS codes(class_id INTEGER, class_code STRING)')
    res = c.execute('SELECT class_id FROM codes WHERE class_code==\"%s\")' % (class_code)).fetchall()
    if len(res) == 0:
        return False
    add_user_to_class(res[0][0],user_id)
    return True
    
    
def add_user_to_class(class_id,user_id):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students(user_id INTEGER, class_user_id)')
    max_id = c.execute('SELECT MAX(class_user_id) from students').fetchall()[0][0]
    if max_id == None:
        c.execute('INSERT INTO students VALUES(%d,%d)' % (user_id,0))
        max_id = 0
    else:
        c.execute('INSERT INTO students VALUES(%d,%d)' % (user_id,max_id+1))
        max_id += 1
    db.commit()
    db.close()

    db = connect('Data/general.db')
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username STRING, password STRING, user_type STRING, email STRING, user_id INTEGER, class_ids STRING)')
    res = c.execute('SELECT class_ids from users WHERE user_id==%d' % (user_id)).fetchall()

    if len(res) == 0:
        return 'Error'

    if res[0][0] == '':
        new_class_ids = '%d:%d' % (class_id,max_id)
    else:
        new_class_ids = res[0][0] + ',%d:%d' % (class_id,max_id)

    c.execute('UPDATE users SET class_ids=\"%s\" WHERE user_id==%d' % (new_class_ids,user_id))
        
    
def get_class_user_id(class_id,user_id):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students(user_id INTEGER, class_user_id)')
    res = c.execute('SELECT class_user_id from students WHERE user_id==%d' % (user_id)).fetchall()
    db.close()
    if len(res) == 0:
        return None
    return res[0][0]
    
#assuming scores is dictionary
def add_review(class_id,scores,comments,user_id):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS reviews(date STRING, time STRING, scores STRING, comments STRING, class_user_id INTEGER)')
    res = c.execute('SELECT categories from info').fetchall()[0][0]
    category_list = res.split(',')
    scores_string = ','.join('%s:%d' % (c,scores[c]) for c in category_list)
    class_user_id = get_class_user_id(class_id,user_id)

    if class_user_id == None:
        db.close()
        return False

    today = datetime.datetime.now() 
    date = str(today.date())
    time = str(today.time()).split('.')[0]
    c.execute('INSERT INTO reviews VALUES(\"%s\",\"%s\",\"%s\",\"%s\",%d)' % (date,time,scores_string,comments,class_user_id))
    db.commit()
    db.close()
    return True
    
def get_next_class_date(date,days):
    weekday_num_to_str = {0:'M',1:'T',2:'W',3:'R',4:'F',5:'S',6:'U'}
    weekday_str_to_num = {'M':0,'T':1,'W':2,'R':3,'F':4,'S':5,'U':6}
    date = datetime.datetime.strptime(date,'%Y-%m-%d')
    index = days.index(weekday_num_to_str[date.weekday()])
    if index == len(days)-1:
        index = 0
    else:
        index += 1
    days_ahead = weekday_str_to_num[days[index]]-date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)
    
def get_first_class_date(date,days):
    weekday_num_to_str = {0:'M',1:'T',2:'W',3:'R',4:'F',5:'S',6:'U'}
    weekday_str_to_num = {'M':0,'T':1,'W':2,'R':3,'F':4,'S':5,'U':6}
    date = datetime.datetime.strptime(date,'%Y-%m-%d')
    days_behind = date.weekday() - weekday_str_to_num[days[0]]
    return date - datetime.timedelta(days_behind)


#assuming date is is yyyy-mm-dd format
#mode is day/week/month
def get_reviews(class_id,date,mode='day'):
    db = connect('Data/%d.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    c.execute('CREATE TABLE IF NOT EXISTS reviews(date STRING, time STRING, scores STRING, comments STRING, class_user_id INTEGER)')
    res = c.execute('SELECT days,time_start,categories from info').fetchall()
    
    if len(res) > 0:
        res = res[0]
    else:
        return None
        
    days = res[0].split(',')
    start_time = res[1]
    categories = res[2].split(',')
    time_split = start_time.split(':')
    next_class_date = get_next_class_date(date,days)
    next_class_date = next_class_date.replace(hour=int(time_split[0]),minute=int(time_split[1]))

    if mode == 'day':
        full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M'))
    elif mode == 'week':
        first_class_date = get_first_class_date(date,days)
        first_class_date = first_class_date.replace(hour=int(time_split[0]),minute=int(time_split[1]))
        full_c_datetime_string = str(first_class_date)
    elif mode == 'month':
        full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M')).replace(day=1)
        
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    averages = {c:[] for c in categories}
    
    for entry in res:
        info = {}
        info['date'] = entry[0]
        info['time'] = entry[1]
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        scores = {}
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]] = int(split_parts[1])
            averages[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)

    averages = {c:sum(averages[c])/float(len(averages[c])) for c in averages}
    return (reviews,averages)




'''
create_class('sample','me',['M','W','F'],'10:00','10:53')
add_review_category(0,'volume')
add_review_category(0,'relevance')
add_review_category(0,'clarity')
delete_review_category(0,'relevance')

auth.add_user('one','pass','student','a@a.com')
auth.add_user('two','pass','student','a@a.com')
auth.add_user('three','pass','student','a@a.com')

add_user_to_class(0,0)
add_user_to_class(0,1)
add_user_to_class(0,2)

print add_review(0,{'volume':3,'clarity':3},'hello',0)
print add_review(0,{'volume':2,'clarity':3},'world',1)
print add_review(0,{'volume':3,'clarity':1},'everyone',2)

print get_reviews(0,'2017-12-01')
'''

















'''
#DEPRECATED

def get_day_reviews(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    c.execute('CREATE TABLE IF NOT EXISTS reviews(date STRING, time STRING, scores STRING, comments STRING, class_user_id INTEGER)')
    res = c.execute('SELECT days,time_start,categories from info').fetchall()
    
    if len(res) > 0:
        res = res[0]
    else:
        return None
        
    days = res[0].split(',')
    start_time = res[1]
    categories = res[2].split(',')
    next_class_date = get_next_class_date(date,days)
    time_split = start_time.split(':')
    next_class_date = next_class_date.replace(hour=int(time_split[0]),minute=int(time_split[1]))
    full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M'))
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    averages = {c:[] for c in categories}
    
    for entry in res:
        info = {}
        info['date'] = entry[0]
        info['time'] = entry[1]
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        scores = {}
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]] = int(split_parts[1])
            averages[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)

    averages = {c:sum(averages[c])/float(len(averages[c])) for c in averages}
    return (reviews,averages)

def get_week_reviews(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    c.execute('CREATE TABLE IF NOT EXISTS reviews(date STRING, time STRING, scores STRING, comments STRING, class_user_id INTEGER)')
    res = c.execute('SELECT days,time_start,categories from info').fetchall()
    
    if len(res) > 0:
        res = res[0]
    else:
        return None
        
    days = res[0].split(',')
    start_time = res[1]
    categories = res[2].split(',')
    first_class_date = get_first_class_date(date,days)
    next_class_date = get_next_class_date(date,days)
    time_split = start_time.split(':')
    first_class_date = first_class_date.replace(hour=int(time_split[0]),minute=int(time_split[1]))
    next_class_date = next_class_date.replace(hour=int(time_split[0]),minute=int(time_split[1]))
    full_c_datetime_string = str(first_class_date)
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    averages = {c:[] for c in categories}
    
    for entry in res:
        info = {}
        info['date'] = entry[0]
        info['time'] = entry[1]
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        scores = {}
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]] = int(split_parts[1])
            averages[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)
    averages = {c:sum(averages[c])/float(len(averages[c])) for c in averages}
        
    return (reviews,averages)




def get_month_reviews(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING,code STRING)')
    c.execute('CREATE TABLE IF NOT EXISTS reviews(date STRING, time STRING, scores STRING, comments STRING, class_user_id INTEGER)')
    res = c.execute('SELECT days,time_start,categories from info').fetchall()
    
    if len(res) > 0:
        res = res[0]
    else:
        return None
        
    days = res[0].split(',')
    start_time = res[1]
    categories = res[2].split(',')
    next_class_date = get_next_class_date(date,days)
    time_split = start_time.split(':')
    next_class_date = next_class_date.replace(hour=int(time_split[0]),minute=int(time_split[1]))
    full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M')).replace(day=1)
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    averages = {c:[] for c in categories}
    
    for entry in res:
        info = {}
        info['date'] = entry[0]
        info['time'] = entry[1]
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        scores = {}
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]] = int(split_parts[1])
            averages[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)

    averages = {c:sum(averages[c])/float(len(averages[c])) for c in averages}
    return (reviews,averages)
'''


