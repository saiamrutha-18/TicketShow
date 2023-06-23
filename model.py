from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,logout_user,login_required,LoginManager,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from datetime import datetime,time,date


db=SQLAlchemy()
class User(db.Model,UserMixin):
    id =db.Column(db.Integer,primary_key=True)
    username =db.Column(db.String(20), nullable=False,unique=True)
    password =db.Column(db.String(50), nullable=False)
    role=db.Column(db.String(50),default='user')

    def get_id(self):
        return (self.id)
    def get_role(self):
        if self.role=='admin':
            return True
        return False


class RegistrationForm(FlaskForm):
    username = StringField( validators=[InputRequired(),Length(min=3, max=10)],render_kw={"placeholder":"username"})
    password=PasswordField( validators=[InputRequired(),Length(min=5, max=10)],render_kw={"placeholder":"password"})
    submit=SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField( validators=[InputRequired(),Length(min=3, max=10)],render_kw={"placeholder":"username"})
    password=PasswordField( validators=[InputRequired(),Length(min=5, max=10)],render_kw={"placeholder":"password"})
    submit=SubmitField('Login')

class AdminLoginForm(FlaskForm):
    username = StringField( validators=[InputRequired(),Length(min=3, max=10)],render_kw={"placeholder":"username"})
    password=PasswordField( validators=[InputRequired(),Length(min=5, max=10)],render_kw={"placeholder":"password"})
    submit=SubmitField('Login')

class Venues(db.Model):
    venue_id= db.Column(db.Integer,primary_key=True)
    venue_name =db.Column(db.String(20), nullable=False)
    place = db.Column(db.String(20), nullable=False)
    location= db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    s_rel=db.relationship('Shows',secondary="venue_shows",backref='venues',cascade="all,delete")
    
    def __repr__(self):
        return f'<Venues: {self.name}>'

class Shows(db.Model):
    show_id= db.Column(db.Integer,primary_key=True)
    show_name =db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    start_timing = db.Column(db.Time, nullable=False)
    end_timing = db.Column(db.Time, nullable=False)
    tags =db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    v_rel=db.relationship('Venues',secondary="venue_shows",backref='shows')
    svenue_id = db.Column(db.Integer(), db.ForeignKey('venues.venue_id'))

    def __repr__(self):
        return f'<Shows: {self.name}>'
    
class Venue_shows (db.Model):
    venue_id=db.Column(db.Integer,db.ForeignKey("venues.venue_id"),primary_key=True)
    show_id=db.Column(db.Integer,db.ForeignKey("shows.show_id"),primary_key=True)
    

class Bookings(db.Model):
    bk_id = db.Column(db.Integer(), primary_key = True)
    bkuser_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    bkvenue_id = db.Column(db.Integer(), db.ForeignKey('venues.venue_id'))
    bkshow_id = db.Column(db.Integer(), db.ForeignKey('shows.show_id'))
    bkvenue_name=db.Column(db.String(20), nullable=False)
    bkshow_name=db.Column(db.String(20), nullable=False)
    bkshow_stiming=db.Column(db.Time, nullable=False)
    bkshow_etiming=db.Column(db.Time, nullable=False)
    n_tickets = db.Column(db.Integer(), nullable = False)
    tot_price = db.Column(db.Integer(), nullable = False)
    

    def __repr__(self):
        return "<Bookings %r%r%r>" % self.venue_id % self.show_id % self.book


