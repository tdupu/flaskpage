# Schema

This file provides documentation on the underlying schema; try to keep it up to date if you make changes.

## roster
			
Column                | Type        |  Notes
----------------------|-------------|-------
id                    |	bigint      | unique identifier automatically assigned by postgres (not MIT id)
departments           | text[]      | List of course_numbers in departments table, e.g. ["18"] or ["6","18"]
description           |	text	    | Student's public description of themself (not currently used)
email	              | text	    | smith@gmail.com (not currently used, we just email kerb@mit.edu)
gender                | text        | optional, currently female, male, or non-binary (optional)
hours                 | boolean[]   | a list of 7x24=168 booleans indicating hours available to pset (in timezone)
location              | text        | currently near or far (but will eventually include dorms, ILGs, etc...
name                  |	text        | e.g. Johnathan Smith
preferred_name        | text        | e.g. John Smith
preferred_pronouns    | text	    | e.g. they/them
preferences           |	jsonb	    | dictionary of preferences (see Preferences tab)
strengths             | jsonb       | dictionary of preference strength (values are integers from 0 to 10)
timezone              |	text	    | ('MIT' means MIT's timezone, America/NewYork)
year                  | smallint    | 1=frosh, 2=soph, 3=junior, 4=senior/super-senior, 5=graduate student
blocked_student_ids   | bigint[]    | list of student ids this student will never be put in a group with
			
## submissions

Column                | Type        |  Notes
----------------------|-------------|-------
id                    |	bigint      | unique identifier automatically assigned by postgres
class_id	      | bigint	    | id in classes table
class_number	      | text        | class number (e.g. "18.701")
year                  | smallint    | year of class (e.g. 2020)
term                  | smallint    | term of class (e.g. 3 = Fall)
group_name            | text	    | custom name, editable by anyone in group
visibility            | smallint    | 0=invitation, 1=permission, 2=automatic, 3=public
preferences	      | jsonb       | optional group preferences; if unspecified, system constructs something from member preferences
strengths             | jsonb       | preference strengths
creator               | text        | kerb of the student who created the group, empty string for system created groups
editors               | text[]      | list of kerbs of students authorized to modify the group (empty list means everyone)
size                  | smallint    | number of rows in grouplist with group_id=id (read/write ratio is high, so worth maintaining)
max                   | smallint    | maximum number of students (None if no limit, may be less than size due to edits)
match_run             | smallint    | only set for system created groups (creator=''), incremented with each matching
request_id            | bigint      | id in request_table (if this is not None there is a pending request and we should not make another)

## problems

Column                | Type        |  Notes
----------------------|-------------|-------
id                    |	bigint      | unique identifier automatically assigned by postgres
timestamp             | timestamp   | timestamp of request (in MIT time, no timezone)
group_id              | bigint      | id of group to whom reqeust was made
student_id            | bigint      | id of student on whose behalf the request was made
kerb                  | text        | kerberos id of student on whose behalf the request was made
