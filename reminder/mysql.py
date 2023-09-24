import pymysql


hostname = "your db hostname here"
username = "your db username here"
password = "your db password here"
database = "your db name here"


def start():
    pass
def register(author, id, password, user_id):
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')

    cur = db.cursor()
        
    cur.execute(f"INSERT INTO user (name, lms_id, pw, user_id) VALUES ('{author}', '{id}', '{password}', '{user_id}') ON DUPLICATE KEY UPDATE lms_id = '{id}', pw = '{password}'")
    db.commit()
    db.close()

def assignment(author):
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')

    cur = db.cursor()
    
    cur.execute(f"SELECT id FROM user WHERE name = '{author}'")
    uid = cur.fetchall()
    
    cur.execute(f"SELECT id, subject, assignment_name, due, is_custom FROM assignment LEFT JOIN user_assignment ON assignment.id = user_assignment.aid WHERE uid = {uid[0][0]}")
    aid_tuple = cur.fetchall()
    print(aid_tuple)
    
    db.commit()
    db.close()
    return aid_tuple

def get_id_pw(author):
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')

    cur = db.cursor()
    
    cur.execute(f"SELECT lms_id, pw FROM user WHERE name = '{author}'")
    idpw = cur.fetchall()
    id = idpw[0][0]
    pw = idpw[0][1]
    print(id, pw)
    return id, pw
  
def refresh(author, assign_list):
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')
    
    cur = db.cursor()
    
    cur.execute(f"SELECT id FROM user WHERE name = '{author}'")
    print("done0")
    uid = cur.fetchall()[0][0]
    
    assignment_set = set()
    for i in range(len(assign_list)):
        print("done")
        cur.execute(f"INSERT INTO assignment (assignment_name, subject, due, is_custom) VALUES ('{assign_list[i]['homework']}', '{assign_list[i]['course']}', '{assign_list[i]['due']}', FALSE) ON DUPLICATE KEY UPDATE due = '{assign_list[i]['due']}'")
        print("done1")
        cur.execute(f"SELECT id from assignment WHERE assignment_name = '{assign_list[i]['homework']}' AND subject = '{assign_list[i]['course']}'")
        print("done2")
        assignment_set.add(cur.fetchall()[0][0])
    
    cur.execute(f"DELETE FROM user_assignment WHERE uid = '{uid}'")
    for aid in assignment_set:
        cur.execute(f"INSERT INTO user_assignment (uid, aid) VALUES ('{uid}', '{aid}')")
    
    db.commit()
    db.close()
    return uid, assignment_set

def custom_assignment(author, assign_list):
    try:
        db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')

        cur = db.cursor()
        
        cur.execute(f"SELECT id FROM user WHERE name = '{author}'")
        print("done0")
        uid = cur.fetchall()[0][0]
        
        assignment_set = set()
        for i in range(len(assign_list)):
            print("done")
            cur.execute(f"INSERT INTO assignment (assignment_name, subject, due, is_custom) VALUES ('{assign_list[i]['homework']}', '{assign_list[i]['course']}', '{assign_list[i]['due']}', TRUE) ON DUPLICATE KEY UPDATE due = '{assign_list[i]['due']}'")
            print("done1")
            cur.execute(f"SELECT id from assignment WHERE assignment_name = '{assign_list[i]['homework']}' AND subject = '{assign_list[i]['course']}'")
            print("done2")
            assignment_set.add(cur.fetchall()[0][0])
            
        for aid in assignment_set:
            cur.execute(f"INSERT INTO user_assignment (uid, aid) VALUES ('{uid}', '{aid}')")
            
        db.commit()
        db.close()
        return None
    except Exception as e:
        return e
    

def delete_custom(author, aid):
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')

    cur = db.cursor()
    
    cur.execute(f"DELETE FROM user_assignment WHERE aid = {aid}")
    cur.execute(f"DELETE FROM assignment WHERE is_custom = 1 AND id = {aid}")
    
    db.commit()
    db.close()