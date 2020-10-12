from flask import Blueprint, render_template, request
from flask_login import login_required, current_user, flash
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
#https://www.tutorialexample.com/a-simple-guide-to-python-detect-pdf-file-is-corrupted-or-incompleted-python-tutorial/

def isFullPdf(f):
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

def show_dashboard(coursename,year,term):
    bigblock="dashboard"
    return bigblock
    
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

#################################

@main.route('/<coursename>/<year>/<term>', methods=['GET'])
def coursepage(coursename,year,term):
    yearlong=year_long(year)
    termlong=term_long(term)
    coursenamelong=coursename_long(coursename)
    return render_template('coursepage.html',**locals())

#################################

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

#################################

@main.route('/profile')
@login_required
def profile():
    email=current_user.email
    ###
    ### get all relevant submissions
    ###
    subs=db.session.query(Submission).filter(Submission.email==email).all()
    subdict=sort_subs_by_stage(subs)
    fresh_subs=subdict['waiting']
    matched_subs=subdict['just_matched']
    first_reviews = subdict['first_reviews']
    completed=subdict['completed']
    ###
    ### get all relevant reviews
    ###
    reviewsubs = db.session.query(Submission).filter( or_(Submission.reviewer1==email,Submission.reviewer2==email)).all()
    sorted_reviews = sort_subs_by_stage(reviewsubs)
    rmatched_subs= sorted_reviews['just_matched']
    rfirst_reviews = sorted_reviews['first_reviews']
    rcompleted= sorted_reviews['completed']
    
    urldict={}
    for sub in subs+reviewsubs:
        urldict[sub.submission_number] = submission_url(sub)
    
    return render_template('profile.html',**locals())



def sort_subs_by_stage(subs):
    cleandict={}
    matched = []
    cleandict['waiting']=[]
    cleandict['just_matched']=[]
    cleandict['first_reviews']=[]
    cleandict['completed']=[]
    
    #split into matched and unmatched
    for s in subs:
        if s.is_matched==0:
            cleandict['waiting'].append(s)
        else:
            matched.append(s)
    
    #collect ones with reviews
    for s in matched:
        if is_reviewed(s):
            cleandict['first_reviews'].append(s)
    
    #remove ones with removed from the matched
    #these are now in the matching stage but waiting
    #for first reviews
    for c in cleandict['first_reviews']:
        matched.remove(c)
    cleandict['just_matched']=matched
    
    #collect all of the completed ones
    for s in cleandict['first_reviews']:
        if is_complete(s):
            cleandict['completed'].append(s)
        
    #to complete remove the completed ones from the first_review list
    for c in cleandict['completed']:
        cleandict['first_reviews'].remove(c)
        
        
    clean_dict['waiting']=sorted(clean_dict['waiting'],
    key=lambda c: [c.assignment,c.problem])
    clean_dict['just_matched']=sorted(clean_dict['just_matched'],
       key=lambda c: [c.assignment,c.problem])
    clean_dict['first_reviews']=sorted(clean_dict['first_reviews'],
       key=lambda c: [c.assignment,c.problem])
    clean_dict['completed']=sorted(clean_dict['completed'],
       key=lambda c: [c.assignment,c.problem])
        
    return cleandict

def sorted_user_submissions(content):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email = content['email']
    subs=db.query(Submission).filter(
    Submission.coursename=coursename,
    Submission.year=year,
    Submission.term=term,
    Submission.email=email).all()
    return sort_subs_by_stage(subs)

@main.route('/upload', methods=['GET'])
@login_required
def upload():
    courses = db.session.query(Course).all()
    courses = sorted(courses, key=lambda c: [c.year,c.term, c.coursename])
    
    namedict={}
    for c in courses:
        namedict[c.id]=course_html(c)
    return render_template('select_course_upload.html',**locals())

#################################

