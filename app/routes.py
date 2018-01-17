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
        game_result = Gameresult(game_id=game.id, user_id=current_user.id)
        db.session.add(game)
        db.session.add(game_result)
        db.session.commit()
        if session.get('diceroll_1_id'): # moze da sie inaczej?
            session.pop('diceroll_1_id')
        if session.get('diceroll_2_id'):
            session.pop('diceroll_2_id')
        if session.get('diceroll_3_id'):
            session.pop('diceroll_3_id')
        flash('New game %s created' % game.name)
        return redirect(url_for('throw', gameid=game.id))
    return render_template('newgame.html', title='New Game', form=form)


@app.route('/throw/<int:gameid>', methods=['GET', 'POST'])
def throw(gameid):      # podzielic funkcję na 3 czesci w zaleznosci od wybranego submita???
    turn = 1
    list_diceroll_1, list_diceroll_2, list_diceroll_3 = [], [], []
    if session.get('diceroll_1_id'):
        class_diceroll_1 = Diceroll.query.get(session['diceroll_1_id'])
        list_diceroll_1 = class_diceroll_1.return_dices_as_list()
        turn = 2
        if session.get('diceroll_2_id'):
            class_diceroll_2 = Diceroll.query.get(session['diceroll_2_id'])
            list_diceroll_2 = class_diceroll_2.return_dices_as_list()
            turn = 3
    form = ThrowForm()
    if form.validate_on_submit():
        if form.throw_sel.data:
            if turn > 1:
                diceroll_to_db = Diceroll()
                if turn == 2:
                    diceroll_to_db = class_diceroll_1
                elif turn == 3:
                    diceroll_to_db = class_diceroll_2
                if form.dice1.data:
                    diceroll_to_db.dice1 = random.randint(1, 6)
                if form.dice2.data:
                    diceroll_to_db.dice2 = random.randint(1, 6)
                if form.dice3.data:
                    diceroll_to_db.dice3 = random.randint(1, 6)
                if form.dice4.data:
                    diceroll_to_db.dice5 = random.randint(1, 6)
                if form.dice5.data:
                    diceroll_to_db.dice5 = random.randint(1, 6)
                flash('Selected dices thrown')
                db.session.add(diceroll_to_db)
                db.session.commit()
                if turn == 2:
                    session['diceroll_2_id'] = diceroll_to_db.id
                    class_diceroll_2 = Diceroll.query.get(session['diceroll_2_id'])
                    list_diceroll_2 = class_diceroll_2.return_dices_as_list()
                elif turn == 3:
                    session['diceroll_3_id'] = diceroll_to_db.id
                    class_diceroll_3 = Diceroll.query.get(session['diceroll_3_id'])
                    list_diceroll_3 = class_diceroll_3.return_dices_as_list()
                turn += 1
                return render_template('throw.html', title='Throw', form=form, turn=turn, dices_1=list_diceroll_1,dices_2=list_diceroll_2, dices_3=list_diceroll_3)
        elif form.throw_all.data:
            diceroll_to_db = Diceroll()
            diceroll_to_db.generate_all_rand_dices()
            if turn == 1:
                list_diceroll_1 = diceroll_to_db.return_dices_as_list()
                db.session.add(diceroll_to_db)
                db.session.commit()
                session['diceroll_1_id'] = diceroll_to_db.id
            elif turn == 2:
                list_diceroll_2 = diceroll_to_db.return_dices_as_list()
                db.session.add(diceroll_to_db)
                db.session.commit()
                session['diceroll_2_id'] = diceroll_to_db.id
            elif turn == 3:
                list_diceroll_3 = diceroll_to_db.return_dices_as_list()
                db.session.add(diceroll_to_db)
                db.session.commit()
                session['diceroll_3_id'] = diceroll_to_db.id
            turn +=1
            flash('All dices thrown')
            return render_template('throw.html', title='Throw', form=form, turn=turn, dices_1=list_diceroll_1, dices_2=list_diceroll_2, dices_3=list_diceroll_3)
        elif form.keep.data or form.cat_sel.data:
            return redirect(url_for('category',gameid=gameid)) # todo complete
    return render_template('throw.html', title='Throw', form=form, turn=turn)


if __name__ == '__main__':
    app.run(host='localhost', port=5027, debug=True)