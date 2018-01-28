from flask import render_template, flash, redirect, url_for, request, session, jsonify
from app import app, db
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from werkzeug.urls import url_parse
from .throw import throw_blueprint

app.register_blueprint(throw_blueprint)

@app.route('/')
@app.route('/index')
@login_required  # user needs to be logged to access "/" and "/index"
def index():
    return render_template('index.html', title='Home')
    # return render_template('form.html')

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
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    print('vvv')

    form = NewGameForm()
    if form.validate_on_submit():

        game = Game(name=form.name.data)
        db.session.add(game)
        db.session.commit()
        human_players_no = form.human_players.data

        computer_players_no = form.computer_players.data

        for c_player in range(1,computer_players_no):
            player = Player(player_name='C'+str(c_player))
            db.session.add(player)
            db.session.commit()
            game_result = Gameresult(game_id=game.id, player_id=player.id)
            db.session.add(game_result)
            db.session.commit()

        flash('New game "{}" and {} computer players created'.format(game.name, computer_players_no))

        return redirect(url_for('playersnames', gameid=game.id, hplayers_no=human_players_no))
    return render_template('newgame.html', title='New Game', form=form)


@app.route('/playersnames/<int:gameid>/<int:hplayers_no>', methods=['GET', 'POST'])
def playersnames(gameid, hplayers_no):

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

        # player = Player(player_name=form.player_name3.data)
        # db.session.add(player)
        # db.session.commit()
        # game_result = Gameresult(game_id=gameid, player_id=player.id)
        # db.session.add(game_result)
        # db.session.commit()

        flash('{} human players created'.format(hplayers_no))

        if session.get('diceroll_1_id'): # moze da sie inaczej?
            session.pop('diceroll_1_id')
        if session.get('diceroll_2_id'):
            session.pop('diceroll_2_id')
        if session.get('diceroll_3_id'):
            session.pop('diceroll_3_id')

        for p in range (1, hplayers_no):
            return redirect(url_for('throw_blueprint.throw', gameid=gameid))

    return render_template('playersnames.html', title='Players Names', form=form, hplayers_no=hplayers_no)


@app.route('/process', methods=['POST'])
def process():
    print('aaa')

    human_players = request.form['human_players']
    print('bbb')
    print("{}".format(human_players))

    if human_players:
        success = str(human_players)

        return jsonify({'name' : success})
    return jsonify({'error' : 'Missing data!'})

@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


if __name__ == '__main__':
    app.run(host='localhost', port=5027, debug=True)