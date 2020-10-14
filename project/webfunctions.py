import time
import datetime
from . import db
#from models import db
#from models import Submission
#from .models import Submission


#we need to do this with all of the emails
def convert_to_lowercase(mystring):
    return mystring.lower()
    
def all_same(mylist):
    allsame=True
    if len(mylist)==0:
        return True
    else:
        for x in mylist:
            if x!=x[0]:
                return False
        return True
        
def unixtime():
    return int(time.time())

def date(unixtime, format = '%m/%d/%Y %H:%M'):
    d = datetime.datetime.fromtimestamp(unixtime)
    return d.strftime(format)

def time_difference(timestamp2,timestamp1):
    """
    t1 = timestamps[1]
    t2 = timestamps[2]
    time_difference(t2,t1)
    """
    t1 = datetime.datetime.fromtimestamp(timestamp1)
    t2 = datetime.datetime.fromtimestamp(timestamp2)
    delta = t2-t1
    return delta.days
    
def is_valid_score(score):
    if type(score)==int and score >= 0 and score <=10:
        return True
    else:
        return False

def current_is_reviewer(sub):
    reviewers=get_reviewers(sub)
    if reviewers.count(current_user.email)>0:
        return True
    else:
        return False

def send_confirmation_email(subs):
    emails = [sub.email for sub in subs]
    if not all_same(emails):
        raise ValueError('not all of the emails are the same')
    else:
        email = {}
        email['receiver'] = emails[0]
        email['subject'] = "New Submissions Processed"
        message = f"""
        This is an automated email: <br> <br>
        
       {date(sub[0].timestamp)}: the following problems have been placed in the waiting room: <br> <br>
        """
        for sub in subs:
            message_part = f"""
            {sub.submission_number}: assignment {sub.assignment}, problem {sub.problem} <br>
            """
            message=message+message_part
            
        message = message + "<br> <br> The matching algorithm runs every midnight."
        email['message']=message
        result = {}
        result['message']=send_basic_email(email)
        return result
        
#
# GENERAL DICTIONARY BASED METHODS
#
#
    
def get_submission(content, by_email=False):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    submission_number=content['submission_number']
    
    if by_email==True:
        email=content['email']
        assignment=content['assignment']
        problem=content['problem']
        subs = db.session.query(Submission).filter(and_(Submission.email==email,
        Submission.coursename==coursename,
        Submission.year==year,
        Submission.term==term,
        Submission.assignment==assignment,
        Submission.problem==problem)).first()
    else:
        subs = db.session.query(Submission).filter(and_(Submission.submission_number==submission_number,
        Submission.coursename==coursename,
        Submission.year==year,
        Submission.term==term)).first()

    return subs
    
def is_valid_problem(content):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email=content['email']
    assignment=content['assignment']
    problem=content['problem']
    #file=content['file']
    probs = db.session.query(Problem).filter(and_(Problem.coursename==couresname,
    Problem.year==year,
    Problem.term==term,
    Problem.assignment==assignment,
    Problem.problem==problem)).all()
    if len(probs)==1:
        return True
    else:
        return False
        

def get_submissions(content):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email=content['email']
    assignment=content['assignment']
    problem=content['problem']
    #file=content['file']
    subs = db.query(Submission).filter(and_(Submission.email==email,
    Submission.coursename==coursename,
    Submission.year==year,
    Submission.term==term,
    Submission.assignment==assignment,
    Submission.problem==problem)).all()
    return subs

def get_reviewersc(content):
    #assumes valid content
    sub=get_submissions(content)[0]
    return [sub.reviewer1,sub.reviewer2]
