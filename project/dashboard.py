import sys
import numpy as np
import matplotlib.pyplot as plt
from statistics import *
from decimal import Decimal
from .webfunctions import *
import datetime



#INSTALL_PATH = '/users/t/d/tdupuy/dev/submission_tools/'
#INSTALL_PATH ='/Users/taylordupuy/Documents/web-development/dev/submission_tools/'
#sys.path.append(INSTALL_PATH+"../excel_tools")
#from table_editor import SheetObject
#from table_functions import *
#from matchmaker_functions import *
#from submission_functions import *

def get_date(unixtime):
    return datetime.fromtimestamp(unixtime)

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

def clean_dec(x):
    return format(x,'.3f')

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

#def update(S,mylist):
#    message = ""
#    for m in mylist:
#        snum=m['submission_number']
#        mold=S.get({'submission_number':m['submission_number']})
#        S.remove(mold)
#        S.append(m)
#        message = message + f" {snum}"
#    return "updated:" + message + "\n unsaved changes will be lost"


def save_hist(subs,key,S,filename,plot_title=""):
    n=len(subs)
    data=[x[key] for x in subs]
    plt.hist(data,bins=7)
    plt.title(plot_title)
    plt.savefig(filename)
    plt.clf()

def score1_hist(p0,scored1):
    """
    TODO: Add the n=X feature
    """
    ass=p0["assignment"]
    pro=p0["problem"]
    n=len(scored1)
    plt.hist(scored1, bins=7)  # arguments are passed to np.histogram
    plt.title(f"score1: assignment {ass}, problem {pro} (n={n})")
    plt.savefig(f"score1-{ass}-{pro}")
    
    """
    savefig(fname, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None, metadata=None)
    """
    
def score2_hist(p0,scored2,filepath="./"):
    ass=p0["assignment"]
    pro=p0["problem"]
    n=len(scored2)
    plt.hist(scored2, bins=7)  # arguments are passed to np.histogram
    plt.title(f"score2: assignment {ass}, problem {pro} (n={n})")
    filename=f"score2-{ass}-{pro}"
    plt.savefig(filepath+f"score2-{ass}-{pro}")
    return filename + ".png"


"""
tmatch
treview1
treview2
"""
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

###############################
###############################

if len(sys.argv)==1:
    PATH_TO_DATA = get_path_to_data()
    #tmode(1,PATH_TO_DATA)
elif len(sys.argv)>=2:
    PATH_TO_DATA = sys.argv[1]
    #tmode(1,PATH_TO_DATA)
elif len(sys.argv)==3:
    is_test = int(sys.argv[2])
    tmode(is_test,PATH_TO_DATA)
else:
    raise ValueError("dashboard.py only accepts 3 or fewer options")

roster_name = get_roster_name(PATH_TO_DATA)
course_name = get_course_name(PATH_TO_DATA)

#
# THIS NEEDS TO BE FIXED TO WORK MORE GENERALLY
#
PATH_TO_DASHBOARD = "/users/t/d/tdupuy/www-root/public/algebra-one/20/f/dashboard/"

#turn off the server
server_down =1
out_msg=webmode(server_down,PATH_TO_DATA)
print(out_msg)


today = datetime.date.today()
todays = today.strftime("%B %d, %Y")

path_to_sheet = PATH_TO_DATA + "roster.xlsx"
S = SheetObject(path_to_sheet,"submissions")
P = SheetObject(path_to_sheet,"assignments")
U = SheetObject(path_to_sheet,"roster")

exercises = P.get({})[1:]
users = U.get({})
submissions = S.get({})
NUM_USERS = len(users)

mid_image_table=""
mid_of_table=""

#u0=users[0]
#p0=exercises[1]
#s0=submissions[1]

