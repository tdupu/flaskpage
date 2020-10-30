from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
#from . import db
from .models import db
from .models import User, Submission
from sqlalchemy import or_, and_
from .webfunctions import *
from .models import coursename_long, term_long
from project.email_tools.email_functions import *
from werkzeug.datastructures import ImmutableMultiDict


def reviewer_reject(sub):
    """
    For when the current user rejects a submission.
    The email is built into this process.
    """
    if sub.is_reviewer(current_user):
        j = sub.get_reviewer_index(current_user)
        if j==1:
            sub.bad1=1
            sub.reviewer1_score=0
            sub.review2_timestamp=int(time.time())
            sub.review1_locked=1
            sub.new_review1=1
            
        elif j==2:
            sub.bad2=1
            sub.reviewer2_score=0
            sub.review2_timestamp=int(time.time())
            sub.review2_locked=1
            sub.new_review2=1
        
        else:
            pass
        
        db.session.commit()
        
    if sub.bad1==1 and sub.bad2==1:
        result=notify_rejection(sub)
        db.session.remove(sub)
        db.session.commit()
    else:
        result={}
        result['message']="Your rejection of this problem has been recorded."
        result['success']=0
        
    db.session.commit()
    
    return result

def notify_rejection(sub):
    email={}
    email['subject']=f"Submission {sub.submission_number} Rejected By Reviewers"
    message="""
    This message is to notify you that reviewers of {sub.submission_number} has indicted that this is an improper submission.
    
    This is for assignment {sub.assignment}, problem {sub.problem}.
    
    This is likely because the problem doesn't match the what was input or the PDF was unreadable.
    
    This submission has been deleted from the database.
    
    You may resubmit without penalty.
    
    From,
    Taylor's Automated Emailer
    """
    email['receiver']=sub.email
    result=send_basic_email(email)
    return result

def submit_review(content):
    sub=get_submission(content)
    if sub.is_reviewer(current_user):
         j = sub.get_reviewer_index(current_user)
    if j==1 and sub.review1_locked==0:
        sub.reviewer1_score=0
        sub.review1=content['review']
        sub.reviewer1_score=content['score']
        sub.review1_timestamp=int(time.time())
        sub.review1_locked=1
        sub.new_review1=1
        
    elif j==2 and sub.review2_locked==0:
        sub.reviewer2_score=0
        sub.review2=content['review']
        sub.reviewer2_score=content['score']
        sub.review2_timestamp=int(time.time())
        sub.review2_locked=1
        sub.new_review2=1
        
    if sub.review1_locked==1 and sub.review2_locked==1:
        sub.new_completion==1
        
    sub.commit()
    
    flash('This review has been recorded. You can now visit the submission page.')
    return redirect(url_for(prof.profile))
            
##############################
##############################

subpage = Blueprint('subpage', __name__)

@subpage.route('/<coursename>/<year>/<term>/<submission_number>', methods=['GET'])
@login_required
def submission_page(coursename,year,term,submission_number):
    """
    This needs a get and show method
    """
    
    s=db.session.query(Submission).filter(
    Submission.submission_number==int(submission_number)
    ).first()
    dates = {}
    times = [s.submission_time,s.review1_timestamp,s.reviewer1_assignment_time,s.review2_timestamp]
    for t in times:
        if t>0:
            dates[t]=date(t)
        else:
            dates[t]='NA'
    
    coursenamelong = coursename_long(s.coursename)
    #year is already long
    termlong = term_long(s.term)
    is_late=s.is_late(current_user)
    #if True:
    if s.user == current_user:
        is_submitter=True
        is_reviewer=False
        #return "Hello World"
        return render_template('submission.html',**locals())
            
    elif s.has_submitted_review(current_user)==True:
        is_submitter=False
        is_reviewer=True
        return render_template('submission.html',**locals())
        
    elif s.needs_review(current_user):
        is_submitter=False
        is_reviewer=True
        return render_template('review.html', **locals())
    
    else:
        return "You seem to have nothing to do with this submission."
        
@subpage.route('/<coursename>/<year>/<term>/<submission_number>', methods=['POST'])
@login_required
def review_post(coursename,year,term,submission_number):
    #content = request.args.to_dict(flat=False)
    #content=request.to_json()
    # ImmutableMultiDict([('submit_button', 'submit'), ('score', '5.0'), ('review', 'something'), ('conduct', 'on')])
    imd = ImmutableMultiDict(request.form)
    content =imd.to_dict(flat=True)
    content['coursename']=coursename
    content['year']=year
    content['term']=term
    content['submission_number']=submission_number
    #content['email']=current_user.email #or maybe this needs to be the submitter
    sub=get_submission(content)
        
    if content["submit_button"]=="return to sender":
        reviewer_reject(sub)
        flash('This submission has been rejected.')
        return redirect(url_for(prof.profile))
        
        
    if content["submit_button"]=="download submission":
        return "DOWNLOADING DOOP DOOP DEE"
        
    if content["submit_button"]=="submit":
            
        if content['conduct']=="off":
            flash('Please verify code of conduct.')
            return redirect(f'/{coursename}/{year}/{term}/{submission_number}')
        
        elif content['conduct']=="on":
                   submit_review(content)
    
    else:
        return f"it failed... here is the post data {content}"


#https://pythonprogramming.net/flask-send-file-tutorial/
@subpage.route('/<coursename>/<year>/<term>/return-files/')
@login_required
def return_files(coursename,year,term):
    content=request.args.to_dict(flat=True)
    content['coursename']=coursename
    content['year']=year
    content['term']=term
    
    sub=get_submission(content)
    
    if sub.is_reviewer(current_user) or sub.is_submitter(current_user):
        try:
            return send_file(f'data/{coursename}/{year}/{term}/uploads/{coursename}-{submission_number}-{assignment}-{problem}.pdf', attachment_filename=f'{coursename}-{submission_number}-{assignment}-{problem}.pdf')
        except Exception as e:
            return str(e)
            
    else:
        return "You do not have permission to view this."

