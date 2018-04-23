from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'bloggin'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog, owner):
        self.title = title
        self.blog = blog
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, user, password):
        self.user = user
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index', 'user']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(user=username).first()
        if user and not user.password == password:
            flash('Incorrect password, please try again.', 'error')
            return render_template('login.html', username=username)
        if not user:
            flash('User does not exist.', 'error')
            return render_template('login.html')
        if user and user.password == password:
            session['user'] = user.user
            flash("Logged in")
            return redirect('/newpost')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ""
        password_error = ""
        verify_error = ""
        good_username = True
        good_password = True
        good_verify = True
        existing_user = User.query.filter_by(user=username).first()
        if username == "":
            username_error = "Please enter a username"
            good_username = False
        else:
            if len(username) < 3:
                username = ""
                username_error = "Username cannot be less than 3 characters."
                good_username = False
        if password == "":
            password_error = "Please enter a password"
            good_password = False
        else:
            if len(password) < 3:
                password_error = "Password cannot be less than 3 characters."
                good_password = False
        if verify == "":
            verify_error = "Please reenter your password"
            good_verify = False
        if existing_user:
            username_error = 'User already exists'
            good_username = False
        if not password == verify:
            verify_error = "Password inputs do not match. Please try again."
            good_verify = False
        if good_username and good_password and good_verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(user=username).first()
            session['user'] = user.user
            return redirect('/newpost')
        else:
            return render_template("signup.html", username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)
    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    page_title = 'Add a Blog Entry'
    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']
        owner = User.query.filter_by(user=session['user']).first()
        if title == '' or blog == '':
            flash("You can't post empty fields. Please try again", "error")
            return render_template('new-post.html', page_title=page_title)
        else:
            new_blog = Blog(title, blog, owner)
            db.session.add(new_blog)
            db.session.commit()
            view_post = Blog.query.filter_by(title=title).first()
            blog_id = str(view_post.id)
            return redirect('/blog?id=' + blog_id)        
    return render_template('new-post.html', page_title=page_title)

@app.route('/blog', methods=['GET', 'POST'])
def list_blogs():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    users = User.query.all()
    if blog_id:
        entry = Blog.query.filter_by(id=blog_id).first()
        author = User.query.filter_by(id=entry.owner_id).first()
        return render_template('view-post.html', page_title=entry.title, entry=entry, author=author)
    return render_template('list-blogs.html', blogs=blogs, users=users, page_title='blogs!')

@app.route('/user', methods=['GET'])
def user():
    user_id = request.args.get('id')
    user = User.query.filter_by(id=user_id).first()
    blogs = Blog.query.filter_by(owner_id=user.id).all()
    return render_template('singleUser.html', page_title=user.user, blogs=blogs)

@app.route('/', methods=['GET'])
def index():
    page_title = 'blog users!'
    users = User.query.all()
    return render_template('index.html', page_title=page_title, users=users)



if __name__ == '__main__':
    app.run()