from flask import render_template, flash, redirect, url_for, session, Blueprint
from app import app
from app.forms import *
from app.models.diceroll import *
from app.category import category_blueprint
from app.models.player import *
from flask_login import login_required

app.register_blueprint(category_blueprint)

throw_blueprint = Blueprint('throw_blueprint', __name__)


@throw_blueprint.route('/throw/<int:game_id>/<int:player_id>', methods=['GET', 'POST'])
@login_required
def throw(game_id, player_id):

    turn = 1
    dicerolls_lists = []

    if session.get('diceroll_1_id'):
        diceroll_1 = Diceroll.query.get(session['diceroll_1_id'])
        dicerolls_lists.append(diceroll_1.return_dices_as_list())
        turn = 2
        if session.get('diceroll_2_id'):
            diceroll_2 = Diceroll.query.get(session['diceroll_2_id'])
            dicerolls_lists.append(diceroll_2.return_dices_as_list())
            turn = 3
            if session.get('diceroll_3_id'):
                return redirect(url_for('category_blueprint.category', game_id=game_id, player_id=player_id,
                                diceroll_id_1=0, diceroll_id_2=0, diceroll_id_3=0))

    game = Game.query.get(int(game_id))
    form = ThrowForm()

    if form.validate_on_submit():
        diceroll = Diceroll()

        if player_id in game.get_list_of_human_players_ids():

            # human_player = HumanPlayer.query.get(int(player_id))
            # human_player.handle_throw_form(turn, form.throw_sel.data, form.throw_all.data, form.keep.data, form.)

            if form.throw_sel.data:
                if turn > 1:
                    diceroll = Diceroll()
                    if turn == 2:
                        diceroll.assign_dices(diceroll_1)
                    elif turn == 3:
                        diceroll.assign_dices(diceroll_2)

                    sel_dices = []
                    for i in range(1, 6):
                        form_dice_sel = getattr(form, 'dice' + str(i))
                        sel_dices.append(form_dice_sel.data)
                    diceroll.check_selected_get_random_numbers_and_insert(sel_dices, player_id, game_id)
                    flash('Selected dices thrown')

            elif form.throw_all.data:
                dicerolls_lists.append(diceroll.throw_all_rand(player_id, game_id))
                if 'diceroll_1_id' not in session:
                    session['diceroll_1_id'] = diceroll.id
                elif 'diceroll_2_id' not in session:
                    session['diceroll_2_id'] = diceroll.id
                else:
                    session['diceroll_3_id'] = diceroll.id
                flash('All dices thrown')

            elif form.keep.data or form.cat_sel:
                return redirect(url_for('category_blueprint.category', game_id=game_id, player_id=player_id))

            dicerolls_lists.append(diceroll.return_dices_as_list())
            if turn == 2:
                session['diceroll_2_id'] = diceroll.id
            elif turn == 3:
                session['diceroll_3_id'] = diceroll.id
            turn += 1

            human_player = HumanPlayer.query.get(int(player_id))
            disabled_categories = list(human_player.generate_dict_of_part_results(game_id).keys())

            return render_template('throw.html', title='Throw', form=form, turn=turn, dices=dicerolls_lists,
                                   disabled_categories=disabled_categories, game_id=game_id)

        else:
            computer_player = ComputerPlayer.query.get(int(player_id))  # todo ?...
            curr_computer_player = computer_player.check_ai_and_return_object()

            choice = 0

            if (turn == 2) or (turn == 3):
                choice = random.randint(1, 3)

            if (turn == 1) or (choice == 1):  # choice = 1 oznacza rzut wszystkimi
                dicerolls_lists.append(diceroll.throw_all_rand(player_id, game_id))
                if 'diceroll_1_id' not in session:
                    session['diceroll_1_id'] = diceroll.id
                elif 'diceroll_2_id' not in session:
                    session['diceroll_2_id'] = diceroll.id
                else:
                    session['diceroll_3_id'] = diceroll.id
                flash('All dices thrown')
                turn += 1
                return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
                                       dices=dicerolls_lists, game_id=game_id)

            elif (choice == 2) and ((turn == 2) or (turn == 3)):  # wybór czym rzucić
                if isinstance(curr_computer_player, ComputerPlayerDummy):
                    if turn == 2:
                        diceroll.assign_dices(diceroll_1)
                    elif turn == 3:
                        diceroll.assign_dices(diceroll_2)
                    ticked_boxes = curr_computer_player.randomly_select_dices(diceroll, game_id)
                    dicerolls_lists.append(diceroll.return_dices_as_list())
                    flash('Computer selected dice with number/s: {} to throw again'.format(sorted(ticked_boxes)))
                    if turn == 2:
                        session['diceroll_2_id'] = diceroll.id
                    elif turn == 3:
                        session['diceroll_3_id'] = diceroll.id
                    turn += 1

                elif isinstance(curr_computer_player, ComputerPlayerSmart):  # todo: sth
                    if turn == 2:
                        diceroll.assign_dices(diceroll_1)
                    elif turn == 3:
                        diceroll.assign_dices(diceroll_2)

                    dum_comp = ComputerPlayerDummy.query.get(player_id)
                    ticked_boxes = dum_comp.randomly_select_dices(diceroll, game_id)  # todo:

                    dicerolls_lists.append(diceroll.return_dices_as_list())
                    flash('Computer selected dice with number/s: {} to throw again'.format(sorted(ticked_boxes)))
                    if turn == 2:
                        session['diceroll_2_id'] = diceroll.id
                    elif turn == 3:
                        session['diceroll_3_id'] = diceroll.id
                    turn += 1

                return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
                                       dices=dicerolls_lists, game_id=game_id)

            elif (choice == 3) or (turn == 4):  # wybór kategorii
                return redirect(url_for('category_blueprint.category', game_id=game_id, player_id=player_id))

    if player_id in game.get_list_of_human_players_ids():
        human_player = HumanPlayer.query.get(int(player_id))
        disabled_categories = list(human_player.generate_dict_of_part_results(game_id).keys())
        return render_template('throw.html', title='Throw', form=form, turn=turn,
                               disabled_categories=disabled_categories, game_id=game_id)
    else:
        return render_template('computerthrow.html', title='Throw', form=form, turn=turn, game_id=game_id)
