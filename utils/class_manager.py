from sqlite3 import connect
import datetime

def get_new_class_id():
    db = connect('Data/general.db')
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS class_ids(id INTEGER)')
    res = c.execute('SELECT MAX(id) from class_ids').fetchall()[0][0]
    if res == None:
        return 0
    return res+1


def update_class_ids(new_id):
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
    db = connect('Data/%d.db' % (new_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING)')
    c.execute('INSERT INTO info VALUES(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"\")' % (class_name,instructor_name,days,time_start,time_end))
    db.commit()    
    db.close()
    update_class_ids(new_id)


def add_review_category(class_id,category):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    res = c.execute('SELECT categories from info').fetchall()[0][0]
    if res == '':
        new_categories = category
    else:
        new_categories = res + ',%s' % (category)
    c.execute('UPDATE info SET categories=\"%s\" WHERE categories==\"%s\"' % (new_categories,res))
    db.commit()
    db.close()


def delete_review_category(class_id,category):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    res = c.execute('SELECT categories from info').fetchall()[0][0]
    category_list = res.split(',')
    new_categories = ','.join(c for c in category_list if str(c) != category)
    c.execute('UPDATE info SET categories=\"%s\" WHERE categories==\"%s\"' % (new_categories,res))
    db.commit()
    db.close()


def add_user_to_class(class_id,user_id):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students(user_id INTEGER, class_user_id)')
    res = c.execute('SELECT MAX(class_user_id) from students').fetchall()[0][0]
    if res == None:
        c.execute('INSERT INTO students VALUES(%d,%d)' % (user_id,0))
    else:
        c.execute('INSERT INTO students VALUES(%d,%d)' % (user_id,res+1))
    db.commit()
    db.close()
    
def get_class_user_id(class_id,user_id):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students(user_id INTEGER, class_user_id)')
    res = c.execute('SELECT class_user_id from students WHERE user_id==%d' % (user_id)).fetchall()
    db.close()
    if len(res) == 0:
        return None
    return res[0][0]
    
#assuming scores is dictionary
def add_review(class_id,scores,comments,user_id):
    db = connect('Data/%s.db' % (class_id))
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
    
    
#not really needed, could just simply call get_reviews and use the scores key to find averages from there
#assuming date is is yyyy-mm-dd format
def get_review_averages(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING)')
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
    scores = {c:[] for c in categories}
    full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M'))
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT scores from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None
    
    for entry in res:
        scores_entry = entry[0].split(',')
        for e in scores_entry:
            info_split = e.split(':')
            scores[info_split[0]].append(int(info_split[1]))

    scores = {c:sum(scores[c])/float(len(scores[c])) for c in scores}
    return scores

def get_reviews(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING)')
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
    scores = {c:[] for c in categories}
    full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M'))
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    
    for entry in res:
        info = {}
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)

    return reviews

def get_week_reviews(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING)')
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
    scores = {c:[] for c in categories}
    full_c_datetime_string = str(first_class_date)
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    
    for entry in res:
        info = {}
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)

    return reviews




def get_month_reviews(class_id,date):
    db = connect('Data/%s.db' % (class_id))
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS info(class_name STRING, instructor_name STRING, days STRING, time_start STRING, time_end STRING,categories STRING)')
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
    scores = {c:[] for c in categories}
    full_c_datetime_string = str(datetime.datetime.strptime('%s %s' % (date,start_time),'%Y-%m-%d %H:%M')).replace(day=1)
    full_n_datetime_string = str(next_class_date)
    res = c.execute('SELECT * from reviews WHERE date || \" \" || time >= \"%s\" AND date || \" \" || time < \"%s\"' % (full_c_datetime_string,full_n_datetime_string)).fetchall()

    if len(res) == 0:
        return None

    reviews = []
    
    for entry in res:
        info = {}
        info['user'] = entry[4]
        info['comments'] = entry[3]
        score_list = entry[2].split(',')
        for score in score_list:
            split_parts = score.split(':')
            scores[split_parts[0]].append(int(split_parts[1]))
        info['scores'] = scores
        reviews.append(info)

    return reviews


'''
create_class('sample','me',['M','W','F'],'10:00','10:53')
add_review_category(0,'volume')
add_review_category(0,'relevance')
add_review_category(0,'clarity')
delete_review_category(0,'relevance')


add_user_to_class(0,123)
add_user_to_class(0,345)
add_user_to_class(0,666)

add_review(0,{'volume':3,'clarity':3},'hello',123)
add_review(0,{'volume':2,'clarity':3},'world',345)
add_review(0,{'volume':3,'clarity':1},'everyone',666)

'''
