import requests

def login(id, password):
    LOGIN_URL = 'https://dgist.blackboard.com/?new_loc=%2Fultra%2Fcourse'

    session = requests.Session()

    login_data = {
        'username' : id,
        'password' : password
    }
    response = session.post(LOGIN_URL, data = login_data)

    if response.status_code == 200:
        print('로그인 성공')
    else:
        return 'error'

    CRAWLING_URL = 'https://lms.dgist.ac.kr/ultra/course'
    response = session.get(CRAWLING_URL)

    return response.content