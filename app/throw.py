from flask import render_template, flash, redirect, url_for, session, Blueprint
from app import app
from app.forms import *
from app.models.diceroll import *
from app.category import category_blueprint

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
                    diceroll.check_selected_get_random_numbers_and_insert(form.dice1.data, form.dice2.data, form.dice3.data, form.dice4.data, form.dice5.data)
                    flash('Selected dices thrown')

            elif form.throw_all.data:
                diceroll.generate_all_rand_dices_and_insert_to_db()
                dicerolls_lists.append(diceroll.return_dices_as_list())
                flash('All dices thrown')

            elif form.keep.data or form.cat_sel:
                return redirect(url_for('category_blueprint.category', gameid=gameid, playerid=playerid))

            dicerolls_lists.append(diceroll.return_dices_as_list())
            if turn == 1:
                session['diceroll_1_id'] = diceroll.id
            elif turn == 2:
                session['diceroll_2_id'] = diceroll.id
            elif turn == 3:
                session['diceroll_3_id'] = diceroll.id
            turn += 1
            return render_template('throw.html', title='Throw', form=form, turn=turn, dices=dicerolls_lists, cat_results={})

        else:

            if turn == 1:
                diceroll.generate_all_rand_dices_and_insert_to_db()
                dicerolls_lists.append(diceroll.return_dices_as_list())
                flash('All dices thrown')
                session['diceroll_1_id'] = diceroll.id
                turn += 1
                return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
                                       dices=dicerolls_lists, cat_results={})

            if turn == 2 or 3:
                b = 4
                return redirect(url_for('category_blueprint.category', gameid=gameid, playerid=playerid))
                # wez 1. lub 2. diceroll i przeanalizuj co zrobic

                #if wybor kategorii:
                #   return redirect(url_for('category_blueprint.category', gameid=gameid, playerid=playerid))

                # if throw selected:
                #   przeanalizuj ktorymi i rzuc
                #   dodaj diceroll 2 lub 3 do bazy

                # if throw all:
                #     diceroll.generate_all_rand_dices_and_insert_to_db()
                #     dicerolls_lists.append(diceroll.return_dices_as_list())
                #     flash('All dices thrown')
                #     return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
                #                            dices=dicerolls_lists, cat_results={})
                # dodaj 2 lub 3 rzut do bazy


            # if form.comp_next_step.data:
            #     if form.throw_sel.data:
            #         if turn > 1:
            #             diceroll = Diceroll()
            #             if turn == 2:
            #                 diceroll.assign_dices(diceroll_1)
            #             elif turn == 3:
            #                 diceroll.assign_dices(diceroll_2)
            #             diceroll.check_selected_get_random_numbers_and_insert(form.dice1.data, form.dice2.data,
            #                                                                   form.dice3.data, form.dice4.data,
            #                                                                   form.dice5.data)
            #             flash('Selected dices thrown')
            #
            #
            #     elif form.keep.data or form.cat_sel:
            #         return redirect(url_for('category_blueprint.category', gameid=gameid, playerid=playerid))
            #
            #
            #     return render_template('computerthrow.html', title='Throw', form=form, turn=turn,
            #                            dices=dicerolls_lists, cat_results={})

            # dicerolls_lists.append(diceroll.return_dices_as_list())
            # if turn == 1:
            #     session['diceroll_1_id'] = diceroll.id
            # elif turn == 2:
            #     session['diceroll_2_id'] = diceroll.id
            # elif turn == 3:
            #     session['diceroll_3_id'] = diceroll.id
            # turn += 1
    if playerid in game.get_list_of_human_players_ids():
        return render_template('throw.html', title='Throw', form=form, turn=turn)
    else:
        return render_template('computerthrow.html', title='Throw', form=form, turn=turn)
