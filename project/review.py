from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
from .models import User
from .webfunctions import *



review = Blueprint('review', __name__)

def process_review(content):
    #assumes submission is valid and is a reviewer
    user = current_user
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email=content['email']
    assignment=content['assignment']
    problem=content['problem']
    reviewer=content['reviewer']
    review=content['review']
    comments=content['comments']
    timestamp=int(time.time())
    sub=get_submission(content)[0]
    j = get_reviewers(content).index(reviewer)+1

def is_valid_review(content):
    """
    returns a message and reviewer number if valid.
    returns a message and j=0 if not valid.

    if any of the entries are empty, kill it.
    if a previous review exists and its not the end of the day, write it.
    if a previous review exists and it its past the end of the day, kill it.
    """
    j=-1 # returns reviewer number or zero
    message = '' #holy moly if you don't initialize this string it gets mad
    n=0
    
    if content['review']=='' and j!=0:
        j=0
        message = "*review of %s rejected. empty review. (if the review is a 10/10 then write something like 'perfect'.) <br>" % submission_number
    
    if n==0 and j!=0:
        message = "*review of %s rejected. empty database. <br>" % submission_number
        j=0
        
    if n==1 and j!=0:
        submission = entries[0]
        old_entry = submission #keep a copy for the replace function later
        reviewer1 = submission['reviewer1']
        reviewer2 = submission['reviewer2']
        is_locked = [submission['review1_locked'],submission['review2_locked']]
    
        if user_id == reviewer1:
            j=1
        elif user_id == reviewer2:
            j=2
        else:
            #message = """
            #*review of %s rejected. incorrect reviewer. <br>
            #""" % submission_number
            message = """
            *review of %s rejected. incorrect reviewer. reviewers are %s and %s. <br>
            """ % (submission_number, reviewer1,reviewer2)
            j=0
     
    if j>0 and is_locked[j-1]:
        j=0
        message = """
        *review of %s rejected. closed. <br>
        """ % submission_number
    
    if j>0:
        try:
            score = int(score)
            if not (0<=score and score <= 10):
                j=0
                message="""
                *review of %s rejected. score must be between 0 and 10. <br>
                """ % submission_number
        except:
            j=0
            message = """
            *review of %s rejected. score set to '%s'. must be an integer. <br>
            """ % (submission_number,score)
    
    if j>0:
        message = """
        *review of %s recorded. score set to %s/10.<br>
        """ % (submission_number,score)
    
    return message, j
    
def write_review(
user_id,
submission_number,
score,
review,
timestamp):
    message,j=is_valid_review(user_id,submission_number,score,review,timestamp,path_to_data)
        
    if j!=0: #write the review
        CONSTANT_DATA = get_constant_data()
        roster_name = CONSTANT_DATA['roster_name']
        S=SheetObject(path_to_data + roster_name, "submissions")
        
        old_entry = S.get({'submission_number':submission_number})[0]
        
        #NEVER DO THIS WITH DICTIONARIES: new_entry = old_entry
        #it have new_entry point to old_entry in memory
        #note: copyd function in ../excel_tools/table_functions.py
        new_entry = {}
        for key in S.keys:
            new_entry[key] = old_entry[key]
        
        new_entry['review%s' % j] = review
        new_entry['reviewer%s_score' % j] = int(score) #not scorej, holy shit this bug took me forever.
        new_entry['review%s_timestamp' % j] = timestamp
        new_entry['new_review%s' % j] = 1
        
        #check to see if this new review makes the entry complete.
        k = (j%2) +1 #other index
        if old_entry['reviewer%s_score' % k]>-1:
            new_entry['new_completion']=1
        
        
        #DEBUG
        #A=set(list(new_entry.keys()))
        #B=set(list(old_entry.keys()))
        #print(B.issubset(A))
        #
        #for a in list(old_entry):
        #    print(a)
        #
        #for b in list(new_entry):
        #    print(b)
        #no such entry old_entry
        S.replace(old_entry,new_entry)
        S.save()
            
    return message