"""
@main.route('/<coursename>/<year>/<term>/upload', methods=['GET','POST'])
@login_required
def uploader(coursename,year,term):
    if request.method == 'GET':
        return render_template('upload.html',**locals())
    elif request.method == 'POST':

    #argdict=request.args.to_dict(flat=False)
    message = ""
     
        for j in range(1,6):
            content = {}
            content['email']=
            content['coursename']
            content['assignment']
            content['problem']request.form[f"problem{j}"]
            content['file']=request.file[f"file{j}"]
            a0=request.form[f"assignment{j}"]
            mini_result = process_submission(content)
            result
"""

@main.route('/<coursename>/<year>/<term>/uploader2', methods=['GET','POST'])
@login_required
def uploader2(coursename,year,term):
    if request.method == 'GET':
        return render_template('uploader2.html',**locals())
    if request.method == 'POST':
        content = request.args.to_dict(flat=False)
        content['file']=request.file['file']
        result = process_submission(content)
        if result['success']==1:
            subs=get_submission(content)
            flash(result['message'])
            send_confirmation_email(subs)
            return redirect(url_for('profile',
            coursename=coursename,
            year=year,
            term=term))
            
        if result['success']==0:
            flash(result['message'])
            return redirect(url_for('uploader2',
            coursename=coursename,
            year=year,
            term=term))
            
def increment_submission_count(path_to_data='./'):
    f=open(path_to_data + "variables.json",'r')
    variables=json.loads(f.read())
    f.close()
    variables['submission_number'] = variables['submission_number']+1
    f = open(path_to_data+"variables.json",'w')
    json.dump(variables,f)
    f.close()
    return "submission number: %s. " % variables['submission_number']

def get_submission_count(path_to_data="./"):
    f=open(path_to_data + "variables.json",'r')
    variables=json.loads(f.read())
    f.close()
    return variables['submission_number']



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

def current_is_reviewer(sub):
    reviewers=get_reviewers(sub)
    if reviewers.count(current_user.email)>0:
        return True
    else:
        return False
        
def reviewer_reject(sub):
    """
    For when the current user rejects a submission.
    """
    if current_is_reviewer(sub):
        j = get_reviewers(content).index(reviewer)+1
        if j==1:
            sub.bad1=1
            sub.reviewer1_score=0
            sub.reviewer1_assignment_time=int(time.time())
            
        if j==2:
            sub.bad2=1
            sub.reviewer2_score=0
            sub.reviewer2_assignment_time=int(time.time())
            
    if sub.bad1==1 and sub.bad2==1:
        result=notify_rejection(sub)
        db.session.remove(sub)
    else:
        result={}
        result['message']="Your rejection of this problem has been recorded."
        result['success']=1
        
    return result

def notify_rejection(sub):
    email={}
    email['subject']=f"Improper Submission {sub.submission_number}"
    message="""
    This message is to notify you that reviewers of {sub.submission_number} has indicted that this is an improper submission.
    
    This is for assignment {sub.assignment}, problem {sub.problem}.
    
    This is likely because the problem doesn't match the what was input or the PDF was unreadable.
    """
    email['receiver']=sub.email
    result=send_basic_email(email)
    return result
    
def notify_rejection(sub):
    email={}
    email['subject']=f"Improper Submission {sub.submission_number}"
    message="""
    This message is to notify you that reviewers of {sub.submission_number} has indicted that this is an improper submission.
    
    This is for assignment {sub.assignment}, problem {sub.problem}.
    
    This is likely because the problem doesn't match the what was input or the PDF was unreadable.
    """
    email['receiver']=sub.email
    result=send_basic_email(email)
    return result
    
def has_first_reviews(sub):
    if sub.reviewer1_score>-1 and sub.reviewer2_score>-1:
        return True
    else:
        return False
        
def get_missing_reviewers(sub):
    late_reviewers = []
    if sub.reviewer1_score=-1:
        late_reviewers.append(sub.reviewer1)
    if sub.reviwer2_score=-1:
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
        
    
        
    
def get_reviewersc(content):
    #assumes valid content
    sub=get_submission(content)[0]
    return [sub.reviewer1,sub.reviewer2]

