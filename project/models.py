from statistics import *
from decimal import Decimal
import numpy as np
import datetime
import time

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

#from . import db
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship

from .webfunctions import *
#from .dbfunctions import *

"""
https://danidee10.github.io/2016/09/19/flask-by-example-2.html

We should add this line:
    db = SQLAlchemy()

then in the other places we should add:
    from model import db
"""

db=SQLAlchemy()

class User(UserMixin,db.Model):
#class User(db.Model):
    __tablename__ = 'users'
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
    config = db.Column(db.JSON)
    """
          {'courses':[{'id':algebra.id,'group':'user'}],
             'emails':[],
             'super_user':0
            }
    """
    submissions=db.relationship('Submission',backref='user')
    
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
    #users=db.relationship('Users',back_populates='courses')
    #problems=db.relationship('Problem',back_populates='course')
    problems=db.relationship('Problem',backref='course')
    
    def get_size(self):
        try:
            return self.size
            
        except:
            #FIXME!!!
            #This needs to be put in at the initialization
            return 36
    
    
    def html(self):
        return f"{coursename_long(self.coursename)}, {term_long(self.term)} {year_long(self.year)}"
        
    def url(self):
    
        return f"/{self.coursename}/{year_long(self.year)}/{self.term}"
        
    def html(self):
        return f"{coursename_long(self.coursename)}, {term_long(self.term)} {year_long(self.year)}"
        
    def get_problems(self):
        problems = db.session.query(Problem).filter(
        and_(Problem.coursename==self.coursename,
        Problem.year==year_long(self.year),
        Problem.term==self.term)).all()
        return problems
        
    def get_assignments(self):
        problems = self.get_problems()
        a = {}
        for p in problems:
            if list(a.keys()).count(p.assignment)==0:
                a[p.assignment]={}
                a[p.assignment]["problems"] = [p]
                a[p.assignment]["due_date"] = p.due_date
            else:
                a[p.assignment]["problems"].append(p)
        return a
        

