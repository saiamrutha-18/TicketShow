from flask import Flask ,render_template,url_for,redirect ,request,send_file,flash
from flask_bcrypt import Bcrypt
from model import *
from flask_cors import CORS
from resources import *
import matplotlib.pyplot as plt
import io
import matplotlib
matplotlib.use('Agg')

app=Flask(__name__)
CORS(app)
api.init_app(app)
parser=reqparse.RequestParser()
parser.add_argument('ven_name')
db.init_app(app)
app.app_context().push()

bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SECRET_KEY']='secretkey'

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view ='login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return render_template('homepg.html')

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect('/booking_shows/'+str(user.id))
    return render_template('loginpg.html',form=form)

@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    form=AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data =='admin' and form.password.data=='admin':
            user=User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                    login_user(user)
                    return redirect(url_for('all_shows'))
            else:
                hashed_pwd= bcrypt.generate_password_hash(form.password.data)
                admin_obj=User(username=form.username.data,password=hashed_pwd,role='admin')
                db.session.add(admin_obj)
                db.session.commit()
                obj=User.query.filter_by(username=form.username.data).first()
                login_user(obj)
                return redirect(url_for('all_shows'))
        else:
            flash("Improper admin credentials,enter correct username and password!")
            return render_template('notadmin.html')
    return render_template('adminloginpg.html',form=form)



@app.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd= bcrypt.generate_password_hash(form.password.data)
        user_obj=User(username=form.username.data,password=hashed_pwd)
        db.session.add(user_obj)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registerpg.html',form=form)


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/all_venues_shows', methods=['GET', 'POST'])
@login_required
def all_shows():
    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    if request.method=='GET':
        shows = Shows.query.all()
        venues = Venues.query.all()
        return render_template('venue_show.html', shows=shows, venues=venues, search=None)
    if request.method == 'POST':
        shows = Shows.query.all()
        search = request.form.get('search')
        query = (f"%{search}%")
        res = Venues.query.filter(Venues.venue_name.like(query)).all()
        return render_template("venue_show.html", search=search, shows=shows, venues=res)       


@app.route('/booking_shows/<int:id>',methods=['GET','POST'])
@login_required
def booking_pg(id):
    usr=User.query.get(id)
    shows = Shows.query.all()
    if request.method=='GET':
        venues = Venues.query.all()
        return render_template('book_tick.html',search=None,user=usr,shows=shows,venues=venues)
    if request.method=='POST':
        search = request.form.get('search')
        query = (f"%{search}%")
        res = Venues.query.filter(Venues.venue_name.like(query)).all()
        return render_template('book_tick.html',search=search,user=usr,shows=shows,venues=res)