def process_submission(content):
    """
    We need to check
        --is_locked
        --
    """
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email=content['email']
    assignment=content['assignment']
    problem=content['problem']
    file=content['file']
    subs = get_submission(content)
    result={}
    result['success']=0
    if len(subs)==0:
        #new submission
        if isFullPdf(file) and is_valid_problem(content):
            sub = Submission()
            sub.email=email
            sub.assignment=assignment
            sub.problem=problem
            sub.data=file
            sub.timestamp=int(time.time())
            sub.submission_number=get_submission_count()
            increment_submission_count()
            """
            new_entry = {}
            new_entry['netid'] = user_id
            new_entry['assignment'] = assignment
            new_entry['problem'] = problem
            new_entry['submission_number'] = new_submission_number
            new_entry['submission_time'] = timestamp
            new_entry['new_submission']=1
            new_entry['submission_locked']=0
            new_entry['closed']=0
            new_entry['total_score1']=0
            new_entry['total_score2']=0
            new_entry['reviewer1_assignment_time']=-1
            new_entry['reviewer1']=''
            new_entry['reviewer1_score']=-1
            new_entry['review1']=''
            new_entry['review1_timestamp']=-1
            new_entry['review1_locked']=0
            new_entry['reviewer2_assignment_time']=-1
            new_entry['reviewer2']=''
            new_entry['reviewer2_score']=-1
            new_entry['review2']=''
            new_entry['review2_timestamp']=-1
            new_entry['review2_locked']=0
            new_entry['new_submission']=1
            new_entry['new_match']=0
            new_entry['new_review1']=0
            new_entry['new_review2']=0
            new_entry['new_completion']=0
            """
            result['success']=1
            result['message']=f"assignment {assignment}, problem {problem} (new): successfully submitted."
    if len(subs)==1:
        sub = subs[0]
        if sub.submission_locked==1:
            result['success']=0
            result['message']=f"assignment {assignment}, problem {problem}: failed. submission is locked.}
        else:
            if isFullPdf(file):
                sub.data=file
                sub.timestamp=int(time.time())
                result['success']=1
                result['message']=f"assignment {assignment}, problem {problem}: PDF successfully updated."
    db.session.commit()
    return result
            

def all_same(mylist):
    allsame=True
    if len(mylist)==0:
        return True
    else:
        for x in mylist:
            if x!=x[0]:
                return False
        return True

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

#I decided this was a terrible idea and the files should be stored next to the submission.
#maybe that is a bad idea too.
"""
def get_file(content):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email=content['email']
    assignment=content['assignment']
    problem=content['problem']
    submission_number=content['submission_number']
    files=db.session.query(Files).query(Files.coursename=coursename,
    Files.year==year,
    Files.term==term,
    Files.email==email,
    Files.submission_number==submission_number).all()
    result={}
    result['success']=0
    result['message']=""
    #I'm not really following through with this result dict being passed"
    if len(files)==0:
        result['message']="file not found"
        result['success']=0
        raise ValueError("file not found")
    elif len(files)!=1:
        result['message']="multiple files!"
        result['success']=0
        raise ValueError("multiple files")
    else:
        fileobject=files[0]
        return fileobject
"""
    
    
def get_submission(content):
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
    
#we need to do this with all of the emails
def convert_to_lowercase(mystring)
    return mystring.lower()
    
def is_valid_problem(content):
    coursename=content['coursename']
    year=content['year']
    term=content['term']
    email=content['email']
    assignment=content['assignment']
    problem=content['problem']
    #file=content['file']
    probs = db.query(Problem).filter(and_(Problem.coursename==couresname,
    Problem.year==year,
    Problem.term==term,
    Problem.assignment==assignment,
    Problem.problem==problem)).all()
    if len(probs)==1:
        return True
    else:
        return False

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


def is_valid_score(score):
    
def is_locked()

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
    
def write_review(user_id,submission_number,score,review,timestamp,path_to_data=PATH_TO_DATA):
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
