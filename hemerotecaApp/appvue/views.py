from flask import Blueprint, render_template

appvue = Blueprint('appvue',__name__)

@appvue.route('/')
def base():
   return render_template('appvue/frontPage.html')