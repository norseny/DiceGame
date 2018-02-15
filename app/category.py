from flask import render_template, flash, redirect, url_for, session, Blueprint
from app.forms import *
from app.models.diceroll import *
from app.models.category import *
from app.models.player import *
from flask_login import login_required

category_blueprint = Blueprint('category_blueprint', __name__)


@category_blueprint.route('/category/<int:game_id>/<int:playerid>', methods=['GET', 'POST'])
@login_required
def category(game_id, playerid):
    
    # dicerolls_data = get_dicerolls_data() #todo: dokonczyc
    dicerolls_data = {}
    dicerolls_data['second_dice_id'] = 0
    dicerolls_data['third_dice_id'] = 0
    if session.get('diceroll_3_id'):
        third_dice = last_dice = Diceroll.query.get(session['diceroll_3_id'])
        dicerolls_data['third_dice_id'] = third_dice.id
        session.get('diceroll_2_id')
        second_dice = Diceroll.query.get(session['diceroll_2_id'])
        dicerolls_data['second_dice_id'] = second_dice.id
        session.get('diceroll_1_id')
        first_dice = Diceroll.query.get(session['diceroll_1_id'])
        dicerolls_data['first_dice_id'] = first_dice.id
    elif session.get('diceroll_2_id'):
        second_dice = last_dice = Diceroll.query.get(session['diceroll_2_id'])
        dicerolls_data['second_dice_id'] = second_dice.id
        session.get('diceroll_1_id')
        first_dice = Diceroll.query.get(session['diceroll_1_id'])
        dicerolls_data['first_dice_id'] = first_dice.id
    elif session.get('diceroll_1_id'):
        first_dice = last_dice = Diceroll.query.get(session['diceroll_1_id'])
        dicerolls_data['first_dice_id'] = first_dice.id
    last_diceroll = last_dice.return_dices_as_list()

    form = SelectCategoryForm()
    hide_checkboxes = False
    game = Game.query.get(game_id)
    player = Player.query.get(playerid)
    comp = []

    cat_results = player.generate_dict_of_part_results(game_id)
    choices = list(form.choices)
    category = Category()
    for i, cat in enumerate(category.category_details):
        choices[i].label = cat['label']
        choices[i].description = cat['desc1']
        choices[i].description1 = cat['desc2']
        if cat['label'] in cat_results:
            choices[i].result = cat_results[cat['label']]

    total = 0
    for radio in choices:
        if hasattr(radio, 'result'):
            total += radio.result

    if not form.submit_next_player.data:  # todo: moze rozwiazac tego ifa inaczej
        if playerid not in game.get_list_of_human_players_ids():

            computer_player = ComputerPlayer.query.get(int(playerid))
            curr_computer_player = computer_player.check_ai_and_return_object()

            if isinstance(curr_computer_player, ComputerPlayerDummy):
                picked_category = curr_computer_player.choose_rand_cat_and_count_result(last_diceroll, game_id)

            elif isinstance(curr_computer_player, ComputerPlayerSmart):
                picked_category = curr_computer_player.choose_cat_and_count_result(last_diceroll, game_id)

            for radio in choices:
                if radio.label == picked_category['name']:
                    radio.result = picked_category['result']
                    total += radio.result

            curr_computer_player.insert_part_result(game_id, picked_category['name'], picked_category['result'],
                                                    dicerolls_data['first_dice_id'], dicerolls_data['second_dice_id'],
                                                    dicerolls_data['third_dice_id'])
            hide_checkboxes = True
            comp.append(True)
            comp.append(picked_category['name'])

    if form.validate_on_submit():

        if form.submit_the_box.data:
            for radio in choices:
                if radio.checked:
                    method_name = ((radio.label).lower()).replace(' ', '_')
                    getattr(category, method_name + '_count')(last_diceroll)
                    player.insert_part_result(game_id, radio.label, category.result, dicerolls_data['first_dice_id'],
                                              dicerolls_data['second_dice_id'], dicerolls_data['third_dice_id'])
                    radio.result = category.result
                    hide_checkboxes = True
                    total += radio.result

                    return render_template('category.html', title='Category Selection', form=form,
                                           hide_checkboxes=hide_checkboxes, player_name=player.player_name,
                                           last_diceroll=last_diceroll, total=total, computer=comp, choices=choices,
                                           hasattr=hasattr, game_id=game_id)

        elif form.submit_next_player.data:  # todo: przycisk label end of the game jak juz wszyscy rzucili

            game = Game.query.get(int(game_id))
            players = game.get_list_of_all_players_ids()
            curr_player_pos = players.index(playerid)

            if curr_player_pos != len(players) - 1:
                playerid = players[int(curr_player_pos + 1)]
            else:
                if 13 == player.get_no_of_turns(game_id):
                    return redirect(url_for('gameend', game_id=game_id))
                else:
                    playerid = players[0]

            session.pop('diceroll_1_id', None)
            session.pop('diceroll_2_id', None)
            session.pop('diceroll_3_id', None)

            player_name = db.session.query(Player.player_name).filter(Player.id == playerid).scalar()
            flash('The current player is: {}'.format(player_name))
            return redirect(url_for('throw_blueprint.throw', game_id=game_id, playerid=playerid))

    return render_template('category.html', title='Category Selection', form=form, hide_checkboxes=hide_checkboxes,
                           player_name=player.player_name, last_diceroll=last_diceroll, total=total, computer=comp,
                           choices=choices,
                           hasattr=hasattr, game_id=game_id)
