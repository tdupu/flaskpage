from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user



grade = Blueprint('grade', __name__)


@grade.route('/grades', methods=['GET'])
@login_required
def grades():
    my_user=current_user
    return "grades"

