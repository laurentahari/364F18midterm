###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField,ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
import json, requests, omdb 

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/SI364midterm"

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from SI364'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################
def save_titles(db_session,titlename):
    x = db.session.query(Title).filter_by(title=titlename).first() 
    url = "http://www.omdbapi.com/?apikey=5d008589&t={}".format(titlename)
    get_request = requests.get(url).json()['Title']

    if not x:
        x = Title(title = get_request)
        db.session.add(x)
        db.session.commit()
        flash("The movie was successfully added!")

    else:
        flash ("This movie already exists") 
        return redirect(url_for('display_all_titles'))


def save_director(db_session, directorname):
    y = db.session.query(Director).filter_by(directorname = directorname).first()
    if y:
        flash("This director has already been added")
        return redirect(url_for('display_all_directors'))
       
    else:
        director = Director(directorname = directorname)
        db_session.add(director)
        db_session.commit
        flash('The director was successfully added!')
        return redirect(url_for('index'))



##################
##### MODELS #####
##################
class Person(db.Model):
    __tablename__ = "People"
    id = db.Column(db.Integer,primary_key=True)
    person = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.person, self.id)

class Title(db.Model):
    __tablename__ = "Movie_Titles"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64))
    directors = db.relationship('Director', backref = 'Title')

    def __repr__(self):
        return "{0} (ID: {1})".format(self.id, self.titles, self.directors)

class Director(db.Model):
    __tablename__="Movie_Directors"
    id = db.Column(db.Integer, primary_key=True)
    directorname = db.Column(db.String(64))
    titleid = db.Column(db.Integer, db.ForeignKey("Movie_Titles.id"))

    def __rept__(self):
        return "{} (ID: {})".format(self.id, self.directorname, self.titleid)


###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    person = StringField("Please enter your name ",validators=[Required()])
    submit = SubmitField()

    def validate_person(self,field):
        if field.data[0] == "@":
            raise ValidationError("This is not a valid name (do not use an @ symbol).")
       

class TitleForm(FlaskForm):
    titlename = StringField("Please enter the name of a movie", validators=[Required(),Length(min=1,max=280)])
    submit = SubmitField('Submit')

    def validate_titlename(self,field):
        if field.data[0] == "@" :
            raise ValidationError("This is not a valid title")

        if field.data[0] == "!" :
            raise ValidationError("This is not a valid title")

class DirectorForm(FlaskForm):
    directorname = StringField("Please enter the name of a director", validators=[Required(),Length(min=1,max=280)])
    submit = SubmitField('Submit')



#######################
###### VIEW FXNS ######
#######################

#need to edit below this
@app.route('/people')
def people():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if request.args:
        person = request.args['person']
        newperson = Person(person=person)
        db.session.add(newperson)
        db.session.commit()
    return render_template('name_example.html', form=form, people=Person.query.all())

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!

#error handler routes

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#initialize the database

@app.route('/', methods=['GET', 'POST']) 
def index():
    form = TitleForm()
    if request.method == 'POST' and form.validate_on_submit():
        titlenames = form.titles.data
    return render_template('base.html',form = form)

@app.route('/view_all_directors', methods=['GET','POST'])
def display_all_directors():
    form = DirectorForm()
    if request.method == 'POST' and form.validate_on_submit():
       directorname = form.directorname.data
       save_director(db.session, directorname)

    errors = [l for l in form.errors.values()]
    if len(errors) > 0:
        flash("ERROR IN FORM SUBMISSION - " + str(errors))

    return render_template('view_all_directors.html',form = form, view_all_directors=Director.query.all())


@app.route('/view_all_titles', methods = ['GET','POST'])
def display_all_titles():
    form = TitleForm()
    if request.args:
        titlename = request.args['titlename']
        save_titles(db.session, titlename)
 

    errors = [l for l in form.errors.values()]
    if len(errors) > 0:
        flash("ERROR IN FORM SUBMISSION - " + str(errors))

    return render_template('view_all_titles.html', form = form, view_all_titles = Title.query.all() )


if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual