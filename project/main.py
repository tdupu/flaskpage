from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
from sqlalchemy import or_, and_
#from .models import Submission, Course, Problem,
#from .models import year_long, term_long, coursename_long
from .models import *
from .webfunctions import *

import sys
sys.path.append('/Users/taylordupuy/Documents/web-development/dev/email_tools')
from email_functions import *

#
# SOME AUXILLARY FUNCTIONS, MOVE LATER
#
#https://www.tutorialexample.com/a-simple-guide-to-python-detect-pdf-file-is-corrupted-or-incompleted-python-tutorial/

def show_submission_page(submission):
    return render_template('submission.html',**locals())

def show_dashboard(coursename,year,term):
    bigblock="dashboard"
    return bigblock

    
main = Blueprint('main', __name__)

#############################################
#############################################
#############################################

@main.route('/')
def index():
    #db.session.query(Course)
    #submissions = db.session.query(Submission).filter(Submission.netid=='tfbloom')
    courses = db.session.query(Course).all()
    courses = sorted(courses, key=lambda c: [c.year,c.term, c.coursename])
    
    namedict={}
    for c in courses:
        namedict[c.id]=c.html()
    return render_template('index.html',**locals())

#################################

@main.route('/<coursename>/<year>/<term>', methods=['GET'])
def coursepage(coursename,year,term):
    
    yearlong=year_long(year)
    termlong=term_long(term)
    coursenamelong=coursename_long(coursename)
        
    course=db.session.query(Course).filter(and_(
    Course.coursename==coursename,
    Course.year==year,
    Course.term==term)).first()
    
    probs = course.get_problems()
    print(probs)
    
    for p in probs:
        try:
            p.make_clean_data()
            print(f"{p.assignment} {p.problem} is ok")
            
        except:
            pass
            
    print( course.url() )
    
    return "YAY"
    #return render_template('coursepage.html',**locals())

#################################

@main.route('/upload', methods=['GET'])
@login_required
def upload():
    courses = db.session.query(Course).all()
    courses = sorted(courses, key=lambda c: [c.year,c.term, c.coursename])
    
    namedict={}
    for c in courses:
        namedict[c.id]=c.html()
    return render_template('select_course_upload.html',**locals())

#################################
            
@main.route('/grades', methods=['GET'])
@login_required
def grades():
    my_user=current_user
    return "grades"

#We could handle a lot of data with queries
#On each user page we could bake the current course into the submission page request.
#We could also bake the course into the upload page requests.
#https://pageroot/upload?course=jedi&year=sith&term=human
#request.args.to_dict(flat=False)
#https://dev.to/svencowart/multi-value-query-parameters-with-flask-3a92

#https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
#https://github.com/mjhea0/flask-ajax-form/blob/master/sqlalchemy-example/hello/views.py
