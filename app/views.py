from flask import render_template, flash, redirect, url_for, request, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app
from app.forms import *
from app.models.user import *
from app.throw import throw_blueprint

app.register_blueprint(throw_blueprint)


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


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
    session.clear()
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
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    form = NewGameForm()
    if form.validate_on_submit():

        game = Game(name=form.name.data, cp_no=form.computer_players.data)
        session['hplayers'] = form.human_players.data

        flash('New game "{}" and {} computer players created'.format(game.name, form.computer_players.data))

        return redirect(url_for('playersnames', gameid=game.id))
    return render_template('newgame.html', title='New Game', form=form)


@app.route('/playersnames/<int:gameid>', methods=['GET', 'POST'])
def playersnames(gameid):
    hplayers_no = 0

    form = PlayersNamesForm()
    if form.validate_on_submit():

        player = Player(player_name=form.player_name1.data)
        db.session.add(player)
        db.session.commit()
        game_result = Gameresult(game_id=gameid, player_id=player.id)
        db.session.add(game_result)
        db.session.commit()

        player = Player(player_name=form.player_name2.data)
        db.session.add(player)
        db.session.commit()
        game_result = Gameresult(game_id=gameid, player_id=player.id)
        db.session.add(game_result)
        db.session.commit()

        if session.get('hplayers'):
            hplayers_no = session['hplayers']

        flash('Human players: {} and {} created'.format(form.player_name1.data, form.player_name2.data))

        if session.get('diceroll_1_id'):  # moze da sie inaczej?
            session.pop('diceroll_1_id')
        if session.get('diceroll_2_id'):
            session.pop('diceroll_2_id')
        if session.get('diceroll_3_id'):
            session.pop('diceroll_3_id')

        return redirect(url_for('throw_blueprint.throw', gameid=gameid))
    return render_template('playersnames.html', title='Players Names', form=form, hplayers_no=hplayers_no)


@app.route('/process', methods=['POST'])
def process():

    human_players = request.form['human_players']

    if human_players:
        success = str(human_players)

        return jsonify({'name': success})
    return jsonify({'error': 'Missing data!'})


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)