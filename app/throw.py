from flask import render_template, flash, redirect, url_for, session, Blueprint
from app import app
from app.forms import *
from app.models.diceroll import *
from app.category import category_blueprint
from app.models.player import *

app.register_blueprint(category_blueprint)

throw_blueprint = Blueprint('throw_blueprint', __name__)

@throw_blueprint.route('/throw/<int:gameid>/<int:playerid>', methods=['GET', 'POST'])
def throw(gameid, playerid):

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

    game = Game.query.get(int(gameid))
    form = ThrowForm()
    if form.validate_on_submit():
        diceroll = Diceroll()
        if playerid in game.get_list_of_human_players_ids():

            if form.throw_sel.data:
                if turn > 1:
                    diceroll = Diceroll()
                    if turn == 2:
                        diceroll.assign_dices(diceroll_1)
                    elif turn == 3:
                        diceroll.assign_dices(diceroll_2)

                    sel_dices = []
                    for i in range(1,6):
                        form_dice_sel = getattr(form, 'dice' + str(i))
                        sel_dices.append(form_dice_sel.data)
                    diceroll.check_selected_get_random_numbers_and_insert(sel_dices)
                    flash('Selected dices thrown')

            elif form.throw_all.data:
                dicerolls_lists.append(diceroll.throw_all_rand())
                if 'diceroll_1_id' not in session:
                    session['diceroll_1_id'] = diceroll.id
                elif 'diceroll_2_id' not in session:
                    session['diceroll_2_id'] = diceroll.id
                else:
                    session['diceroll_3_id'] = diceroll.id
                flash('All dices thrown')

            elif form.keep.data or form.cat_sel:
                return redirect(url_for('category_blueprint.category', gameid=gameid, playerid=playerid))

            dicerolls_lists.append(diceroll.return_dices_as_list())
            if turn == 2:
                session['diceroll_2_id'] = diceroll.id
            elif turn == 3:
                session['diceroll_3_id'] = diceroll.id
            turn += 1
            return render_template('throw.html', title='Throw', form=form, turn=turn, dices=dicerolls_lists, cat_results={})

        else:
            computer_player = ComputerPlayer.query.get(int(playerid))
            curr_computer_player = computer_player.check_ai_and_return_object()

            choice = 0
            if (turn == 2) or (turn == 3):
                choice = random.randint(1,3)

            if (turn == 1) or (choice == 1): # choice = 1 oznacza rzut wszystkimi
                dicerolls_lists.append(diceroll.throw_all_rand())
                if 'diceroll_1_id' not in session:
                    session['diceroll_1_id'] = diceroll.id
                elif 'diceroll_2_id' not in session:
                    session['diceroll_2_id'] = diceroll.id
                else:
                    session['diceroll_3_id'] = diceroll.id
                flash('All dices thrown')
                turn += 1
                return render_template('computerthrow.html', title='Throw', form=form, turn=turn, dices=dicerolls_lists, cat_results={})

            elif (choice == 2) and (turn == 2) or (turn == 3): # wybór czym rzucić
                if isinstance(curr_computer_player, ComputerPlayerDummy):
                    if turn == 2:
                        diceroll.assign_dices(diceroll_1)
                    elif turn == 3:
                        diceroll.assign_dices(diceroll_2)
                    ticked_boxes = curr_computer_player.randomly_select_dices(diceroll)
                    dicerolls_lists.append(diceroll.return_dices_as_list())
                    flash('Computer selected dices with number(/s): {} to throw again'.format(sorted(ticked_boxes)))
                    turn += 1
                    if turn == 2:
                        session['diceroll_2_id'] = diceroll.id
                    elif turn == 3:
                        session['diceroll_3_id'] = diceroll.id
                return render_template('computerthrow.html', title='Throw', form=form, turn=turn, dices=dicerolls_lists, cat_results={})

            elif (choice == 3) or (turn == 4): # wybór kategorii
                return redirect(url_for('category_blueprint.category', gameid=gameid, playerid=playerid))
    if playerid in game.get_list_of_human_players_ids():
        return render_template('throw.html', title='Throw', form=form, turn=turn)
    else:
        return render_template('computerthrow.html', title='Throw', form=form, turn=turn)
