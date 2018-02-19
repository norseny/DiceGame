from flask import render_template, flash, redirect, url_for, request, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app
from app.forms import *
from app.models.user import *
from app.models.player import *
from app.models.game import *
from app.throw import throw_blueprint
from app.category import category_blueprint
from datetime import datetime

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
        game = Game(name=form.name.data)
        session['hplayers'] = form.human_players.data
        flash('New game "{}" created'.format(game.name))

        return redirect(url_for('playersnames', game_id=game.id, cplayers_no=form.computer_players.data))
    return render_template('newgame.html', title='New Game', form=form)


@app.route('/playersnames/<int:game_id>/<int:cplayers_no>', methods=['GET', 'POST'])
@login_required
def playersnames(game_id, cplayers_no):
    form = PlayersNamesForm()
    if form.validate_on_submit():

        human_players = []
        if form.players.data[0] != '':
            human_players = form.players.data[:]

        human_player = HumanPlayer(player_name=current_user.username)
        human_player.insert_player_to_db(game_id, True)

        for player in human_players:
            human_player = HumanPlayer(player_name=player)
            human_player.insert_player_to_db(game_id)

        game = Game.query.get(game_id)
        human_players_ids = game.get_list_of_human_players_ids()

        computer_player = ComputerPlayer()
        computer_player.create_cplayers(game_id, cplayers_no, form.computer_ai.data)

        return redirect(url_for('throw_blueprint.throw', game_id=game_id, player_id=human_players_ids[0]))

    # init the form with name of the user as the first player
    if session.get('hplayers'):
        form.players.entries[0] = current_user.username
        for i in range(1, session['hplayers']):
            form.players.append_entry()
        session.pop('hplayers', None)

    return render_template('playersnames.html', title='Players Names', form=form, cplayers_no=cplayers_no)


@app.route('/gameend/<int:game_id>/<int:suspend>', methods=['GET', 'POST'])
@login_required
def gameend(game_id, suspend=False):

    gameresults_dict = {}
    if not suspend:
        gameresult = Gameresult()
        gameresult.update_results(game_id)
        gameresults_all = Gameresult.query.filter_by(game_id=game_id).all()
        game = Game.query.get(game_id)
        game.finished = True
        db.session.commit()

        for el in gameresults_all:
            if isinstance(el, Gameresult):
                player = Player.query.get(int(el.player_id))
                gameresults_dict[player.player_name] = el.result

    return render_template('gameend.html', title='End of the game', gameresults_dict=gameresults_dict, suspend=suspend)


@app.route('/suspendedgames', methods=['GET', 'POST'])
@login_required
def suspendedgames():
    games = {}
    human_player = Player.query.filter_by(user_id=current_user.id).first()
    if human_player != None:
        player_unfinished_games = dict(
            Gameresult.query.filter_by(player_id=human_player.id, result=None).add_columns(Gameresult.game_id).all())

        for game_id in player_unfinished_games.values():
            unassingned_dicerolls_list = human_player.find_unassigned_dicerolls(game_id)
            human_player.remove_unassigned_dicerolls(unassingned_dicerolls_list)

        for el in player_unfinished_games.values():
            games[el] = list(Game.query.with_entities(Game.name, Game.date).filter_by(id=el).first())
            query = Turn.query.filter_by(game_id=el, player_id=human_player.id)
            games[el].append(query.count())
            games[el].append(query.with_entities(func.sum(Turn.part_result)).scalar())

    return render_template('suspendedgames.html', title='Suspended games',
                           games=games, isinstance=isinstance, datetime=datetime, human_player=human_player)


@app.route('/showcategory/<int:game_id>/<int:player_id>', methods=['GET', 'POST'])
@login_required
def showcategory(game_id, player_id):
    game = Game.query.get(int(game_id))
    player = Player.query.get(int(player_id))
    last_turn = Turn.query.filter_by(game_id=game_id, player_id=player_id).order_by(Turn.id.desc()).first()

    comp_last_cat, human_last_cat = 0, 0
    if player.computer_player:
        comp_last_cat = last_turn.category
    else:
        human_last_cat = last_turn.category

    last_diceroll_obj = Diceroll.query.filter_by(game_id=game_id, player_id=player_id).order_by(
        Diceroll.id.desc()).first()
    last_diceroll = last_diceroll_obj.return_dices_as_list()

    cat_results = player.generate_dict_of_part_results(game_id)
    categories = []
    category = Category()

    for i, cat in enumerate(category.category_details):
        categories.append({'label': '', 'description': '', 'description1': '', 'result': ''})
        categories[i]['label'] = cat['label']
        categories[i]['description'] = cat['desc1']
        categories[i]['description1'] = cat['desc2']
        if cat['label'] in cat_results:
            categories[i]['result'] = cat_results[cat['label']]

    total = 0
    for el in categories:
        if el['result'] != '':
            total += int(el['result'])

    form = ShowCategoryForm()
    if form.validate_on_submit():
        if form.submit_next_player.data:

            players = game.get_list_of_all_players_ids()
            curr_player_pos = players.index(player_id)

            if curr_player_pos != len(players) - 1:
                player_id = players[int(curr_player_pos + 1)]
            else:
                if 13 == player.get_no_of_turns(game_id):
                    return redirect(url_for('gameend', game_id=game_id, suspend=False))
                else:
                    player_id = players[0]

            return redirect(url_for('throw_blueprint.throw', game_id=game_id, player_id=player_id))

    return render_template('showcategory.html', title='The results', form=form, player_name=player.player_name,
                           last_diceroll=last_diceroll, total=total, comp_last_cat=comp_last_cat, categories=categories,
                           game_id=game_id, human_last_cat=human_last_cat)

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
