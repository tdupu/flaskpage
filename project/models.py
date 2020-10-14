from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from . import db
from sqlalchemy import or_, and_
from .webfunctions import *
import datetime
import time

"""
https://danidee10.github.io/2016/09/19/flask-by-example-2.html

We should add this line:
    db = SQLAlchemy()

then in the other places we should add:
    from model import db
"""


def date_to_unit(s):
    return time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y").timetuple())

def term_long(x):
    if x=='f':
           return "Fall"
    elif x=='s':
        return "Spring"
    elif x=='u':
        return "Summer"
    else:
        return x
           
def year_long(x):
    return "20"+str(x)
       
def coursename_long(x):
    if x=='algebra-one':
        return "Algebra I"
    elif x=='algebraic-topology':
        return "Algebraic Topology"
    else:
        return x
           
def course_html(s):
    return f"{coursename_long(s.coursename)}, {term_long(s.term)} {year_long(s.year)}"
    
    
def has_first_reviews(sub):
    if sub.reviewer1_score>-1 and sub.reviewer2_score>-1:
        return True
    else:
        return False
        
def get_missing_reviewers(sub):
    late_reviewers = []
    if sub.reviewer1_score==-1:
        late_reviewers.append(sub.reviewer1)
    if sub.reviwer2_score==-1:
        late_reviewers.append(sub.reviewer2)
    return late_reviewers
    
def get_late_reviewers(sub):
    reviewers = get_missing_reviewers(sub)
    now = int(time.time())
    then = sub.timestamp
    result = {}
    if time_difference(now,then)>7:
        late_reviewers = get_missing_reviewers(sub)
        return late_reviewers
    else:
        return []
   
def notify_late_reviewers(sub):
    email={}
    email['message']=f"""
    You have be poked by the author of submission {sub.submission_number}.
    """
    email['subject']="Review for {sub.submission_number}."
    late_reviewers=get_late_reviewers(sub)
    for r in late_reviewers:
        email['receiver']=r
        send_basic_email(email)
    
    result={}
    result['message']="reviewers have been poked"
    return result

"""
Where does the database get instantiated?

"""

class User(UserMixin,db.Model):
#class User(db.Model):
    __tablename__ = 'roster'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    pronoun=db.Column(db.String(250))
    uvm_student=db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    courses = db.Column(db.String(1000))
    major = db.Column(db.String(250))
    degree = db.Column(db.String(250))
    credits = db.Column(db.Integer)
    reg_status = db.Column(db.String(250))
    reg_data = db.Column(db.String(250))
    email = db.Column(db.String(250))
    netid = db.Column(db.String(250))
    password = db.Column(db.String(250))
    participation = db.Column(db.JSON)
    grades = db.Column(db.JSON)
    
    def get_grade(self,ass):
        """
        get_grade('yshi9',1)
        7.875473484848484
        """
        from . import db
        import numpy as np
        subs=db.session.query(Submission).filter( and_(Submission.netid==user, Submission.assignment==ass, Submission.closed==1))
        subs = sorted(subs, key=lambda s: s.total_score2)
        return np.mean([s.total_score2 for s in subs[0:2]])
        
    def is_reviewer(self, sub):
        reviewers=sub.get_reviewers()
        if reviewers.count(current_user.email)>0:
            return True
        else:
            return False
    
