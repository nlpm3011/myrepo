from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired


class SignUpForm(FlaskForm):
    inputFirstName = StringField('First Name',
        [DataRequired(message="Please enter your first name!")])
    inputLastName = StringField('Last Name',
        [DataRequired(message="Please enter your last name!")])
    inputEmail = StringField('Email address',
        [Email(message="Not a valid email address!"),
        DataRequired(message="Please enter your email address!")])
    inputPassword = StringField('Password',
        [InputRequired(message="Please enter your password!"),
        EqualTo('inputConfirmPassword', message="Passwords does not match!")])
    inputConfirmPassword=PasswordField('Confirm password')
    # inputName = StringField()
    # inputEmail = StringField()
    # inputPassword = PasswordField()
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    inputEmail=StringField('Email addrress',
        [Email(message="Not a valid email address!"),
        DataRequired(message="Please enter your email address!")])
    inputPassword=PasswordField('Password',
        [InputRequired(message="Please enter your password!")])
    submit=SubmitField('Sign in')

class TaskForm(FlaskForm):
    inputDescription=StringField('Task Description',
        [DataRequired(message="Please enter your task content!")])
    inputPriority=SelectField('Priority', coerce=int)
    inputProjectName = SelectField('Project', coerce=int)
    inputStatus = SelectField('Status', coerce=int)
    inputStatusRO = StringField('inputStatus')
    inputDeadline = DateTimeLocalField('Project Deadline', format='%Y-%m-%dT%H:%M', 
        validators=[DataRequired(message="Please select a valid deadline")])
    submit1=SubmitField('Create Task')
    submit2=SubmitField('Edit Task')
    def set_status_choices(self, statuses):
        self.inputStatus.choices = [(status.status_id, status.description) for status in statuses]

class ProjectForm(FlaskForm):
    inputName=StringField('Project Name',
        [DataRequired(message="Please enter your project name!")])
    inputDescription=StringField('Project Description',
        [DataRequired(message="Please enter your project description!")])
    inputDeadline = DateTimeLocalField('Project Deadline', format='%Y-%m-%dT%H:%M', 
        validators=[DataRequired(message="Please select a valid deadline")])
    inputStatus=SelectField('Status', coerce=int)
    
    submit=SubmitField('Create Project')
    
class SearchForm(FlaskForm):
    search_query = StringField('Search by Name or Description')
    submit = SubmitField('Search')


