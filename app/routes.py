import os

from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import event, false, true
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, RegistrationForm, NewMemeForm, PhotoForm, SearchForm
from app.models import User, Meme, Location, Category, MemeToCategory
from flask_login import current_user, login_user, login_required, logout_user

app.config["IMAGE_UPLOADS"] = "/Users/Caitlyn/PycharmProjects/icmemes/app/static/img"


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        search = form.search.data
        return redirect(url_for('results', search=search))

    return render_template('index.html', title='Home', form=form)


@app.route('/results/<search>')
def results(search):
    mtc=[]
    memes = []
    category = Category.query.filter_by(name=search).first()
    if category:
        mtc = MemeToCategory.query.filter_by(category_id=category.id).all()
    else:
        location = Location.query.filter_by(name=search).first_or_404()
        memes = Meme.query.filter_by(location_id=location.id).all()

    return render_template('results.html', title="Results", category=category, mtc=mtc, memes=memes)


@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":

        if request.files:
            image = request.files["image"]
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            print("image saved")
            return redirect(request.url)

    return render_template("upload_image.html")


@app.route('/meme/<name>')
def meme(name):

    meme=Meme.query.filter_by(name=name).first()
    if meme is None:
        return render_template('404.html')

    mtc = MemeToCategory.query.filter_by(meme_id=meme.id).all()

    return render_template('meme.html', title="Meme", meme=meme, mtc=mtc)


@app.route('/memes')
def memes():

    memes = Meme.query.all()

    images = os.listdir('/Users/Caitlyn/PycharmProjects/icmemes/app/static/img')
    images = ['img/' + file for file in images]

    return render_template('memes.html', title="Memes", images=images, memes=memes)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = NewMemeForm()

    locationList = Location.query.all()
    form.location.choices = [(location.id, location.name) for location in locationList]

    categoriesList = Category.query.all()
    form.categories.choices = [(category.id, category.name) for category in categoriesList]

    if request.method == "POST":

        if request.files:
            image = request.files["image"]
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            print("image saved")
            # return redirect(request.url)

    if form.validate_on_submit():
        taken = false
        memecheck = Meme.query.all()
        for meme in memecheck:
            if meme.name == form.name.data:
                taken = true
        if taken == true:
            flash('Meme has already been submitted')
            return render_template("create.html", title="New Meme", form=form, )

        flash('New Event added: {}'.format(
            form.name.data))

        for l in locationList:
            if l.id == form.location.data:
                place = l.id

        newmemeentry = Meme(name=form.name.data, caption=form.caption.data, location_id=place, image_name="img/"+image.filename)
        db.session.add(newmemeentry)
        db.session.commit()

        memeList = Meme.query.all()

        for m in memeList:
            if m.name == form.name.data:
                currentEvent = m.id

        m2cList = MemeToCategory.query.all()
        idnum = 0
        for m in m2cList:
            if m.id > idnum:
                idnum = m.id
        idnum = idnum + 1

        for entry in form.categories.data:
            for c in categoriesList:
                if c.id == entry:
                    newmtoc = MemeToCategory(id=idnum, category_id=c.id, meme_id=currentEvent)
                    db.session.add(newmtoc)
                    db.session.commit()

    return render_template('create.html', title="Create", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
    # enter base information

    # User
    user1 = User(id=1, username="cfloyd", email="cfloyd@ithaca.edu")
    user1.set_password("a")
    db.session.add(user1)
    db.session.commit()

    # Memes
    meme1 = Meme(id=1, name="Homer Connect hurts", caption="shouldn't stress about next semester rn", location_id=3, image_name="img/icmeme1.jpg")
    db.session.add(meme1)
    meme2 = Meme(id=2, name="Winter is so great", caption="Winter is my favorite season", location_id=3, image_name="img/memetest.jpg")
    db.session.add(meme2)
    meme3 = Meme(id=3, name="Game of Thrones x Ithaca", caption="Freshmen better prepare", location_id=3, image_name="img/wintermeme.jpg")
    db.session.add(meme3)
    meme4 = Meme(id=4, name="Wegmans take my money", caption="Wegmans is so expensive", location_id=4, image_name="img/newmeme.jpeg")
    db.session.add(meme4)
    meme5 = Meme(id=5, name="IYKYK", caption="Some teachers just need help", location_id=2, image_name="img/techmeme.jpg")
    db.session.add(meme5)
    meme6 = Meme(id=6, name="CS > Everyone else", caption="CS majors rule", location_id=5,
                 image_name="img/csmeme.jpg")
    db.session.add(meme6)
    meme7 = Meme(id=7, name="Athlete problems", caption="Student Athletes", location_id=6,
                 image_name="img/athletememe.jpg")
    db.session.add(meme7)
    db.session.commit()

    # Location
    location1 = Location(id=1, name="Campus Center")
    db.session.add(location1)
    location2 = Location(id=2, name="Park School")
    db.session.add(location2)
    location3 = Location(id=3, name="No Specific Location")
    db.session.add(location3)
    location4 = Location(id=4, name="Off Campus")
    db.session.add(location4)
    location5 = Location(id=5, name="Williams")
    db.session.add(location5)
    location6 = Location(id=6, name="Hill Center")
    db.session.add(location6)
    db.session.commit()

    # Categories
    category1 = Category(id=1, name="food")
    db.session.add(category1)
    category2 = Category(id=2, name="technology")
    db.session.add(category2)
    category3 = Category(id=3, name="athlete")
    db.session.add(category3)
    category4 = Category(id=4, name="registration")
    db.session.add(category4)
    category5 = Category(id=5, name="computer science")
    db.session.add(category5)
    category6 = Category(id=6, name="winter")
    db.session.add(category6)
    db.session.commit()

    # MemeToCategory
    mtc1 = MemeToCategory(id=1, meme_id=1, category_id=4)
    db.session.add(mtc1)
    mtc2 = MemeToCategory(id=2, meme_id=2, category_id=6)
    db.session.add(mtc2)
    mtc3 = MemeToCategory(id=3, meme_id=3, category_id=6)
    db.session.add(mtc3)
    mtc4 = MemeToCategory(id=4, meme_id=5, category_id=2)
    db.session.add(mtc4)
    mtc5 = MemeToCategory(id=5, meme_id=4, category_id=1)
    db.session.add(mtc5)
    mtc6 = MemeToCategory(id=6, meme_id=6, category_id=2)
    db.session.add(mtc6)
    mtc7 = MemeToCategory(id=7, meme_id=6, category_id=5)
    db.session.add(mtc7)
    mtc8 = MemeToCategory(id=8, meme_id=7, category_id=3)
    db.session.add(mtc8)
    db.session.commit()

    return redirect('/index')