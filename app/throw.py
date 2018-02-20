from flask import render_template, flash, redirect, url_for, session, Blueprint
from app import app
from app.forms import *
from app.models.diceroll import *
from app.category import category_blueprint
from app.models.player import *
from app.models.game import *
from flask_login import login_required

app.register_blueprint(category_blueprint)

throw_blueprint = Blueprint('throw_blueprint', __name__)


@throw_blueprint.route('/throw/<int:game_id>/<int:player_id>', methods=['GET', 'POST'])
@login_required
def throw(game_id, player_id):
    turn = 1
    dicerolls_lists = []
    player = Player.query.get(player_id)
    dicerolls_objects_lists = player.find_unassigned_dicerolls(game_id)

    for diceroll in dicerolls_objects_lists:
        dicerolls_lists.append(diceroll.return_dices_as_list())

    if dicerolls_lists:
        turn = len(dicerolls_lists) + 1

    if turn > 3:
        return redirect(url_for('category_blueprint.category', game_id=game_id, player_id=player_id))

    game = Game.query.get(int(game_id))

    form = ThrowForm()

    if form.validate_on_submit():
        diceroll = Diceroll()

        if player_id in game.get_list_of_human_players_ids():
            human_player = HumanPlayer.query.get(int(player_id))
            categories = human_player.generate_categories_table_data(game_id)

            if form.throw_sel.data:
                if turn > 1:
                    diceroll = Diceroll()
                    if turn == 2:
                        diceroll.assign_dices(dicerolls_objects_lists[0])
                    elif turn == 3:
                        diceroll.assign_dices(dicerolls_objects_lists[1])

                    sel_dices = []
                    for i in range(1, 6):
                        form_dice_sel = getattr(form, 'dice' + str(i))
                        sel_dices.append(form_dice_sel.data)
                    diceroll.check_selected_get_random_numbers_and_insert(sel_dices, player_id, game_id)
                    flash('Selected dices thrown')

            elif form.throw_all.data:
                dicerolls_lists.append(diceroll.throw_all_rand(player_id, game_id))
                flash('All dices thrown')

            elif form.keep.data or form.cat_sel:
                return redirect(url_for('category_blueprint.category', game_id=game_id, player_id=player_id))

            dicerolls_lists.append(diceroll.return_dices_as_list())
            turn += 1

            return render_template('throw.html', title='Throw', form=form, turn=turn, dices=dicerolls_lists,
                                   game_id=game_id,
                                   player_name=human_player.player_name, categories=categories)

        else:
            computer_player = ComputerPlayer.query.get(int(player_id))
            curr_computer_player = computer_player.check_ai_and_return_object()

            choice = 0

            if (turn == 2) or (turn == 3):
                if isinstance(curr_computer_player, ComputerPlayerSmart):
                    if turn == 2:
                        diceroll.assign_dices(dicerolls_objects_lists[0])
                    elif turn == 3:
                        diceroll.assign_dices(dicerolls_objects_lists[1])
                    choice = curr_computer_player.decide(diceroll.return_dices_as_list())
                elif isinstance(curr_computer_player, ComputerPlayerDummy):
                    choice = random.randint(1, 3)

            if (turn == 1) or (choice == 1):  # choice = 1 oznacza rzut wszystkimi
                dicerolls_lists.append(diceroll.throw_all_rand(player_id, game_id))
                flash('All dices thrown')
                turn += 1
                return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
                                       dices=dicerolls_lists, game_id=game_id, player_name=player.player_name)

            elif (choice == 2) and ((turn == 2) or (turn == 3)):  # wybór czym rzucić
                if isinstance(curr_computer_player, ComputerPlayerDummy):
                    if turn == 2:
                        diceroll.assign_dices(dicerolls_objects_lists[0])
                    elif turn == 3:
                        diceroll.assign_dices(dicerolls_objects_lists[1])
                    ticked_boxes = curr_computer_player.randomly_select_dices(diceroll, game_id)
                    dicerolls_lists.append(diceroll.return_dices_as_list())
                    flash('Computer selected dice with number/s: {} to throw again'.format(sorted(ticked_boxes)))
                    if turn == 2:
                        session['diceroll_2_id'] = diceroll.id
                    elif turn == 3:
                        session['diceroll_3_id'] = diceroll.id
                    turn += 1

                elif isinstance(curr_computer_player, ComputerPlayerSmart):
                    if turn == 2:
                        diceroll.assign_dices(dicerolls_objects_lists[0])
                    elif turn == 3:
                        diceroll.assign_dices(dicerolls_objects_lists[1])

                    dum_comp = ComputerPlayerDummy.query.get(player_id)
                    ticked_boxes = dum_comp.randomly_select_dices(diceroll, game_id)

                    #ticked_boxes = curr_computer_player.choose_which_dices_to_select(diceroll, game_id)

                    dicerolls_lists.append(diceroll.return_dices_as_list())
                    flash('Computer selected dice with number/s: {} to throw again'.format(sorted(ticked_boxes)))
                    if turn == 2:
                        session['diceroll_2_id'] = diceroll.id
                    elif turn == 3:
                        session['diceroll_3_id'] = diceroll.id
                    turn += 1

                return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
                                       dices=dicerolls_lists, game_id=game_id, player_name=player.player_name)

            elif (choice == 3) or (turn == 4):
                return redirect(url_for('category_blueprint.category', game_id=game_id, player_id=player_id))

    if player_id in game.get_list_of_human_players_ids():
        human_player = HumanPlayer.query.get(int(player_id))
        return render_template('throw.html', title='Throw', form=form, turn=turn,
                               game_id=game_id, dices=dicerolls_lists,
                               player_name=human_player.player_name)
    else:
        return render_template('computerthrow.html', title='Throw', form=form, turn=turn, game_id=game_id,
                               player_name=player.player_name, dices=dicerolls_lists)
