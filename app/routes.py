from flask import render_template, flash, redirect, url_for, request, session
from app import app, db
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from werkzeug.urls import url_parse
import random


@app.route('/')
@app.route('/index')
@login_required  # user needs to be logged to access "/" and "/index"
def index():
    # return render_template('index.html', title='Home', game_results=Gameresult.query.all())
    return render_template('index.html', title='Home', game_results=current_user.game_results)
    # return render_template('index.html', title='Home', game_results=game_results)
# w tutorialu posts=posts


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
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user-player')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    form = NewGameForm()
    if form.validate_on_submit():
        game = Game(name=form.name.data)
        db.session.add(game)
        gameresult = Gameresult(game_id=game.id, user_id=current_user.id)
        db.session.add(game)
        db.session.add(gameresult)
        db.session.commit()
        flash('New game %s created' % game.name)
        return redirect(url_for('throw'))
    return render_template('newgame.html', title='New Game', form=form)


@app.route('/throw', methods=['GET', 'POST'])
def throw():
    dices = []
    form = ThrowForm()
    if form.validate_on_submit():
        for i in range(5):
            dices.append(random.randint(1, 6))
        diceroll = Diceroll(dice1=dices[0], dice2=dices[1], dice3=dices[2], dice4=dices[3], dice5=dices[4])
        db.session.add(diceroll)
        db.session.commit()

        firstDiceroll = Diceroll.query.get(diceroll.id)
        session['firstDicerollId'] = firstDiceroll.id

        flash('Dices thrown')
        #return redirect(url_for('thrown'))
        return render_template('thrown.html', title='Thrown', dices=dices, firstDicerollId=firstDiceroll.id)
    return render_template('throw.html', title='Throw', form=form)


@app.route('/thrown', methods=['GET', 'POST'])
def thrown():
    firstDicerollId = session.get('firstDicerollId', None)

    if  firstDicerollId is not None:
        return render_template('thrown.html', title='Throw', firstDiceroll=firstDicerollId)
    return render_template('thrown.html', title='Thrown', firstDicerollId='aaa')


if __name__ == '__main__':
    app.run()
