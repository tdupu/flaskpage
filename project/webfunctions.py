def is_reviewed(s):
    return s.review1_timestamp>-1 and s.review2_timestamp>-1

def is_complete(s):
    if is_reviewed(s):
        a=s.assignment
        p=s.problem
        r1 = s.reviewer1
        r2 = s.reviewer2
        subs = session.query(Submission).filter( and_(or_(Submission.netid==r1,Submission.netid==r2),Submission.assignment ==a,Submission.problem ==p))
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
    subs=session.query(Submission).filter( and_(Submission.netid==user, Submission.assignment==ass))
    subs = sorted(subs, key=lambda s: s.total_score2)
    return np.mean([s.total_score2 for s in subs[0:2]])
