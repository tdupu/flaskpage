from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
from .models import User

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
    
def process_submission(content, to_database=False):
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
            if to_database==True:
                sub.data=file
            else:
                path_to_data=f'data/{coursename}/{year}/{term}/uploads/
                filename='{coursename}-{assignment}-{problem}-{submission_number}'
                with open(path_to_data+filename,'w') as f:
                    f=file
            sub.timestamp=int(time.time())
            sub.submission_number=get_submission_count()
            increment_submission_count()
            sub.new_submission=1
            sub.submission_locked=0
            sub.closed=0
            sub.total_score1=0
            sub.total_score2=0
            sub.reviewer1_assignment_time=-1
            sub.reviewer1=''
            sub.reviewer1_score=-1
            sub.review1=''
            sub.review1_timestamp=-1
            sub.review1_locked=0
            sub.reviewer2_assignment_time=-1
            sub.reviewer2=''
            sub.reviewer2_score=-1
            sub.review2=''
            sub.review2_timestamp=-1
            sub.review2_locked=0
            sub.new_submission=1
            sub.new_match=0
            sub.new_review1=0
            sub.new_review2=0
            sub.new_completion=0
            result['success']=1
            result['message']=f"assignment {assignment}, problem {problem} (new): successfully submitted."
            db.session.commit()
    elif len(subs)==1:
        sub = subs[0]
        if sub.submission_locked==1:
            result['success']=0
            result['message']=f"assignment {assignment}, problem {problem}: failed. submission is locked."
        else:
            if isFullPdf(file):
                if to_database=True:
                    sub.data==file
                    sub.timestamp=int(time.time())
                else:
                    path_to_data=f'data/{coursename}/{year}/{term}/uploads/
                    filename='{coursename}-{assignment}-{problem}-{submission_number}'
                    with open(path_to_data+filename,'w') as f:
                        f=file
                    
                 result['success']=1
                 result['message']=f"assignment {assignment}, problem {problem}: PDF successfully updated."
                 db.session.commit()
                 
            else:
                result['success']=0
                result['message']=f"assignment {assignment}, problem {problem}: failed. Not a PDF."
    else:
        raise ValueError("DOUBLE SUBMISSIONS IN THE DATABASE")
    
    return result
    
#######################

upload = Blueprint('upload', __name__)

@upload.route('/<coursename>/<year>/<term>/uploader2', methods=['GET','POST'])
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
            return redirect()
            

