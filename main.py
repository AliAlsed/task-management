from flask import Flask, render_template, request, redirect, url_for, session

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import RollbackToSavepointClause


# engine = create_engine('mysql+pymysql://root:@localhost/tasks')
engine = create_engine('sqlite:///college.db')
meta = MetaData()
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tasks = relationship("Task")
    name = Column('name', String(50))
    password = Column('password', String(50))
    email = Column('email', String(50))
    phone = Column('phone', String(50))
    position = Column('position', String(50))
    department = Column('department', String(50))
    role = Column('role', String(50))


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column('name', String(50))
    description = Column('description', String(60))
    # progress = Column('progress', String(30))
    # status = Column('status', String(50))
    # due_date = Column('due_date', String(30))
    # task_type = Column('task_type', String(30))
    # assigned_to = Column('assigned_to', String(50))
    # actual_days = Column('actual_days', Integer)
    # link = Column('link', String(50))


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    title = Column('title', String(50))
    description = Column('description', String(60))


Base.metadata.create_all(engine)
db_session = sessionmaker()
db_session.configure(bind=engine)
Base.metadata.create_all(engine)

app = Flask(__name__)

app.secret_key = 'aliprog96'


# seeding if no admin
s = db_session()
admin = s.query(User).filter(
    User.name == "admin" and User.password == "admin").all()
if len(admin) == 0:
    admin = User(name="admin", password="admin", email="",
                 phone="", position="admin", department="it", role="admin")
    s.add(admin)
    s.commit()


@app.route('/')
def home():
    if 'loggedin' in session:
        if session['role'] == "admin":
            s = db_session()
            users = s.query(User).filter().all()
            return render_template('admin.html', users=users)
        else:
            s = db_session()
            users = s.query(User).filter(
                User.id == session['id']).all()
            if len(users) > 0:
                return render_template('index.html', user=users[0])
            else:
                return render_template('login.html')

    else:
        print("not")
        return render_template('login.html')


@app.route('/main', methods=['POST', 'GET'])
def main():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        print(request.form['username'])

        username = request.form['username']
        password = request.form['password']
        s = db_session()
        users = s.query(User).filter(
            User.name == username and User.password == password).all()
        print(users)
        if len(users) > 0:
            session['loggedin'] = True
            session['username'] = users[0].name
            session['id'] = users[0].id
            session['role'] = users[0].role

    return redirect(url_for('home'))


@app.route('/users')
def users_add():
    return render_template('users.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/users', methods=['POST'])
def users_insert():
    if request.method == "POST":
        name = request.form['name']
        password = str(request.form['password'])
        email = request.form['email']
        phone = str(request.form['phone'])
        position = request.form['position']
        department = request.form['department']
        user = User(name=name, password=password, email=email,
                    phone=phone, position=position, department=department, role="user")
        s = db_session()
        s.add(user)
        s.commit()
        print(user)
    return render_template('users.html')


@app.route('/tasks/del/<id>', methods=['GET'])
def delete_task(id):
    s = db_session()
    task = s.query(Task).filter(
        Task.id == id).all()[0]
    s.delete(task)
    s.commit()
    return redirect(url_for('home'))


@app.route('/tasks/<uid>')
def tasks_add(uid):
    return render_template('tasks.html')


@app.route('/tasks/<uid>', methods=['POST'])
def tasks_insert(uid):
    if request.method == "POST":
        name = request.form['name']
        description = str(request.form['desc'])
        task = Task(name=name, description=description, user_id=uid)
        s = db_session()
        s.add(task)
        s.commit()
        print(task)
    return redirect(url_for('home'))


@app.route('/course')
def course_index():
    return render_template('course.html')


@app.route('/course', methods=['POST'])
def course_create():
    title = request.form['title']
    description = request.form['description']
    course = Course(title=title, description=description)
    s = db_session()
    s.add(course)
    s.commit()
    print('add')
    return render_template('course.html')


@app.route('/allcourse')
def course_all():
    s = db_session()
    courses = s.query(Course).filter().all()
    print(courses)
    return render_template('courses.html', all_course=courses)


if __name__ == "__main__":
    app.run(debug=True)
