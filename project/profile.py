from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import db
from .models import User, Submission
from sqlalchemy import or_


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

########################
prof = Blueprint('prof', __name__)
#####################

@prof.route('/profile')
@login_required
def profile():
    my_user=current_user #need this for the html
    email=current_user.email
    ###
    ### get all relevant submissions
    ###
    times={}
    subs=db.session.query(Submission).filter(Submission.email==email).all()
    subdict=sort_subs_by_stage(subs)
    print(subdict)
    fresh_subs=subdict['waiting']
    matched_subs=subdict['just_matched']
    first_reviews = subdict['first_reviews']
    completed=subdict['completed']
    
    for sub in fresh_subs:
        #times[sub.submission_number]=sub.days_overdue()
        times[sub.submission_number]=sub.days_since_submitted()
        
    for sub in matched_subs + first_reviews:
        times[sub.submission_number]=sub.days_since_matched()
    
    
    
    ###
    ### get all relevant reviews
    ###
    
    #this is turning up empty
    #reviewsubs = db.session.query(Submission).filter( or_(Submission.reviewer1_email==email,Submission.reviewer2_email==email)).all()

    
    reviewsubs = db.session.query(Submission).filter(or_(Submission.reviewer1==current_user.netid, Submission.reviewer2==current_user.netid)).all()
    
    finished=[]
    todo=[]
    
    for s in reviewsubs:
        if s.has_submitted_review(current_user):
            finished.append(s)
        else:
            todo.append(s)
            times[s.submission_number]=s.days_since_matched()
            

    sorted_reviews=sort_subs_by_stage(finished,reviewer=True)
    rmatched_subs= sorted_reviews['just_matched']
    rfirst_reviews = sorted_reviews['first_reviews']
    rcompleted= sorted_reviews['completed']
    
    urldict={}
    for sub in subs+reviewsubs:
        urldict[sub.submission_number] = sub.url()
    
    return render_template('profile.html',**locals())


@prof.route('/<coursename>/<year>/<term>/<submission_number>/poke', methods=['POST'])
@login_required
def poke(coursename,year,term,submission_number):
    content={}
    content['coursename']=coursename
    content['year']=year
    content['term']=term
    content['submission_number']=submission_number
    sub=get_submission(content)
    sub.poke_reviewers()
    result=sub.notify_late_reviewers()
    flash( result['message'] )
