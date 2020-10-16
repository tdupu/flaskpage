#from .models import db
#from .webfunctions import *

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