class Course(db.Model):
    __tablename__ = 'courses'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    coursename = db.Column(db.String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = db.Column(db.Integer)
    term = db.Column(db.String(250)) #F=Fall, S=Spring, U=Summer
    coursenumber = db.Column(db.String(250))
    uvm_course = db.Column(db.Integer)
    zulipurl = db.Column(db.String(250))
    zuliprc = db.Column(db.String(250))
    homepage = db.Column(db.String(250))
    size = db.Column(db.Integer)
    
    def html(self):
        return f"{coursename_long(self.coursename)}, {term_long(self.term)} {year_long(self.year)}"
        
    def url(self):
        return f'{self.coursename}/{self.year -2000}/{self.term}'
    
            

class Problem(db.Model):
    __tablename__ = 'assignments'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = db.Column(db.Integer)
    term = db.Column(db.String(250)) #F=Fall, S=Spring, U=Summer
    assignment = db.Column(db.String(250))
    problem = db.Column(db.String(250))
    references = db.Column(db.JSON)
    """
    
    """
    due_date = db.Column(db.Date)
    hints = db.Column(db.String(1000))
    locked = db.Column(db.Integer)
    datasets = db.Column(db.JSON)
    """
    num_c
    num_m
    mt --- matchtime
    rt --- review time
    score2 ---
    ct --- completion time
    """
    
    def get_data(self,key):
        """
        completion time
        """
        return self.datasets["key"]
        
    def append_data(self,x):
        self.datasets[key].append(x)
        
    def get_references(self,key):
        return self.references[key]
        
    
        
    

class Submission(db.Model):
    __tablename__ = 'submissions'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    coursename = db.Column(db.String)
    year = db.Column(db.Integer)
    term = db.Column(db.Integer)
    submission_number = db.Column(db.Integer)
    submission_locked = db.Column(db.Integer)
    netid = db.Column(db.String(250))
    email = db.Column(db.String(250))
    assignment = db.Column(db.String(250))
    problem = db.Column(db.String(250))
    closed = db.Column(db.Integer)
    submission_time = db.Column(db.Integer)
    total_score1 = db.Column(db.Float)
    total_score2 = db.Column(db.Float)
    reviewer1_assignment_time =db.Column(db.Integer)
    reviewer1 = db.Column(db.String(250))
    reviewer1_email = db.Column(db.String(250))
    reviewer1_score = db.Column(db.Integer)
    review1 = db.Column(db.String(1000))
    review1_timestamp = db.Column(db.Integer)
    review1_locked = db.Column(db.Integer)
    reviewer2_assignment_time=db.Column(db.Integer)
    reviewer2 = db.Column(db.String(250))
    reviewer2_email = db.Column(db.String(250))
    reviewer2_score = db.Column(db.Integer)
    review2 = db.Column(db.String(1000))
    review2_timestamp = db.Column(db.Integer)
    review2_locked = db.Column(db.Integer)
    new_submission = db.Column(db.Integer)
    new_match = db.Column(db.Integer)
    new_review1 = db.Column(db.Integer)
    new_review2 = db.Column(db.Integer)
    new_completion = db.Column(db.Integer)
    bad1 = db.Column(db.Integer())
    bad2 = db.Column(db.Integer())
    data = db.Column(db.LargeBinary)
    

    
    def is_matched(self):
        if self.reviewer1_assignment_time>-1 and self.reviewer2_assignment_time>-1:
            return True
        else:
            return False

    def is_reviewed(self):
        return self.review1_timestamp>-1 and self.review2_timestamp>-1
        
    def is_submitter(self,user):
        return self.netid==user.netid
        
    def get_reviewers(self):
        return [self.reviewer1,self.reviewer2]
    
    def get_reviewer_index(self,user):
        if self.reviewer1_email==user.email:
            return 1
        elif self.reviewer2_email==user.email:
            return 2
        else:
            return 0
    
    def is_reviewer(self,user):
        reviewers = self.get_reviewers()
        return (reviewers.count(user.netid)>0)
        
    def needs_review(self,user):
        return (self.is_reviewer(user) and (not self.has_submitted_review(user)))
        
    def is_late(self,user):
        return (self.is_reviewer(user) and self.days_since_matched()>7)
        
    def is_overdue(self):
        return "not implemented"
        
    def can_poke(self):
        return ( (not self.is_reviewed()) and  (self.days_since_matched()>7))
        
    def days_since_matched(self):
        if self.reviewer1_assignment_time>=-1:
            return time_difference(unixtime(),self.reviewer1_assignment_time)
        else:
            return "NA"

    def is_complete(self):
        from . import db
        if self.is_reviewed():
            a=self.assignment
            p=self.problem
            r1 = self.reviewer1
            r2 = self.reviewer2
            subs = db.session.query(Submission).filter( and_(or_(Submission.netid==r1,Submission.netid==r2),Submission.assignment ==a,Submission.problem ==p))
            if subs[0].is_reviewed() and subs[1].is_reviewed():
                return True
            else:
                return False
        else:
            return False
            
    def days_since_submitted(self):
        return time_difference(unixtime(),self.timestamp)
         
    """
    def days_overdue(self):
        problem=db.session.query(Problem).filter(and_(
        Problem.assignment==self.assignment,
        Problem.problem==self.problem,
        Problem.coursename==self.coursename,
        Problem.year==self.year,
        Problem.term==self.term
        ).first()
        return time_difference(self.timestamp,date_to_unix(problem.duedate()))
        """
            
    def has_submitted_review(self,user):
        if self.reviewer1==user.netid and self.review1_timestamp>-1:
            return True
        elif self.reviewer2==user.netid and self.review2_timestamp>-1:
            return True
        else:
            return False
    
    def has_first_reviews(self):
        had_first_reviews(self)
            
    def get_missing_reviewers(self):
        get_missing_reviewers(self)
        
    def get_late_reviewers(self):
        get_late_reviewers(self)
       
    def notify_late_reviewers(sub):
        email={}
        email['message']=f"""
        You have be poked by the author of submission {sub.submission_number}.
        """
        email['subject']="Review for {sub.submission_number}."
        late_reviewers=get_late_reviewers(sub)
        for r in late_reviewers:
            email['receiver']=r
            send_basic_email(email)
        
        result={}
        result['message']="reviewers have been poked"
        return result
        
    def url(self):
        return f'{self.coursename}/{self.year -2000}/{self.term}/{self.submission_number}'
        