"""
For a given problem.
How many are unmatched?
How many are matched?
How many people have not submitted?
How many are graded?
"""
for p0 in exercises:
    waiting = S.get({"assignment":p0["assignment"], "problem":p0["problem"],"submission_locked":0})
    num_waiting = len(waiting)
    matched = S.get({"assignment":p0["assignment"], "problem":p0["problem"],"submission_locked":1})
    num_matched = len(matched)
    num_available = NUM_USERS - num_matched
    num_submitted = num_matched+num_waiting
    
    ass=p0["assignment"]
    pro=p0["problem"]
    
    matched = S.get({"assignment":p0["assignment"], "problem":p0["problem"],"submission_locked":1})
    
    scored1 = []
    for m in matched:
        mnew=copyd(m)
        if m['review1_timestamp']>-1 and m['review2_timestamp']>-1:
            s1 = m['reviewer1_score']
            s2 = m['reviewer2_score']
            mnew['total_score1'] = (s1+s2)/2
            scored1.append(mnew)
    
    scored2 = []
    for m in scored1:
        reviewer1 = m['reviewer1']
        reviewer2 = m['reviewer2']
        s1 = m['reviewer1_score']
        s2 = m['reviewer2_score']
        search1=searchd(scored1,{'netid':reviewer1})
        search2=searchd(scored1,{'netid':reviewer2})
        if len(search1)>0 and len(search2)>0:
            mnew = copyd(m)
            sub1 = search1[0]
            sub2 = search2[0]
            r1=sub1['total_score1']
            r2=sub2['total_score1']
            w1 = float(r1/(r1+r2))
            w2 = float(r2/(r1+r2))
            ts2=w1*s1+w2*s2
            mnew['total_score2']=ts2
            scored2.append(mnew)
            
    update(S,scored2)
    
    """
    Histogram
    """
    total_scored2 = [m["total_score2"] for m in scored2]
    n = len(total_scored2)
    #plt.hist(total_scored2, bins=7)  # arguments are passed to np.histogram
    #plt.title(f"assignment {ass}, problem {pro} (n={n})")
    #plt.show()
    plot2filename=score2_hist(p0,total_scored2,PATH_TO_DASHBOARD)
    
    #average distance
    scorechanges=[]
    for m in scored2:
        scorechanges.append([m['total_score1']-m['total_score2']])
    
    if len(total_scored2)>0:
        mean0=mean(total_scored2)
        med0=median(total_scored2)
        if total_scored2>1:
            std0=stdev(total_scored2)
        else:
            std0=0
        time_data=get_times(scored2)
        rt0=mean(time_data['review_times'])
        mt0=mean(time_data['matching_times'])
    
    else:
        mean0=0
        med0=0
        std0=0
        rt0=0
        mt0=0
        
    
    html_image0=f'<img src="{plot2filename}" alt="{plot2filename}" />'
    
    start_of_table="""
    <table>
    <tr>
    <th>(ass,pro)</th>
    <th>subs</th>
    <th>not subbed</th>
    <th>waiting</th>
    <th>matches</th>
    <th>completed</th>
    <th>match time</th>
    <th>rev time </th>
    <th>mean</th>
    <th>median</th>
    <th>std</th>
    </tr>"""
    
    mid_of_table= mid_of_table+f"""
    <tr>
    <td> ({ass},{pro}) </td>
    <td>  {num_submitted} </td>
    <td>  {num_available} </td>
    <td>  {num_waiting} </td>
    <td>  {num_matched} </td>
    <td> {n} </td>
    <td>  {clean_dec(mt0)} </td>
    <td>  {clean_dec(rt0)} </td>
    <td>  {clean_dec(mean0)} </td>
    <td>  {clean_dec(med0)} </td>
    <td>  {clean_dec(std0)} </td>
    </tr>
    """
    mid_image_table = mid_image_table+f"<tr> {html_image0} </tr>"

    TITLE = f"SUBMISSION DASHBOARD (updated: {todays})"

    HTML_START=f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title> {TITLE} </title>
        <link rel="stylesheet" href="styles.css">
      </head>
      <h1> {TITLE} </h1>
      <body>
      """
    HTML_END="""
    </body>
    </html>
    """
    
    end_of_table="</table>"
    
S.save()
html_table = start_of_table+mid_of_table+end_of_table

caption = """
<p>
NOTES: <br>
match time,review time computed in days; completed submissions used (meaning the second score with the weighted average has been computed).<br>
submitted, available, waiting, and matched are all the number of people currently in each category for this problem.
</p>

<h1> Histograms of Scores</h1>
"""

image_table = "<center> <table>" + mid_image_table + end_of_table +"</center>"
html_page = HTML_START + html_table + caption + image_table + HTML_END
    
f = open(PATH_TO_DASHBOARD+"dashboard.html", "w")
f.write(html_page)
f.close()

"""
TURN WEBPAGE BACK ON
"""
server_down=0
out_msg=webmode(server_down,PATH_TO_DATA)
print(out_msg)
