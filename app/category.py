from flask import render_template, flash, redirect, url_for, session, Blueprint
from app.forms import *
from app.models.diceroll import *
from app.models.category import *
from app.models.computerPlayer import *

category_blueprint = Blueprint('category_blueprint', __name__)

@category_blueprint.route('/category/<int:gameid>/<int:playerid>', methods=['GET','POST'])
def category(gameid, playerid):

    form = SelectCategoryForm()
    hide_checkboxes = False
    game = Game.query.get(gameid)
    player = Player.query.get(playerid)
    comp = []

    second_dice_id = 0 #todo: optymalizacja
    third_dice_id = 0
    if session.get('diceroll_3_id'):
        third_dice = last_dice = Diceroll.query.get(session['diceroll_3_id'])
        third_dice_id = third_dice.id
        session.get('diceroll_2_id')
        second_dice = Diceroll.query.get(session['diceroll_2_id'])
        second_dice_id = second_dice.id
        session.get('diceroll_1_id')
        first_dice = Diceroll.query.get(session['diceroll_1_id'])
        first_dice_id = first_dice.id
    elif session.get('diceroll_2_id'):
        second_dice = last_dice = Diceroll.query.get(session['diceroll_2_id'])
        second_dice_id = second_dice.id
        session.get('diceroll_1_id')
        first_dice = Diceroll.query.get(session['diceroll_1_id'])
        first_dice_id = first_dice.id
    elif session.get('diceroll_1_id'):
        first_dice = last_dice = Diceroll.query.get(session['diceroll_1_id'])
        first_dice_id = first_dice.id
    last_diceroll = last_dice.return_dices_as_list()

    if not form.submit_next_player.data:
        if playerid not in game.get_list_of_human_players_ids():
            computer_player = ComputerPlayer(playerid)
            category = Category()
            cat_name = category.choose_rand_cat_and_count_result(last_diceroll)
            computer_player.insert_part_result(gameid, cat_name, category.result, first_dice_id, second_dice_id, third_dice_id)
            hide_checkboxes = True
            comp.append(True)
            comp.append(cat_name)

    cat_results = player.generate_dict_of_part_results(gameid)

    if form.validate_on_submit():

        if form.submit_the_box.data:
            category = Category()
            form_dict = form.__dict__
            for key in form_dict.items():
                if key[0] in category.names:
                    cat_dict = key[1].__dict__
                    if cat_dict['data']:
                        getattr(category, key[0] + '_count')(last_diceroll)
                        player.insert_part_result(gameid, key[0], category.result, first_dice_id, second_dice_id, third_dice_id)
                        cat_results[str(key[0])] = category.result
                        hide_checkboxes = True


                        return render_template('category.html', title='Category Selection', form=form,hide_checkboxes=hide_checkboxes, player_name=player.player_name, last_diceroll=last_diceroll, cat_results=cat_results, sum=sum, computer=comp)

        elif form.submit_next_player.data: # todo: przycisk label end of the game jak juz wszyscy rzucili

            # gameresult = Gameresult() # do testow
            # gameresult.update_results(gameid)
            # return redirect(url_for('gameend', gameid=gameid))

            game = Game.query.get(int(gameid))
            players = game.get_list_of_all_players_ids()
            curr_player_pos = players.index(playerid)

            if curr_player_pos != len(players)-1:
                playerid = players[int(curr_player_pos + 1)]
            else:
                if 14 == player.get_no_of_turns(gameid):
                    gameresult = Gameresult()
                    gameresult.update_results(gameid)
                    return redirect(url_for('gameend', gameid=gameid))
                else:
                    playerid = players[0]

            # game = Game.query.get(int(gameid))
            # human_players = game.get_list_of_human_players_ids()
            # curr_player_pos = human_players.index(playerid)
            #
            # if curr_player_pos != len(human_players)-1:
            #     playerid = human_players[int(curr_player_pos + 1)]
            # else:
            #     if 14 == player.get_no_of_turns(gameid):
            #         gameresult = Gameresult()
            #         gameresult.update_results(gameid)
            #         return redirect(url_for('gameend', gameid=gameid))
            #     else:
            #         playerid = human_players[0]

            session.pop('diceroll_1_id', None)
            session.pop('diceroll_2_id', None)
            session.pop('diceroll_3_id', None)

            player_name =  db.session.query(Player.player_name).filter(Player.id == playerid).scalar()
            flash('The current player is: {}'.format(player_name))
            return redirect(url_for('throw_blueprint.throw', gameid=gameid, playerid=playerid))

    return render_template('category.html', title='Category Selection', form=form, hide_checkboxes=hide_checkboxes, player_name=player.player_name, last_diceroll=last_diceroll, cat_results=cat_results, sum=sum, computer=comp)
