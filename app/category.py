from flask import render_template, flash, redirect, url_for, session, Blueprint
from app.forms import *
from app.models.diceroll import *
from app.models.category import *

category_blueprint = Blueprint('category_blueprint', __name__)

@category_blueprint.route('/category/<int:gameid>/<int:playerid>', methods=['GET','POST'])
def category(gameid, playerid):

    form = SelectCategoryForm()
    hide_checkboxes = False
    player = Player.query.get(playerid)

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
                        turn_id = player.insert_part_result(gameid, key[0], category.result, first_dice_id, second_dice_id, third_dice_id)
                        return render_template('category.html', title='Category Selection', form=form,hide_checkboxes=hide_checkboxes, player_name=player.player_name, last_diceroll=last_diceroll, cat_results=cat_results)

        elif form.submit_next_player.data:
            # wyczysc dane diceroll, itp
            # zmien playera

            return redirect(url_for('throw_blueprint.throw', gameid=gameid, playerid=playerid))
    return render_template('category.html', title='Category Selection', form=form, hide_checkboxes=hide_checkboxes, player_name=player.player_name, last_diceroll=last_diceroll, cat_results=cat_results)



