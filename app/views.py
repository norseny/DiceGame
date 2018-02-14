from flask import render_template, flash, redirect, url_for, request, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app
from app.forms import *
from app.models.user import *
from app.models.player import *
from app.throw import throw_blueprint
from app.category import category_blueprint


app.register_blueprint(throw_blueprint)
app.register_blueprint(category_blueprint)


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
@login_required
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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/newgame', methods=['GET', 'POST'])
@login_required
def newgame():
    form = NewGameForm()
    if form.validate_on_submit():

        game = Game()
        session['cplayers'] = form.computer_players.data
        session['hplayers'] = form.human_players.data
        flash('New game "{}" created'.format(game.name))

        return redirect(url_for('playersnames', gameid=game.id))
    return render_template('newgame.html', title='New Game', form=form)


@app.route('/playersnames/<int:gameid>', methods=['GET', 'POST'])
@login_required
def playersnames(gameid):

    form = PlayersNamesForm()
    if form.validate_on_submit():

        human_players = []
        if form.players.data[0] != '':
            human_players = form.players.data[:]
        human_players.insert(0, current_user.username)
        for player in human_players:
            human_player = HumanPlayer(player_name=player)
            human_player.insert_player_to_db(gameid)

        game = Game.query.get(gameid)

        human_players_ids = game.get_list_of_human_players_ids()

        if session.get('cplayers'):
            computer_player = ComputerPlayer()
            computer_player.create_cplayers(gameid, session['cplayers'], form.computer_ai.data)
            session.pop('cplayers', None)

        session.pop('diceroll_1_id', None)
        session.pop('diceroll_2_id', None)
        session.pop('diceroll_3_id', None) # todo: lepiej przechowac to w liscie session['game_data']

        flash('Players created. The current player is: {}'.format(human_players[0]))

        return redirect(url_for('throw_blueprint.throw', gameid=gameid ,playerid=human_players_ids[0]))

    if session.get('hplayers'):
        form.players.entries[0] = current_user.username
        for i in range(1, session['hplayers']):
            form.players.append_entry()
        session.pop('hplayers', None)

    return render_template('playersnames.html', title='Players Names', form=form)


@app.route('/gameend/<int:gameid>', methods=['GET', 'POST'])
@login_required
def gameend(gameid):

    gameresult = Gameresult()
    gameresult.update_results(gameid)
    gameresults_all = Gameresult.query.filter_by(game_id=gameid).all()
    gameresults_dict = {}

    for el in gameresults_all:
        if isinstance(el, Gameresult):
            player = Player.query.get(int(el.player_id))
            gameresults_dict[player.player_name] = el.result

    return render_template('gameend.html', title='End of the game', gameresults_dict=gameresults_dict)


# @app.route('/process', methods=['POST'])
# def process():
#
#     human_players = request.form['human_players']
#
#     if human_players:
#         success = str(human_players)
#
#         return jsonify({'name': success})
#     return jsonify({'error': 'Missing data!'})
#
#
# @app.route('/_add_numbers')
# def add_numbers():
#     a = request.args.get('a', 0, type=int)
#     b = request.args.get('b', 0, type=int)
#     return jsonify(result=a + b)
