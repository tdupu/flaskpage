import sys
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
from statistics import *
from decimal import Decimal


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

def get_date(unixtime, format_str='%m/%d/%Y'):
    return datetime.datetime.fromtimestamp(unixtime).strftime(format_str)
    
def strdate_to_int(s):
    time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y").timetuple())
    
def string_to_timestamp(date_str, format_str='%m/%d/%Y'):
    datetime_obj = datetime.datetime.strptime(date_str, format_str)
    return datetime_obj.timestamp()
    
def get_times(subs):
    """
    submissions need to be complete
    """
    matching_times=[]
    review_times=[]
    for m in subs:
        t0 = m['submission_time']
        t1 = m['reviewer1_assignment_time']
        t2 = m['reviewer2_assignment_time']
        t11 = m['review1_timestamp']
        t22 = m['review2_timestamp']
        tmatch = time_difference(max(t1,t2),t0)
        treview1 = time_difference(t11,t1)
        treview2 = time_difference(t22,t2)
        matching_times.append(tmatch)
        review_times.append(treview1)
        review_times.append(treview2)
    return {"review_times":review_times,"matching_times":matching_times}
    
def searchd(list_of_dicts,sdict):
    new_list = []
    keys=sdict.keys()
    for x in list_of_dicts:
        ok = 1
        for key in keys:
            if x[key]!=sdict[key]:
                ok=0
                break
        
        if ok==1:
            new_list.append(x)
    return new_list
    
def clean_dec(x):
    return format(x,'.3f')
    
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

"""
def current_is_reviewer(sub):
    reviewers=get_reviewers(sub)
    if reviewers.count(current_user.email)>0:
        return True
    else:
        return False
"""

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

def get_times(subs):
    """
    submissions need to be complete
    """
    matching_times=[]
    review_times=[]
    for m in subs:
        t0 = m['submission_time']
        t1 = m['reviewer1_assignment_time']
        t2 = m['reviewer2_assignment_time']
        t11 = m['review1_timestamp']
        t22 = m['review2_timestamp']
        tmatch = time_difference(max(t1,t2),t0)
        treview1 = time_difference(t11,t1)
        treview2 = time_difference(t22,t2)
        matching_times.append(tmatch)
        review_times.append(treview1)
        review_times.append(treview2)
    return {"review_times":review_times,"matching_times":matching_times}

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
           
def course_html(c):
    return f"{coursename_long(c.coursename)}, {term_long(c.term)} {year_long(c.year)}"
    
    
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
   
def poke_reviewers(sub):
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

def sort_subs_by_stage(subs,reviewer=False):
    cleandict={}
    matched = []
    cleandict['waiting']=[]
    cleandict['just_matched']=[]
    cleandict['first_reviews']=[]
    cleandict['completed']=[]
    
    #split into matched and unmatched
    if reviewer==False:
        for s in subs:
            if not s.is_matched():
                cleandict['waiting'].append(s)
            else:
                matched.append(s)
    if reviewer==True:
        matched=subs
    
    #collect ones with reviews
    for s in matched:
        if s.is_reviewed():
            cleandict['first_reviews'].append(s)
    
    #remove ones with removed from the matched
    #these are now in the matching stage but waiting
    #for first reviews
    for c in cleandict['first_reviews']:
        matched.remove(c)
    cleandict['just_matched']=matched
    
    #collect all of the completed ones
    for s in cleandict['first_reviews']:
        if s.is_complete():
            cleandict['completed'].append(s)
        
    #to complete remove the completed ones from the first_review list
    for c in cleandict['completed']:
        cleandict['first_reviews'].remove(c)
        
    output = {}
    output['waiting']=sorted(cleandict['waiting'],
    key=lambda c: [c.assignment,c.problem])
    output['just_matched']=sorted(cleandict['just_matched'],
       key=lambda c: [c.assignment,c.problem])
    output['first_reviews']=sorted(cleandict['first_reviews'],
       key=lambda c: [c.assignment,c.problem])
    output['completed']=sorted(cleandict['completed'],
       key=lambda c: [c.assignment,c.problem])
        
    return output

def sorted_user_submissions(content):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email = content['email']
    subs=db.query(Submission).filter(
    Submission.coursename==coursename,
    Submission.year==year,
    Submission.term==term,
    Submission.email==email).all()
    return sort_subs_by_stage(subs)

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
