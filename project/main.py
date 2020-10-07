from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from . import db
from sqlalchemy import or_, and_
from .models import Submission, Course
import time
import datetime
#from pyPdf2 import PdfFileReader

import sys
sys.path.append('/Users/taylordupuy/Documents/web-development/dev/email_tools')
from email_functions import *


#
# SOME AUXILLARY FUNCTIONS, MOVE LATER
#
def isFullPdf(f):
    #https://www.tutorialexample.com/a-simple-guide-to-python-detect-pdf-file-is-corrupted-or-incompleted-python-tutorial/
    end_content = ''
    start_content = ''
    size = os.path.getsize(f)
    if size < 1024: return False
    with open(f, 'rb') as fin:
        #start content
        fin.seek(0, 0)
        start_content = fin.read(1024)
        start_content = start_content.decode("ascii", 'ignore' )
        fin.seek(-1024, 2)
        end_content = fin.read()
        end_content = end_content.decode("ascii", 'ignore' )
    start_flag = False
    #%PDF
    if start_content.count('%PDF') > 0:
        start_flag = True
    
        
    if end_content.count('%%EOF') and start_flag > 0:
        return True
    eof = bytes([0])
    eof = eof.decode("ascii")
    if end_content.endswith(eof) and start_flag:
        return True
    return False


def submission_url(s):
    return f'{s.coursename}/{s.year -2000}/{s.term}/{s.submission_number}'
    
def date(unixtime, format = '%m/%d/%Y %H:%M'):
    d = datetime.datetime.fromtimestamp(unixtime)
    return d.strftime(format)

def is_matched(s):
    if s.reviewer1_assignment_time>-1 and s.s.reviewer2_assignment_time>-1:
        return True
    else:
        return False

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
    
    
def show_submission_page(submission):
    return render_template('submission.html',**locals())

def show_dashboard(course):
    pass
    
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
        namedict[c.id]=course_html(c)
    return render_template('index.html',**locals())


@main.route('/<coursename>/<year>/<term>', methods=['GET'])
def coursepage(coursename,year,term):
    yearlong=year_long(year)
    termlong=term_long(term)
    coursenamelong=coursename_long(coursename)
    return render_template('coursepage.html',**locals())


@main.route('/<coursename>/<year>/<term>/<submission_number>', methods=['GET'])
@login_required
def submission_page(coursename,year,term,submission_number):
    """
    This needs a get and show method
    """
    subs=db.session.query(Submission).filter(and_(Submission.submission_number==submission_number,Submission.coursename==coursename,Submission.year==(int(year)+2000),Submission.term==term)).all()
    if len(subs)==1:
        s=subs[0]
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
        return render_template('submission.html',**locals())
    else:
        return f"404 not found:{len(subs)}"
    
    #return redirect(url_for('main.profile'))


@main.route('/profile')
@login_required
def profile():
    my_user=current_user
    student=current_user.netid
    ###
    ### get all relevant submissions
    ###
    subs=db.session.query(Submission).filter(Submission.netid==student).all()
    urldict={}
    for sub in subs:
        urldict[sub.submission_number] = submission_url(sub)
    
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

@main.route('/upload', methods=['GET'])
@login_required
def upload():
    courses = db.session.query(Course).all()
    courses = sorted(courses, key=lambda c: [c.year,c.term, c.coursename])
    
    namedict={}
    for c in courses:
        namedict[c.id]=course_html(c)
    return render_template('select_course_upload.html',**locals())
    

@main.route('/<coursename>/<year>/<term>/upload', methods=['GET','POST'])
@login_required
def uploader(coursename,year,term):
#
    if request.method == 'GET':
        return render_template('upload.html')

    elif request.method == 'POST':
    #https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        #argdict=request.args.to_dict(flat=False)
        request.form['conduct']
        message = ""
        
        
        for j in range(1,6):
            p0=request.form[f"problem{j}"]
            a0=request.form[f"assignment{j}"]
            file0=request.file[f"file{j}"]
            db.session.query(Course)
            
            
            is_a_pdf=isFullPdf(file0)
            
            
        for j in range(1,11):
            score0=request.form[f"score{j}"]
            review=request.form[f"review{j}"]
            subnum0=request.form[f"subnumber{j}"]
        
@main.route('/grades', methods=['GET'])
@login_required
def uploader(coursename,year,term):
        return redirect('main.profile')

#We could handle a lot of data with queries
#On each user page we could bake the current course into the submission page request.
#We could also bake the course into the upload page requests.
#https://pageroot/upload?course=jedi&year=sith&term=human
#request.args.to_dict(flat=False)
#https://dev.to/svencowart/multi-value-query-parameters-with-flask-3a92


