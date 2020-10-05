# Schema

  
This file provides documentation on the underlying schema; try to keep it up to date if you make changes.

  
## roster

Column  | Type  |  Notes
------|-------------|-------
id  | bigint  | unique identifier automatically assigned by postgres
pronoun | text | 
name | text | 
uvm_student | int | 1 if yes, 0 if no
student_id | int | 0 if not a UVM student
class | text | 
major | text |
degree | text |
credits | int | 
reg_status | text | 
reg_data | text | 
email | text | email of the user
netid | text | uvm netid, no spaces, empty if not a uvm student   
password| text | sha256 hashed password
  

## courses
Column  | Type  |  Notes
----------------------|-------------|-------
id  | bigint  | unique identifier automatically assigned by postgres
class_name  | text  | Course name, e.g. Algebra I
class_number  | text  | Course number, e.g. 18.701
UVM  | smallint  | 0 if UVM course, 1 if not UVM course
year  | smallint  | Calendar year
term  | smallint  | Encoding of semester 0=IAP, 
zulipurl  | text  | webpage to zulip
zuliprc  | text  | code for a bot in the course
homepage  | text  | course homepage
size  | smallint  | number of rows in classlist with class_id = id (read/write ratio is high, so worth maintaining)
problems | json | a python dictionary whose keys are strings [assignment, problem] and whose values are integers


  

## submissions
Column  | Type  |  Notes
----------------------|-------------|-------
id  |  bigint  | unique identifier automatically assigned by SQLAlchemy 
courseid | int | the database id number of the associated course   
submission_number| int | order of the submission for the course
submission_locked | int | 1 if locked, 0 if not
netid | text | uvm netid, if student is a UVM student
assignment| text | which group of problems this is in 
problem | text | the particular problem
closed | int | 1 if closed, 0 if not
submission_time | int | unix timestamp for the submission
total_score1 | double | first score based on initial review  
total_score2 | double | second score based on initial review
reviewer1_assignment_time | int | unix timestamp when the first reviewer was matched, -1 if not assigned
reviewer1 | text | netid or email of first reviewer 
reviewer1_score | int | a number between 0 and 10, -1 if not assigned
review1 | text | feedback from reviewer
review1_timestamp | int | unix time of review
review1_locked | int | 1 if yes, 0 if no 
reviewer2_assignment_time | int | unix timestamp when the second reviewer was matched, -1 if not assigned
reviewer2 | text | netid or email of second reviewer 
reviewer2_score | int | a number between 0 and 10, -1 if not assigned
review2 | text | feedback from reviewer
review2_timestamp | int | unix time of review
review2_locked | int | 1 if yes, 0 if no 
new_submission | int | 1 if yes, 0 if no 
new_match | int | 1 if yes, 0 if no
new_review1 | int | 1 if yes, 0 if no
new_review2 | int | 1 if yes, 0 if no
new_completion | in | 1 if yes, 0 if no
