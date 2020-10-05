from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db
from sqlalchemy import or_, and_

#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
from .models import Submission, Course


import sys
sys.path.append('/Users/taylordupuy/Documents/web-development/dev/email_tools')
from email_functions import *

#
# SOME AUXILLARY FUNCTIONS, MOVE LATER
#

def is_reviewed(s):
    return s.review1_timestamp>-1 and s.review2_timestamp>-1

def is_complete(s):
    if is_reviewed(s):
        a=s.assignment
        p=s.problem
        r1 = s.reviewer1
        r2 = s.reviewer2
        subs = db.session.query(Submission).filter( and_(or_(Submission.netid==r1,Submission.netid==r2),Submission.assignment ==a,Submission.problem ==p))
        if is_reviewed(subs[0]) and is_reviewed(subs[1]):
            return True
        else:
            return False
    else:
        return False
    
def get_grade(user,ass):
    """
    get_grade('yshi9',1)
    7.875473484848484
    """
    subs=db.session.query(Submission).filter( and_(Submission.netid==user, Submission.assignment==ass))
    subs = sorted(subs, key=lambda s: s.total_score2)
    return np.mean([s.total_score2 for s in subs[0:2]])
    
#
#
#

main = Blueprint('main', __name__)

@main.route('/')
def index():
    courses = db.session.query(Course).all()
    courses = sorted(courses, key=lambda c: [c.year,c.term, c.class_name])
    return render_template('index.html',**locals())


@main.route('/profile')
@login_required
def profile():
    my_user=current_user
    student=current_user.netid
    ###
    ### get all relevant submissions
    ###
    subs=db.session.query(Submission).filter(Submission.netid==student)
    fresh_subs=db.session.query(Submission).filter(and_(Submission.netid==student, Submission.new_submission==1) ).all()
    matched_subs=db.session.query(Submission).filter(and_(Submission.netid==student, Submission.submission_locked==1)).all()

    first_reviews = []
    for s in matched_subs:
        if is_reviewed(s):
            first_reviews.append(s)

    for c in first_reviews:
        matched_subs.remove(c)
            
    completed =[]
    for s in first_reviews:
        if is_complete(s):
            completed.append(s)
            
    for c in completed:
        first_reviews.remove(c)

    fresh_subs=sorted(fresh_subs,key=lambda c: [c.assignment,c.problem])
    matched_subs=sorted(matched_subs,key=lambda c: [c.assignment,c.problem])
    first_reviews = sorted(first_reviews,key=lambda c: [c.assignment,c.problem])
    completed=sorted(completed,key=lambda c: [c.assignment,c.problem])
    
    ###
    ### get all relevant reviews
    ###
    rmatched_subs = db.session.query(Submission).filter( or_(Submission.reviewer1==student,Submission.reviewer2==student)).all()
    
    rfirst_reviews = []
    for s in rmatched_subs:
        if is_reviewed(s):
            rfirst_reviews.append(s)

    for c in rfirst_reviews:
        rmatched_subs.remove(c)
            
    rcompleted =[]
    for s in rfirst_reviews:
        if is_complete(s):
            completed.append(s)
            
    for c in rcompleted:
        rfirst_reviews.remove(c)

    rmatched_subs=sorted(rmatched_subs,key=lambda c: [c.assignment,c.problem])
    rfirst_reviews = sorted(rfirst_reviews,key=lambda c: [c.assignment,c.problem])
    rcompleted=sorted(rcompleted,key=lambda c: [c.assignment,c.problem])
    
    
    return render_template('profile.html',**locals())

@main.route('/<c.class_name>/<c.year>/<c.term>/')
@login_required
def coursepage(c):
    """
    This is where the
    """
    return render_template('classpage.html',**locals())
    


#@main.route(f"/{sub.course}/{sub.year}/{sub.term}/{sub.submission_number}")
#@login_required
#def subpage(sub):
#
#    return render_template('submission.html',**locals())
    
    #return redirect(url_for('main.profile'))
    
