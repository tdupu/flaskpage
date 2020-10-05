from flask_login import UserMixin
from . import db
#import os
#import sys
#from sqlalchemy import Column, ForeignKey, Integer, String, Float, Numeric, JSON
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import relationship
#from sqlalchemy import create_engine

#Base = declarative_base()

"""
This needs to be modified to work with out excel based databases.
"""

class User(UserMixin,db.Model):
    __tablename__ = 'roster'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    pronoun=db.Column(db.String(250))
    uvm_student=db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    courses = db.Column(db.String(1000))
    major = db.Column(db.String(250))
    degree = db.Column(db.String(250))
    credits = db.Column(db.Integer)
    reg_status = db.Column(db.String(250))
    reg_data = db.Column(db.String(250))
    email = db.Column(db.String(250))
    netid = db.Column(db.String(250))
    password = db.Column(db.String(250))
    
class Course(db.Model):
    __tablename__ = 'courses'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = db.Column(db.Integer)
    term = db.Column(db.String(250)) #F=Fall, S=Spring, U=Summer
    class_number = db.Column(db.String(250))
    uvm_course = db.Column(db.Integer)
    zulipurl = db.Column(db.String(250))
    zuliprc = db.Column(db.String(250))
    homepage = db.Column(db.String(250))
    size = db.Column(db.Integer)

  

class Problem(db.Model):
    __tablename__ = 'assignments'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = db.Column(db.Integer)
    term = db.Column(db.String(250)) #F=Fall, S=Spring, U=Summer
    assignment = db.Column(db.String(250))
    problem = db.Column(db.String(250))
    references = db.Column(db.String(1000))

class Submission(db.Model):
    __tablename__ = 'submissions'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String)
    year = db.Column(db.Integer)
    term = db.Column(db.Integer)
    submission_number = db.Column(db.Integer)
    submission_locked = db.Column(db.Integer)
    netid = db.Column(db.String(250))
    email = db.Column(db.String(250))
    assignment = db.Column(db.String(250))
    problem = db.Column(db.String(250))
    closed = db.Column(db.Integer)
    submission_time = db.Column(db.Integer)
    total_score1 = db.Column(db.Float)
    total_score2 = db.Column(db.Float)
    reviewer1_assignment_time =db.Column(db.Integer)
    reviewer1 = db.Column(db.String(250))
    reviewer1_email = db.Column(db.String(250))
    reviewer1_score = db.Column(db.Integer)
    review1 = db.Column(db.String(1000))
    review1_timestamp = db.Column(db.Integer)
    review1_locked = db.Column(db.Integer)
    reviewer2_assignment_time=db.Column(db.Integer)
    reviewer2 = db.Column(db.String(250))
    reviewer2_email = db.Column(db.String(250))
    reviewer2_score = db.Column(db.Integer)
    review2 = db.Column(db.String(1000))
    review2_timestamp = db.Column(db.Integer)
    review2_locked = db.Column(db.Integer)
    new_submission = db.Column(db.Integer)
    new_match = db.Column(db.Integer)
    new_review1 = db.Column(db.Integer)
    new_review2 = db.Column(db.Integer)
    new_completion = db.Column(db.Integer)

