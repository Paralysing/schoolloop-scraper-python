from bs4 import BeautifulSoup
import requests
import re

class SchoolLoopScraper:
    def __init__(self, username, password, schoolloop_domain='montavista.schoolloop.com'):
        self.schoolloop_domain = schoolloop_domain
        self.username = username
        self.password = password

    def extract_schoolloop_info(self):
        grade_data = {}
        assignment_data = {}
        schoolloop_session = requests.Session()
        r1 = schoolloop_session.get('https://' + self.schoolloop_domain + '/portal/guest_home?d=x', timeout=10)
        s1 = BeautifulSoup(r1.text, 'lxml')
        form_data_id = s1.find('input', {'id' : 'form_data_id'})['value']
        cookie = {
            'JSESSIONID': r1.cookies['JSESSIONID'],
            'slid': r1.cookies['slid']
        }
        payload = {
            'login_name': self.username,
            'password': self.password,
            'event_override': 'login',
            'form_data_id': form_data_id
        }
        r2 = schoolloop_session.post('https://' + self.schoolloop_domain + '/portal/guest_home?etarget=login_form', cookies=cookie, data=payload, timeout=10)
        s2 = BeautifulSoup(r2.text, 'lxml')
        for row in s2.find_all('table', {'class' : 'student_row'}):
            try:
                grade = float(row.find('div', {'class': 'percent'}).text.replace('%', ''))
            except AttributeError:
                grade = 'N/A'
            grade_str = str(grade)
            period = str(row.find('td', {'class': 'course'}).a.text)
            grade_data[period] = grade_str
        for row in s2.find_all('table', {'class' : 'table_basic'}):
            assignment = {}
            assignment['title'] = row.find('td', {'class': 'item_title'}).find('span').text.strip()
            assignment['title'] = re.sub(r'[^\x00-\x7f]',r'', assignment['title'])
            course = row.find('td', {'style': 'width: 140px;'}).text.strip()
            assignment['date'] = row.find('td', {'style': 'width: 70px;'}).text.replace('Due:', '').strip()
            assignment['date'] = re.sub(r'[^\x00-\x7f]',r'', assignment['date'])
            if course not in assignment_data:
                assignment_data[course] = []
            assignment_data[course].append(assignment)
        r3 = schoolloop_session.get('https://' + self.schoolloop_domain + '/portal/endSession', timeout=10)
        return {
            'grades': grade_data,
            'assignments': assignment_data
        }
