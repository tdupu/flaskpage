import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Numeric, JSON, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

#https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
"""
Running
    python database_declarative.py
Will create flaskpage_database.db
"""

Base = declarative_base()
 
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    pronoun=Column(String(250))
    uvm_student=Column(Integer)
    student_id = Column(Integer)
    courses = Column(String(1000))
    major = Column(String(250))
    degree = Column(String(250))
    credits = Column(Integer)
    reg_status = Column(String(250))
    reg_data = Column(String(250))
    email = Column(String(250))
    netid = Column(String(250))
    password = Column(String(250))
    participation = Column(JSON)
    grades = Column(JSON)
    config = Column(JSON)
    submissions=relationship('Submission',backref='user')

class Course(Base):
    __tablename__ = 'courses'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    coursename = Column(String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = Column(Integer)
    term = Column(String(250)) #F=Fall, S=Spring, U=Summer
    coursenumber = Column(String(250))
    uvm_course = Column(Integer)
    zulipurl = Column(String(250))
    zuliprc = Column(String(250))
    homepage = Column(String(250))
    size = Column(Integer)
    #users=relationship('Users',back_populates='courses')
    #problems=relationship('Problem',back_populates='course')
    problems=relationship('Problem',backref='course')
    
class Problem(Base):
    __tablename__ = 'problems'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    coursename = Column(String(250)) #algebra-one, algebraic-topology, agittoc1, agittoc2, agittoc3
    year = Column(Integer)
    term = Column(String(250)) #F=Fall, S=Spring, U=Summer
    assignment = Column(String(250))
    problem = Column(String(250))
    references = Column(JSON)
    due_date = Column(Integer)
    hints = Column(String(1000))
    locked = Column(Integer)
    datasets = Column(JSON)
    submissions=relationship('Submission',backref='prob')
    course_id=Column(Integer,ForeignKey('courses.id'))
    description = Column(String(1000))
    #course=relationship('Course',back_populates='problems')
    
class Submission(Base):
    __tablename__ = 'submissions'
    __table_args__ = {'extend_existing': True}
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    coursename = Column(String)
    year = Column(Integer)
    term = Column(Integer)
    submission_number = Column(Integer)
    submission_locked = Column(Integer)
    netid = Column(String(250))
    email = Column(String(250))
    assignment = Column(String(250))
    problem = Column(String(250))
    closed = Column(Integer)
    submission_time = Column(Integer)
    total_score1 = Column(Float)
    total_score2 = Column(Float)
    reviewer1_assignment_time =Column(Integer)
    reviewer1 = Column(String(250))
    reviewer1_email = Column(String(250))
    reviewer1_score = Column(Integer)
    review1 = Column(String(1000))
    review1_timestamp = Column(Integer)
    review1_locked = Column(Integer)
    reviewer2_assignment_time=Column(Integer)
    reviewer2 = Column(String(250))
    reviewer2_email = Column(String(250))
    reviewer2_score = Column(Integer)
    review2 = Column(String(1000))
    review2_timestamp = Column(Integer)
    review2_locked = Column(Integer)
    new_submission = Column(Integer)
    new_match = Column(Integer)
    new_review1 = Column(Integer)
    new_review2 = Column(Integer)
    new_completion = Column(Integer)
    bad1 = Column(Integer)
    bad2 = Column(Integer)
    data = Column(LargeBinary)
    w1 = Column(Float)
    w2 = Column(Float)
    user_id = Column(Integer,ForeignKey('users.id'))
    #user = relationship('User',back_populates='submissions')
    prob_id = Column(Integer,ForeignKey('problems.id'))
    #prob = relationship('Problem',back_populates='submissions')
 
#Create an engine that stores data in the local directory's
#sqlalchemy_example.db file.
#engine = create_engine('sqlite:///flaskpage_database.db')
engine = create_engine('sqlite:///db.sqlite')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