@app.route('/booking_shows/usr/<int:id>/venue/<int:venue_id>/show/<int:show_id>',methods=['GET','POST'])
@login_required
def book(id,venue_id,show_id):
    u=User.query.get_or_404(id)
    v=Venues.query.get_or_404(venue_id)
    s=Shows.query.get_or_404(show_id) 
    bookings = Bookings.query.filter_by(bkvenue_id=venue_id, bkshow_id=show_id).all()
    tick_booked=0
    for book in bookings:
        tick_booked+=book.n_tickets 
    seats_avail=(v.capacity //len(v.s_rel) )-tick_booked
    if request.method=='GET':             
        return render_template('booking_form.html',seats_avail=seats_avail,user=u,show=s,venue=v)
    if request.method=='POST':
        n_tick=request.form.get('n_tickets')
        if seats_avail >=int(n_tick):
            seats_avail-=int(n_tick)                              
            user_bk=Bookings(bkuser_id=u.id,bkvenue_id=v.venue_id,bkshow_id=s.show_id,bkvenue_name=v.venue_name,bkshow_name=s.show_name,bkshow_stiming=s.start_timing,bkshow_etiming=s.end_timing,n_tickets=request.form.get('n_tickets'),tot_price=request.form.get('tot'))
            db.session.add(user_bk)
            db.session.commit()
        else:
            flash("insufficient seats")
            return render_template('insuffseats.html')
        return redirect('/usr_bookings/'+str(id))
        
@app.route('/usr_bookings/<int:id>',methods=['POST','GET'])
@login_required
def user_bookings(id):
   
    if request.method=='GET':
        bk_obj_list=Bookings.query.filter_by(bkuser_id=id).all()
        return render_template('all_bookings.html',bobjs = bk_obj_list,search=None,id=id)
    if request.method=='POST':
        search = request.form.get('search')
        query = (f"%{search}%")
        res = Bookings.query.filter(Bookings.bkvenue_name.like(query)).all() 
        return render_template('all_bookings.html',bobjs=res,search=search,id=id)

@app.route('/assign/add_show/<int:id>',methods=['POST','GET'])
@login_required
def add_show(id):
    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    v1 = Venues.query.get(id)
    if request.method == 'GET':
        return render_template('add_show_form.html',v1=v1)
    if request.method == 'POST':
        s_name = request.form.get('s_name')
        s_rating= request.form.get('s_rating')
        s_timing = datetime.strptime(request.form.get('s_timing'), '%H:%M').time()
        e_timing = datetime.strptime(request.form.get('e_timing'), '%H:%M').time()
        s_tags = request.form.get('s_tags')
        s_price = request.form.get('s_price')
        sv_id=v1.venue_id
        s1 = Shows(show_name=s_name,rating=s_rating,start_timing=s_timing,end_timing=e_timing,tags=s_tags,price=s_price,svenue_id=sv_id)
        db.session.add(s1)
        db.session.commit()
        shows=Shows.query.all()
        return render_template('assign_show.html',shows=shows,v1=v1)
        

@app.route('/add_venue',methods=['POST','GET'])
@login_required
def add_venue():

    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('add_venue_form.html')
    if request.method == 'POST':
        v_name = request.form.get('v_name')
        v_place = request.form.get('v_place')
        v_loc = request.form.get('v_loc')
        v_cap = request.form.get('v_cap')
        v1 = Venues(venue_name=v_name,place=v_place,location=v_loc,capacity=v_cap)
        db.session.add(v1)
        db.session.commit()
        return redirect('/all_venues_shows') 



@app.route('/assign/<int:id>',methods=['POST','GET'])
@login_required
def assign(id):

    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    v1 = Venues.query.get(id)
    if request.method == 'GET':
        shows=Shows.query.all()
        return render_template('assign_show.html',shows=shows,v1=v1)
    if request.method == 'POST':
        s_id = request.form.get('s_id')
        show =Shows.query.get(int(s_id))
        v1.shows.append(show)        
        db.session.commit()
        return redirect('/all_venues_shows')


@app.route('/delete_venue/<int:id>')
@login_required
def delete_venue(id):

    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    try:
        venue_to_del=Venues.query.get_or_404(id)
        venue_shows_to_del = Venue_shows.query.filter_by(venue_id=id).all()
        for venue_show in venue_shows_to_del:
            db.session.delete(venue_show)
        db.session.delete(venue_to_del)
        db.session.commit()
        return redirect('/all_venues_shows')
    except:
        return "could not delete"


@app.route('/update_venue/<int:id>',methods=['POST','GET'])
@login_required
def update_venue(id):

    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    venue_obj=Venues.query.get_or_404(id)
    
    if request.method == 'POST':
        venue_obj.venue_name=request.form['v_name']
        venue_obj.place=request.form['v_place']
        venue_obj.location=request.form['v_loc']
        venue_obj.capacity=request.form['v_cap']
        try:
            db.session.commit()
            return redirect('/all_venues_shows')
        except:
            return 'could not update'
    else:
        return render_template('update_venue_form.html',venue=venue_obj)


@app.route('/venue/<int:venue_id>/show/<int:show_id>')
@login_required
def rem_show_from_venue(venue_id,show_id):
    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    v=Venues.query.get_or_404(venue_id)
    s=Shows.query.get_or_404(show_id)
    show_to_del= Venue_shows.query.filter_by(venue_id=v.venue_id,show_id=s.show_id).first()
    try:
        db.session.delete(show_to_del)
        db.session.commit()
        return redirect('/all_venues_shows')
    except:
        return "could not delete"


@app.route('/update_show/<int:id>',methods=['POST','GET'])
@login_required
def update_show(id):

    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    show_obj= Shows.query.get_or_404(id)
    if request.method == 'POST':
        try:
            show_obj.show_name=request.form['s_name']
            show_obj.rating=request.form['s_rating']
            show_obj.start_timing = datetime.strptime(request.form.get('s_timing'), '%H:%M:%S').time()
            show_obj.end_timing = datetime.strptime(request.form.get('e_timing'), '%H:%M:%S').time()
            show_obj.tags=request.form['s_tags']
            show_obj.price=request.form['s_price']
            db.session.commit()
            return redirect('/all_venues_shows')
        except:
            return 'could not update'
    else:
        return render_template('update_show_form.html',show=show_obj)


@app.route('/summary')
@login_required
def summary():
    currentuser = User.query.filter_by(id= current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    # Create a figure and axes
    fig,ax = plt.subplots()

    # Retrieve show names and ratings from the database and extract them
    shows = Shows.query.with_entities(Shows.show_name, Shows.rating).all()
    show_names = []
    ratings = []
    for show in shows:
        show_name = show[0]
        rating = float(show[1])
        show_names.append(show_name)
        ratings.append(rating)

    colors = ['#2196F3', '#4CAF50', '#FF5722', '#E91E63']

    # Create a bar plot of show ratings with custom colors
    ax.bar(show_names, ratings, color=colors)
    ax.set_title('Show Ratings')
    ax.set_xlabel('Shows')
    ax.set_ylabel('Rating')
    ax.set_ylim((0, 10))
    ax.grid(True)

    # Save the plot as a PNG image
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    # Return the image as a response
    return send_file(img, mimetype='image/png')


@app.route('/rating_page')
@login_required
def rating_page():
    currentuser = User.query.filter_by(id=current_user.id).first()
    if not currentuser.get_role():
        return redirect(url_for('login'))
    
    return render_template('summary.html')


if __name__ == "__main__":
    app.run(debug=True)