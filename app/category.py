from flask import render_template, flash, redirect, url_for, session, Blueprint
from app.forms import *
from app.models.diceroll import *
from app.models.category import *
from app.models.player import *
from flask_login import login_required

category_blueprint = Blueprint('category_blueprint', __name__)


@category_blueprint.route('/category/<int:game_id>/<int:player_id>', methods=['GET', 'POST'])
@login_required
def category(game_id, player_id):
    game = Game.query.get(game_id)
    player = Player.query.get(player_id)
    dicerolls_objects_list = player.find_unassigned_dicerolls(game_id)
    dicerolls_ids = []

    for diceroll_obj in dicerolls_objects_list:
        dicerolls_ids.append(diceroll_obj.id)

    if dicerolls_ids:
        last_diceroll_obj = Diceroll.query.get(dicerolls_ids[len(dicerolls_ids) - 1])
        last_diceroll = last_diceroll_obj.return_dices_as_list()

    dicerolls_data = {}
    dicerolls_data['first_dice_id'], dicerolls_data['second_dice_id'], dicerolls_data['third_dice_id'] = 0, 0, 0

    if len(dicerolls_ids) >= 1:
        dicerolls_data['first_dice_id'] = dicerolls_ids[0]
        if len(dicerolls_ids) >= 2:
            dicerolls_data['second_dice_id'] = dicerolls_ids[1]
            if len(dicerolls_ids) == 3:
                dicerolls_data['third_dice_id'] = dicerolls_ids[2]

    if player_id not in game.get_list_of_human_players_ids():
        computer_player = ComputerPlayer.query.get(int(player_id))
        curr_computer_player = computer_player.check_ai_and_return_object()

        if isinstance(curr_computer_player, ComputerPlayerDummy):
            picked_category = curr_computer_player.choose_rand_cat_and_count_result(last_diceroll, game_id)
        elif isinstance(curr_computer_player, ComputerPlayerSmart):
            picked_category = curr_computer_player.choose_cat_and_count_result(last_diceroll, game_id)

        curr_computer_player.insert_part_result(game_id, picked_category['name'], picked_category['result'],
                                                dicerolls_data['first_dice_id'], dicerolls_data['second_dice_id'],
                                                dicerolls_data['third_dice_id'])

        return redirect(url_for('showcategory', game_id=game_id, player_id=player_id))

    form = SelectCategoryForm()

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

    if form.validate_on_submit():

        if form.submit_the_box.data:
            for radio in choices:
                if radio.checked:
                    method_name = ((radio.label).lower()).replace(' ', '_')
                    getattr(category, method_name + '_count')(last_diceroll)
                    player.insert_part_result(game_id, radio.label, category.result, dicerolls_data['first_dice_id'],
                                              dicerolls_data['second_dice_id'], dicerolls_data['third_dice_id'])
                    radio.result = category.result
                    total += radio.result

                    return redirect(url_for('showcategory', game_id=game_id, player_id=player_id))

    return render_template('category.html', title='Category Selection', form=form,
                           player_name=player.player_name, last_diceroll=last_diceroll, total=total,
                           choices=choices,
                           hasattr=hasattr, game_id=game_id)
