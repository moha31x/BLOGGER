from flask import flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, current_user
from app import db, login, admin

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)	

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.now)
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)	

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def my_posts(self):
		own = Post.query.filter_by(user_id=self.id)
		return own.order_by(Post.timestamp.desc())

	def other_posts(self):
		their = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		return their.order_by(Post.timestamp.desc())		

	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())			

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Post {}>'.format(self.content)


class MyModelView(ModelView):
    def is_accessible(self):
        if current_user == User.query.get(1):
            flash('Welcome back Admin!')
            return True
        else:
            abort(403)
            return False
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))    

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Post, db.session))		