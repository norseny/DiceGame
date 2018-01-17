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
        if session.get('dicerollid1'):
            session.pop('dicerollid1')
        if session.get('dicerollid2'):
            session.pop('dicerollid2')
        if session.get('dicerollid3'):
            session.pop('dicerollid3')
        flash('New game %s created' % game.name)
        return redirect(url_for('throw', gameid=game.id))
    return render_template('newgame.html', title='New Game', form=form)

@app.route('/throw/<int:gameid>', methods=['GET', 'POST'])
def throw(gameid):
    turn = 1
    diceroll1 = []
    diceroll2 = []
    diceroll3 = []
    if session.get('dicerollid1'):
        id = session['dicerollid1']
        dicerollclass1 = Diceroll.query.get(id)
        diceroll1.append(dicerollclass1.dice1)
        diceroll1.append(dicerollclass1.dice2)
        diceroll1.append(dicerollclass1.dice3)
        diceroll1.append(dicerollclass1.dice4)
        diceroll1.append(dicerollclass1.dice5)
        turn = 2
        if session.get('dicerollid2'):
            id = session['dicerollid2']
            dicerollclass2 = Diceroll.query.get(id)
            diceroll2.append(dicerollclass2.dice1)
            diceroll2.append(dicerollclass2.dice2)
            diceroll2.append(dicerollclass2.dice3)
            diceroll2.append(dicerollclass2.dice4)
            diceroll2.append(dicerollclass2.dice5)
            turn = 3
    form = ThrowForm()
    if form.validate_on_submit():
        if form.throwsel.data:
            print('throwsel')
            if turn > 1 :
                dicerolldb = Diceroll()
                if turn ==2:
                    dicerolldb = dicerollclass1
                elif turn == 3:
                    dicerolldb = dicerollclass2
                if form.dice1.data:
                    dicerolldb.dice1 = random.randint(1, 6)
                if form.dice2.data:
                    dicerolldb.dice2 = random.randint(1, 6)
                if form.dice3.data:
                    dicerolldb.dice3 = random.randint(1, 6)
                if form.dice4.data:
                    dicerolldb.dice5 = random.randint(1, 6)
                if form.dice5.data:
                    dicerolldb.dice5 = random.randint(1, 6)
                flash('Selected dices thrown')
                db.session.add(dicerolldb)
                db.session.commit()
                if turn == 2:
                    session['dicerollid2'] = dicerolldb.id
                    id = session['dicerollid2']
                    dicerollclass2 = Diceroll.query.get(id)
                    diceroll2.append(dicerollclass2.dice1)
                    diceroll2.append(dicerollclass2.dice2)
                    diceroll2.append(dicerollclass2.dice3)
                    diceroll2.append(dicerollclass2.dice4)
                    diceroll2.append(dicerollclass2.dice5)
                elif turn == 3:
                    session['dicerollid3'] = dicerolldb.id
                    id = session['dicerollid3']
                    dicerollclass3 = Diceroll.query.get(id)
                    diceroll3.append(dicerollclass3.dice1)
                    diceroll3.append(dicerollclass3.dice2)
                    diceroll3.append(dicerollclass3.dice3)
                    diceroll3.append(dicerollclass3.dice4)
                    diceroll3.append(dicerollclass3.dice5)
                turn += 1
                return render_template('throw.html', title='Throw', form=form, turn=turn, dices1=diceroll1,dices2=diceroll2, dices3=diceroll3)
        elif form.throwall.data:
            if not session.get('dicerollid1'):
                for i in range(5):
                    diceroll1.append(random.randint(1, 6))
                dicerolldb = Diceroll(dice1=diceroll1[0], dice2=diceroll1[1], dice3=diceroll1[2], dice4=diceroll1[3],dice5=diceroll1[4])
                db.session.add(dicerolldb)
                db.session.commit()
                session['dicerollid1'] = dicerolldb.id
            elif session.get('dicerollid1') and (not session.get('dicerollid2')):
                for i in range(5):
                    diceroll2.append(random.randint(1, 6))
                dicerolldb = Diceroll(dice1 = diceroll2[0], dice2=diceroll2[1], dice3=diceroll2[2], dice4=diceroll2[3], dice5=diceroll2[4])
                db.session.add(dicerolldb)
                db.session.commit()
                session['dicerollid2'] = dicerolldb.id
                id = session['dicerollid2']
            elif session.get('dicerollid2') is not None:
                for i in range(5):
                    diceroll3.append(random.randint(1, 6))
                dicerolldb = Diceroll(dice1=diceroll3[0], dice2=diceroll3[1], dice3=diceroll3[2], dice4=diceroll3[3],dice5=diceroll3[4])
                db.session.add(dicerolldb)
                db.session.commit()
                session['dicerollid3'] = dicerolldb.id
                id = session['dicerollid3']
            turn +=1
            flash('All dices thrown')
            return render_template('throw.html', title='Throw', form=form, turn=turn, dices1=diceroll1,dices2=diceroll2, dices3=diceroll3)
        elif form.keep.data or form.catsel.data:
            return redirect(url_for('category',gameid=gameid)) # todo complete
    return render_template('throw.html', title='Throw', form=form, turn=turn, dices1=diceroll1, dices2=diceroll2, dices3=diceroll3)


@app.route('/thrown<int:gameid>/<int:turn>/<int:dicerollid>', methods=['GET', 'POST'])
def thrown(gameid, turn, dicerollid):
    form = ThrowForm()
    if form.validate_on_submit():
        if dicerollid is not None:
            return render_template('thrown.html', title='Throw', dicerollid=dicerollid)
    return render_template('thrown.html', title='Thrown', dicerollid='aaa')


if __name__ == '__main__':
    app.run(host='localhost', port=5027, debug=True)