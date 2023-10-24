from flask import Flask, redirect, render_template, request, flash, session
from forms import SignUpForm, SignInForm, TaskForm, ProjectForm,SearchForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY']='Khang Python-Flask Web App'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'app.db')

app.config['SQLITECHEMY_TRACK_MODIFICATIONS']=False
app.app_context().push() 

db=SQLAlchemy(app)
migrate=Migrate(app,db)

import models
@app.route('/')

def main():
    todolist=[
        {
            'name': 'Buy milk',
            'description': 'Buy 2 liters of milk in Coompart.'
        },
        {
            'name': 'Get money',
            'description': 'Get 500k from ATM'
        }
    ]
    return render_template('index.html', todolist=todolist)

@app.route('/signUp', methods=['GET', 'POST'])
def showSignUp():
    form=SignUpForm()

    if form.validate_on_submit():
    # if request.method=='POST':
        print("Validate on submit")
        _fname=form.inputFirstName.data
        _lname=form.inputLastName.data
        _email=form.inputEmail.data
        _password=form.inputPassword.data
        # _name=request.form['inputName']
        # _email=request.form['inputEmail']
        # _password=request.form['inputPassword']

        # user={'fname':_fname,'lname':_lname, 'email':_email,'password':_password}
        if(db.session.query(models.User).filter_by(email=_email).count()==0):
            user=models.User(first_name=_fname,last_name=_lname, email=_email)
            user.set_password(_password)
            db.session.add(user)
            db.session.commit()
            return render_template('signUpSuccess.html', user=user)
        else:
            flash('Email {} is already exsits!'.format(_email))
            return render_template('signup.html',form=form)
    # return render_template('index.html')
    # return render_template('signup.html')
    print("Not validate on submit")
    return render_template('signup.html', form = form)

@app.route('/signIn',methods=['GET','POST'])
def signIn():
    form=SignInForm()
    if form.validate_on_submit():
        _email=form.inputEmail.data
        _password=form.inputPassword.data

        user=db.session.query(models.User).filter_by(email=_email).first()
        if(user is None):
            flash('Wrong email address or password!')
        else:
            if(user.check_password(_password)):
                session['user']=user.user_id
                # return render_template('userhome.html')
                return redirect('/userHome')
            else:
                flash('Wrong email address or password')
    return render_template('signin.html', form=form)


from forms import SearchForm  # Import form

@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    _user_id = session.get('user')
    form = SearchForm()  # Create an instance of the search form

    if form.validate_on_submit():  # Check if the form is submitted
        search_query = form.search_query.data  # Get the search query
        projects = db.session.query(models.Project).filter(
            (models.Project.name.contains(search_query)) |
            (models.Project.description.contains(search_query))
        ).all()
        tasks = db.session.query(models.Task).filter(
            (models.Task.description.contains(search_query))
        ).all()
    else:
        projects = db.session.query(models.Project).all()
        tasks = db.session.query(models.Task).all()

    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        return render_template('userhome.html', user=user, projects=projects, tasks=tasks, form=form)
    else:
        return redirect('/')



@app.route('/logOut',methods=['GET','POST'])
def logOut():
    session.pop('user', None)
    return redirect('/userHome')

# @app.route('/newTask',methods=['GET','POST'])
# def newTask():
#     a_user_id=session.get('user')
#     form=TaskForm()
#     form.inputProjectName.choices=[(p.project_id, p.name) for p in db.session.query(models.Project).all()]
#     form.inputPriority.choices=[(p.priority_id,p.text) for p in db.session.query(models.Priority).all()]
#     form.inputStatus.choices=[(p.status_id,p.description) for p in db.session.query(models.Status).all()]
@app.route('/newTask', methods=['GET', 'POST'])
def newTask():
    a_user_id = session.get('user')
    form = TaskForm()
    form.inputProjectName.choices=[(p.project_id, p.name) for p in db.session.query(models.Project).all()]
    form.inputPriority.choices=[(p.priority_id,p.text) for p in db.session.query(models.Priority).all()]
    form.inputStatus.choices=[(p.status_id,p.description) for p in db.session.query(models.Status).all()]
    statuses = db.session.query(models.Status).all()
    form.set_status_choices(statuses)


    if a_user_id:
        user=db.session.query(models.User).filter_by(user_id=a_user_id).first()
        
        if form.validate_on_submit():
            _description=form.inputDescription.data
            _priority_id=form.inputPriority.data
            _deadline=form.inputDeadline.data
            _project_id=form.inputProjectName.data
            _status_id=form.inputStatus.data
            priority=db.session.query(models.Priority).filter_by(priority_id=_priority_id).first()
            project=db.session.query(models.Project).filter_by(project_id=_project_id).first()
            status=db.session.query(models.Project).filter_by(status_id=_status_id).first()
            _task_id=request.form['hiddenTaskId']
            if project and _deadline > project.deadline:
                flash("Deadline of the task cannot be later than the project's deadline.", "error")
                return render_template('/newTask.html', form=form, user=user)
            if (_task_id=="0"):
                task=models.Task(description=_description, priority=priority, deadline=_deadline, project=project,status=status)
                db.session.add(task)
            else:
                task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
                task.description=_description
                task.priority=priority
                task.deadline=_deadline

            db.session.commit()
            return redirect('/userHome')
        return render_template('/newTask.html', form=form, user=user)
    return redirect('/')