class Problem(db.Model):
    __tablename__ = 'problems'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    coursename = db.Column(db.String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = db.Column(db.Integer)
    term = db.Column(db.String(250)) #F=Fall, S=Spring, U=Summer
    assignment = db.Column(db.String(250))
    problem = db.Column(db.String(250))
    references = db.Column(db.JSON)
    due_date = db.Column(db.Integer)
    hints = db.Column(db.String(1000))
    locked = db.Column(db.Integer)
    datasets = db.Column(db.JSON)
    description = db.Column(db.String(1000))
    """
    self.datasets['subs']=
    self.datasets['waiting']
    self.datasets['matched']
    self.datasets['reviewed']
    self.datasets['completed']=[m.id for m in scored2]
    self.datasets['score'] = [m.total_score2 for m in scored2]
    tt=self._get_time_data(scored2)
    self.datasets['rt'] = tt['rt']
    self.datasets['mt'] = tt['rt']
    """
    #submissions=db.relationship('Submission',back_populates='prob')
    #course_id=db.Column(db.Integer,db.ForeignKey('Course.id'))
    #course=db.relationship('Course',back_populates='problems')
    submissions=db.relationship('Submission',backref='prob')
    course_id=db.Column(db.Integer,db.ForeignKey('courses.id'))
    
    def get_data(self,key):
        """
        completion time
        """
        return self.datasets["key"]
        
    def append_data(self,x):
        self.datasets[key].append(x)
        
    def get_references(self,key):
        return self.references[key]
        
    def get_submissions(self):
        #this is stupid
        subs=db.session.query(Submission).filter(and_(
        Submission.coursename==self.coursename,
        Submission.year==self.year,
        Submission.term==self.term,
        Submission.assignment==self.assignment,
        Submission.problem==self.problem)).all()
        return subs
        
    def get_matched(self):
        return db.session.query(Submission).filter(
        and_(
        Submission.coursename==self.coursename,
        Submission.year==self.year,
        Submission.term==self.term,
        Submission.assignment==self.assignment,
        Submission.problem==self.problem,
        Submission.submission_locked==1
        )).all()
    
    
    def get_reviewed(self):
        subs = self.get_matched(self)
        reviewed = []
        for s in subs:
            if s.is_reviewed():
                reviewed.append(s)
        return reviewed

        return db.session.query(Submission).filter(and_(
        Submission.coursename==self.coursename,
        Submission.year==self.year,
        Submission.term==self.term,
        Submission.assignment==self.assignment,
        Submission.problem==self.problem,
        Submission.submission_locked==1,
        Submission.review2_timestamp>-1,
        Submission.review2_timestamp>-1)).all()
        
    def score1(self,subs_to_update=None):
        if subs_to_update==None:
            subs_to_update=self.get_reviewed()
        for s in subs_to_update:
            s.score1()
        
        result={'success':1, 'message':'total_score1 values have been updated'}
        return result
        
    def get_course(self):
        return db.session.query(Course).filter(
        and_(
        Course.coursename==self.coursename,
        Course.year==(self.year-2000),
        Course.term==self.term
        )).first()
        
    def num_submitted(self):
        return len(self.get_submissions())
        
    def num_available(self):
        return self.get_course().get_size() - self.num_submitted()
        
    def num_waiting(self):
        return len(self.datasets['waiting'])
        
    def num_matched(self):
        return len(self.datasets['matched'])
        
    def num_completed(self):
        return len(self.datasets['completed'])
        
    def mean_match_time(self):
        return self.make_stats()['mean_mt']
        
    def mean_review_time(self):
        return self.make_stats()['mean_rt']
        
    def mean_score(self):
        return self.make_stats()['mean']
        
    def median_score(self):
        return self.make_stats()['med']
        
    def std(self):
        return self.make_stats()['std']
    
    def url(self):
        return f"/{p.coursename}/{p.year}/{p.term}/hw{p.assignment}"
        
    def histogram(key,user=None):
        """
        tm
        tr
        tc
        score2
        """
        #<img src="/plot.png" "my plot">
        import io
        from flask import Response
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        import matplotlib.pyplot as plt
        data = self.datasets[key]
        n=len(data)
        plt.hist(data, bins=7)  # arguments are passed to np.histogram
        plt.title(f"{key}: assignment {self.assignment}, problem {self.problem} (n={n})")
        fig=plt.figure()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    
    def _get_time_data(self,subs):
        """
        submissions need to be complete
        """
        matching_times=[]
        review_times=[]
        for m in subs:
            t0 = m.submission_time
            t1 = m.reviewer1_assignment_time
            t2 = m.reviewer2_assignment_time
            t11 = m.review1_timestamp
            t22 = m.review2_timestamp
            tmatch = time_difference(max(t1,t2),t0)
            treview1 = time_difference(t11,t1)
            treview2 = time_difference(t22,t2)
            matching_times.append(tmatch)
            review_times.append(treview1)
            review_times.append(treview2)
        return {"rt":review_times,"mt":matching_times}
       
    def make_stats(self):
        stats={}
        d = self.datasets
        scores=d['scores']
        n = len(scores)
        if len(scores)>0:
            stats['mean']=mean(scores)
            stats['median']=median(scores)
            if len(scores)>1:
                stats['std']=stdev(scores)
            else:
                stats['std']=0
            stats['mean_rt']=mean(d['rt']) #review times
            stats['mean_mt']=mean(d['mt']) #matching times
        else:
            stats['mean']=0
            stats['med']=0
            stats['std']=0
            stats['mean_rt']=0
            stats['mean_mt']=0
        return stats
    
    def make_scored2(self,scored1=None,subs_to_update=None):
    
        try:
            if scored1==None:
                scored1=self.get_scored1()
            if subs_to_update==None:
                subs_to_update=self.get_scored1()
                
            scored2=[]
            for m in subs_to_update:
                reviewers=m.get_reviewers()
                reviewer1 =reviewers[0]
                reviewer2 =reviewers[1]
                s1 = m.reviewer1_score
                s2 = m.reviewer2_score
                search1 = []
                search2 = []
                for s in scored1:
                    if s.netid==reviewer1:
                        search1.append(n)
                    if s.netid==reviewer2:
                        search2.append(n)
                        
                if len(search1)>1 and len(search2)>1:
                    sub1=search1[0]
                    sub2=search2[0]
                    r1=sub1.total_score1
                    r2=sub2.total_score1
                    w1=float(r1/(r1+r2))
                    w2=float(r2/(r1+r2))
                    ts2=w1*s1+w2+s2
                    m.total_score2=ts2
                    scored2.append(m)
                    
            db.session.commit()
            
            result = {'success':1, 'message':"It worked!", 'completed':scored2}
            
        except Exception as e:
            session.rollback()
            result={'success':0, 'message':e}
        
        return result
    
    def make_clean_data(self):
        """
        INPUT: a problem class
        OUTPUT: prints to JSON
           --d['subs'] submission_ids
           --d['waiting'] submission_ids in waiting
           --d['matched'] submission_ids matched
           --d['ts']
           --
        """
        try:
            subs = self.get_submissions()
            waiting = []
            for sub in subs:
                if sub.submission_locked==0:
                    waiting.append(sub)
            matched = self.get_matched()
            scored1=[]
            for m in matched:
                if m.is_reviewed():
                    m.scored1()
                    scored1.append(m)
            scored2 = self.make_scored2(
            scored1=scored1,
            subs_to_update=scored1)['completed']
            
            
            self.datasets['subs']=[m.id for m in subs]
            self.datasets['waiting'] = [m.id for m in waiting]
            self.datasets['matched']=[m.id for m in matched]
            self.datasets['reviewed']=[m.id for m in scored1]
            self.datasets['completed']=[m.id for m in scored2]
            self.datasets['scores'] = [m.total_score2 for m in scored2]
            tt=self._get_time_data(scored2)
            self.datasets['rt'] = tt['rt']
            self.datasets['mt'] = tt['rt']
            result={'success':1,'message':f'the datasets for {self.assignment} problem {self.problem} have been updated'}
            return result
        except Exception as e:
            db.session.rollback()
            return {'success':0, 'error':e}
        
            
        

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
    w1 = db.Column(db.Float)
    w2 = db.Column(db.Float)
    #user_id = db.Column(db.Integer,db.ForeignKey('roster.id'))
    #user = db.relationship('User',back_populates='submissions')
    #prob_id = db.Column(db.Integer,db.ForeignKey('problems.id'))
    #prob = db.relationship('Problem',back_populates='submissions')
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    #user = relationship('User',back_populates='submissions')
    prob_id = db.Column(db.Integer,db.ForeignKey('problems.id'))
    
    #reviewer_submission_id = Column(Integer, ForeignKey('submissions.id')
    #reviewer_submission=relationship(
    #"Submission")
    #lazy="joined",
    #join_depth=2)
    
    
    def is_matched(self):
        if self.reviewer1_assignment_time>-1 and self.reviewer2_assignment_time>-1:
            return True
        else:
            return False

    def is_reviewed(self):
        return self.review1_timestamp>-1 and self.review2_timestamp>-1
        
    def make_score1(self):
        result = {"success":1,"message":'score1 has been updated'}
        if self.is_reviewed():
            self.score1 = (self.reviewer1_score + self.reviewer2_score)/2
            return result
        else:
            result["success"]=0
            result["message"]="score1 not updated. This submission does not have two reviews"
            return result
            
    def get_reviewer_subs(self):
        reviewers=self.get_reviewers()
        reviewer1 = reviewers[0]
        reviewer2 = reviewers[1]
        
        return db.session.query(Problem).filter(and_(
        Problem.coursename==self.coursename,
        Problem.year==self.year,
        Problem.term==self.term,
        Problem.assignment==self.assignment,
        Problem.problem==self.problem,
        or_(Problem.netid==reviewer1.netid,
            Problem.netid==reviewer2.netid)
        )).all()
            
    def get_problem(self):
        return db.session.query(Problem).filter(and_(
        Problem.coursename==self.coursename,
        Problem.year==self.year,
        Problem.term==self.term,
        Problem.assignment==self.assignment,
        Problem.problem==self.problem
        )).first()
        
        
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
    
    def path_to_upload(self):
        return self.path_to_data()+"upload/"
        
    def path_to_data(self):
        return f'../data/{self.coursename}/{self.year}/{self.term}/'
        
    def filename(self):
        return f'{self.coursename}-{self.assignment}-{self.problem}-{self.submission_number}'

db.create_all()

##########################
##########################
##########################
