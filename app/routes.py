import os

from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import event, false, true
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, RegistrationForm, NewMemeForm, PhotoForm, MemeSearchForm, SearchForm
from app.models import User, Meme, Location, Category, MemeToCategory
from flask_login import current_user, login_user, login_required, logout_user


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        search = form.search.data
        return redirect(url_for('results', search=search))

    # categoriesList = Category.query.all()
        # for category in categoriesList:
        #     if search == category.name:
        #         result = search
        #         return render_template('results', )
        #     else:
        #         flash('No results found')
        #         return render_template('index.html', title='Home', form=form)

    # search = MemeSearchForm(request.form)

    # categoriesList = Category.query.all()
    # search.categories.choices = [(category.id, category.name) for category in categoriesList]

    # if request.method == 'POST':
        # return search_results(search)

    return render_template('index.html', title='Home', form=form)


@app.route('/results/<search>')
def results(search):
    category = Category.query.filter_by(name=search).first_or_404()

    # get all memes with category
        # def search_results(search):
    # results = []
    # search_string = search.data['search']

    # if search.data['search'] == '':
        # qry = db_session.query(Album)
        # results = qry.all()

    # if not results:
        # flash('No results found')
        # return redirect('/')

    # else:
        # display results
        # return render_template('results.html', results=results)
    return render_template('results.html', title="Results", category=category)


@app.route('/memes')
def memes():
    UPLOAD_FOLDER = '/static/img'

    form = PhotoForm()

    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        # f.save(os.path.join(
            # app.instance_path, 'photos', filename
        # ))

        f.save(os.path.join(app.config[UPLOAD_FOLDER], filename))

        return redirect(url_for('index'))

    return render_template('memes.html', title="Memes", form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = NewMemeForm()

    locationList = Location.query.all()
    form.location.choices = [(location.id, location.name) for location in locationList]

    categoriesList = Category.query.all()
    form.categories.choices = [(category.id, category.name) for category in categoriesList]

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
        # events = ["No upcoming shows"]

        for l in locationList:
            if l.id == form.location.data:
                place = l.id

        newmemeentry = Meme(name=form.name.data, caption=form.caption.data, location_id=place)
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
    meme1 = Meme(id=1, name="meme1", caption="so funny", location_id=1)
    db.session.add(meme1)
    meme2 = Meme(id=2, name="meme2", caption="great picture", location_id=2)
    db.session.add(meme2)
    db.session.commit()

    # Location
    location1 = Location(id=1, name="Campus Center")
    db.session.add(location1)
    location2 = Location(id=2, name="Park School")
    db.session.add(location2)
    db.session.commit()

    # Categories
    category1 = Category(id=1, name="food")
    db.session.add(category1)
    category2 = Category(id=2, name="technology")
    db.session.add(category2)
    category3 = Category(id=3, name="athlete")
    db.session.add(category3)
    db.session.commit()

    # MemeToCategory
    mtc1 = MemeToCategory(id=1, meme_id=1, category_id=1)
    db.session.add(mtc1)
    mtc2 = MemeToCategory(id=2, meme_id=1, category_id=3)
    db.session.add(mtc2)
    mtc3 = MemeToCategory(id=3, meme_id=2, category_id=2)
    db.session.add(mtc3)
    db.session.commit()

    return redirect('/index')