@app.route('/deleteTask', methods=['GET','POST'])
def deleteTask():
    _user_id=session.get('user')
    if _user_id:
        _task_id=request.form['hiddenTaskId']
        if _task_id:
            task=db.session.query(models.Task).filter_by(task_id=_task_id).first()
            db.session.delete(task)
            db.session.commit()
        return redirect('/userHome')
    return redirect('/')

@app.route('/editTask', methods=['GET', 'POST'])
def editTask():
    _user_id = session.get('user')
    form = TaskForm()
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]

    if _user_id:
        _task_id = request.form['hiddenTaskId']
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
            if task:
                if task.completed:
                    # If the task is already completed, set it as not completed
                    task.completed = False
                else:
                    # If the task is not completed, set it as completed
                    task.completed = True

                db.session.commit()
            if form.validate_on_submit():
                _status_id = form.inputStatus.data
                status = db.session.query(models.Status).filter_by(status_id=_status_id).first()
                
                if status:
                    task.status = status

                    # Check if all tasks in the project are completed
                    project = task.project
                    if all(task.status_id == 3 for task in project.tasks):
                        project.status_id = 3  # Set project status to "Completed"
                    elif any(task.status_id == 1 for task in project.tasks):
                        project.status_id = 1  # Set project status to "In Progress"
                    else:
                        project.status_id = 2  # Set project status to "Not Started"

                    db.session.commit()
                    return redirect('/userHome')
                else:
                    flash('Invalid status selected.')
                    return redirect('/editTask', task=task, form=form)

            return render_template('/newTask.html', form=form, task=task)
        else:
            flash('Invalid task selected.')
            return redirect('/userHome')

    return redirect('/')

@app.route('/doneTask', methods=['POST'])
def doneTask():
    _user_id = session.get('user')
    _task_id = request.form.get('hiddenTaskId')
    if _user_id and _task_id:
        task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
        if task:
            task.status_id = 3  # Set task status to "Done"

            # Check if all tasks in the project are completed
            project = task.project
            if all(t.status_id == 3 for t in project.tasks):
                project.status_id = 3  # Set project status to "Completed"
            elif any(t.status_id == 1 for t in project.tasks):
                project.status_id = 1  # Set project status to "In Progress"
            else:
                project.status_id = 2  # Set project status to "Not Started"

            db.session.commit()

    return redirect('/userHome')


@app.route('/newProject',methods=['GET','POST'])
def newProject():
    a_user_id=session.get('user')
    form=ProjectForm()
    form.inputStatus.choices=[(s.status_id,s.description) for s in db.session.query(models.Status).all()]
    if a_user_id:
        user=db.session.query(models.User).filter_by(user_id=a_user_id).first()
        
        if form.validate_on_submit():
            _name=form.inputName.data
            _description=form.inputDescription.data
            _deadline=form.inputDeadline.data
            _status_id=form.inputStatus.data
            status=db.session.query(models.Status).filter_by(status_id=_status_id).first()

            _project_id=request.form['hiddenProjectId']
            if (_project_id=="0"):
                project=models.Project(name=_name, description=_description,deadline=_deadline, user=user, status=status)
                db.session.add(project)
            else:
                project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                project.name=_name
                project.description=_description
                project.status=status

            db.session.commit()
            return redirect('/userHome')
        return render_template('/newProject.html', form=form, user=user)
    return redirect('/')

@app.route('/deleteProject', methods=['GET','POST'])
def deleteProject():
    _user_id=session.get('user')
    if _user_id:
        _project_id=request.form['hiddenProjectId']
        if _project_id:
            project=db.session.query(models.Project).filter_by(project_id=_project_id).first()
            db.session.delete(project)
            db.session.commit()
        return redirect('/userHome')
    return redirect('/')

@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id=session.get('user')
    form=ProjectForm()
    form.inputStatus.choices=[(p.status_id, p.description) for p in db.session.query(models.Status).all()]
    if _user_id:
        _project_id=request.form['hiddenProjectId']
        if _project_id:
            project=db.session.query(models.Project).filter_by(project_id=_project_id).first()
            form.inputName.default=project.name
            form.inputDescription.default=project.description
            form.inputDeadline.default=project.deadline
            form.inputStatus.default=project.status_id
            form.process()
            return render_template('/newProject.html', form=form, project=project, user=_user_id)
    return redirect('/')
@app.route('/searchProjects', methods=['POST'])
def searchProjects():
    status_filter = request.form.get('searchProjectStatus')
    name_filter = request.form.get('searchProjectName')

    # Query your database based on the filters
    # Example:
    projects = db.session.query(models.Project).filter(
        (models.Project.name.contains(name_filter) if name_filter else True) &
        (models.Project.status_id == status_filter if status_filter else True)
    ).all()

    return render_template('userhome.html', user=user, projects=projects)


if __name__=='__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)

