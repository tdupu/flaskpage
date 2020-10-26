
import sys, os
sys.path.append('./..')
sys.path.append(["/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/flaskpage","/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/flaskpage/project"])

#without adding data to the database queries will not work.
#os.remove('/Users/taylordupuy/Documents/web-development/dev/flaskpage/project/db.sqlite')


############################
from werkzeug.security import generate_password_hash, check_password_hash

sys.path.append('/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/flaskpage/project/excel_tools')
sys.path.append('/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/flaskpage/project/email_tools')

from table_editor import SheetObject

R=SheetObject('/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/data/algebra-one/20/f/roster.xlsx','roster')
S=SheetObject('/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/data/algebra-one/20/f/roster.xlsx','submissions')
A=SheetObject('/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/data/algebra-one/20/f/roster.xlsx','assignments')
P=SheetObject('/users/t/d/tdupuy/test.tdupuy.w3.uvm.edu-root/data/algebra-one/20/f/roster-test.xlsx','assignments')

from database_declarative import User, Submission, Problem, Course, Base
#from models import db
#from models import User, Submission, Problem, Course
from sqlalchemy import create_engine
import numpy as np
from email_functions import *
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///../data/db.sqlite')
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

def is_reviewed(s):
    return s.review1_timestamp>-1 and s.review2_timestamp>-1

def is_complete(s):
    if is_reviewed(s):
        a=s.assignment
        p=s.problem
        r1 = s.reviewer1
        r2 = s.reviewer2
        subs = session.query(Submission).filter( and_(or_(Submission.netid==r1,Submission.netid==r2),Submission.assignment ==a,Submission.problem ==p))
        if is_reviewed(subs[0]) and is_reviewed(subs[1]):
            return True
        else:
            return False
    else:
        return False
    
def is_matched(s):
    if s.reviewer1_assignment_time>-1 and s.reviewer2_assignment_time>-1:
        return True
    else:
        return False
    
def get_grade(user,ass):
    """
    get_grade('yshi9',1)
    7.875473484848484
    """
    subs=session.query(Submission).filter( and_(Submission.netid==user, Submission.assignment==ass))
    subs = sorted(subs, key=lambda s: s.total_score2)
    return np.mean([s.total_score2 for s in subs[0:2]])

def get_email(netid):
    user=session.query(User).filter(User.netid==netid).first()
    return user.email

def strdate_to_int(s):
    time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y").timetuple())
    
def string_to_timestamp(date_str, format_str='%m/%d/%Y'):
    datetime_obj = datetime.datetime.strptime(date_str, format_str)
    return datetime_obj.timestamp()
    
Base.metadata.create_all(engine)

# Insert an Address in the address table
algebra = Course(
    coursename = 'algebra-one',
    year=20,
    term = 'f', #F=Fall, S=Spring, U=Summer,
    coursenumber = 'Math 251', #used to be class
    uvm_course = 1,
    zulipurl = 'https://uvm-mathematics.zulipchat.com',
    zuliprc = '',
    homepage = 'https://www.uvm.edu/~tdupuy/',
    size = 36
)
session.add(algebra)
session.commit()

# Insert an Address in the address table
algebraic_topology = Course(
    coursename = 'algebraic-topology',
    year=20,
    term = 'f', #F=Fall, S=Spring, U=Summer,
    coursenumber = 'Math 354', #used to be class
    uvm_course = 1,
    zulipurl = 'https://uvm-mathematics.zulipchat.com',
    zuliprc = '',
    homepage = 'https://www.uvm.edu/~tdupuy/',
    size = 9
)
session.add(algebraic_topology)
session.commit()

"""
from sqlalchemy.ext.declarative import DeclarativeMeta

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
    """

algebra=session.query(Course).filter(and_(
    Course.coursename == 'algebra-one',
    Course.year==2020,
    Course.term == 'f')
).first()

topology=session.query(Course).filter(and_(
    Course.coursename == 'algebraic-topology',
    Course.year==20,
    Course.term == 'f')
).first()

myproblems = A.get({})

for x in myproblems:
    new_problem = Problem(
    coursename = 'algebra-one', #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = 2020,
    term = 'f', #f=Fall, s=Spring, u=Summer
    assignment = x['assignment'],
    problem = x['problem'],
    #references = x['']
    datasets={'subs':[],
                  'waiting':[],
                  'matched':[],
                  'reviewed':[],
                  'completed':[],
                  'scores':[],
                  'rt':[],
                  'mt':[]}
    )
    session.add(new_problem)

session.commit()

for p in session.query(Problem).all():
    #print(p)
    results=P.get({"assignment":int(p.assignment),"problem":int(p.problem)})
    print(results)
    if len(results)==1:
        #print(results[0])
        result = results[0]
        p.description=result['description']
        p.hints=result['comment']
        if result['due_date']==None:
            pass
        else:
            p.due_date=result['due_date'].timestamp()
        #print(p.due_date)
        p.course=algebra
        #print(p.course) this seems to be storing things properly
session.commit()


#session.rollback()
myusers = R.get({})

# Insert a Person in the person table
for x in myusers:
    new_person = User(
        name = x['name'],
        pronoun=x['pronoun'],
        uvm_student=1,
        student_id = x['student_id'],
        courses = 'algebra-one/f/20',
        major = x['major'],
        degree = x['degree'],
        credits = x['credits'],
        reg_status = x['reg_status'],
        reg_data = x['reg_data'],
        email = x['email'].lower(),
        netid = x['netid'],
        password = generate_password_hash(x['password'],method='sha256'),
        config={'courses':[{'id':algebra.id,'group':'user'}],'emails':[],'super_user':0})
    session.add(new_person)

session.commit()


mysubs = S.get({})
for x in mysubs:
    new_sub = Submission(
        coursename = 'algebra-one',
        year = '2020',
        term = 'f',
        submission_number = x['submission_number'],
        submission_locked = x['submission_locked'],
        netid = x['netid'],
        email = get_email(x['netid']),
        assignment = x['assignment'],
        problem = x['problem'],
        closed = x['closed'],
        submission_time = x['submission_time'],
        total_score1 = x['total_score1'],
        total_score2 = x['total_score2'],
        reviewer1_assignment_time =x['reviewer1_assignment_time'],
        reviewer1 = x['reviewer1'],
        reviewer1_email = '',
        reviewer1_score = x['reviewer1_score'],
        review1 = x['review1'],
        review1_timestamp = x['review1_timestamp'],
        review1_locked = x['review1_locked'],
        #bad1, bad2
        reviewer2_assignment_time =x['reviewer2_assignment_time'],
        reviewer2 = x['reviewer2'],
        reviewer2_email = '',
        reviewer2_score = x['reviewer2_score'],
        review2 = x['review2'],
        review2_timestamp = x['review2_timestamp'],
        review2_locked = x['review2_locked'],
        new_submission = x['new_submission'],
        new_match = x['new_match'],
        new_review1 = x['new_review1'],
        new_review2 = x['new_review2'],
        new_completion = x['new_completion'])
    session.add(new_sub)

session.commit()

#need to correct the submissions
for s in session.query(Submission).all():
    prob=session.query(Problem).filter(and_(
        Problem.coursename==s.coursename,
        Problem.problem==s.problem,
        Problem.assignment==s.assignment)).first()
    course=session.query(Course).filter(
        Course.coursename==s.coursename).first()
    user=session.query(User).filter(User.netid==s.netid).first()
    s.prob=prob
    s.course=course
    s.user=user
session.commit()
