from flask import render_template, flash, redirect, url_for, session, Blueprint
from app.forms import *
from app.models import *
import random

throw_blueprint = Blueprint('throw_blueprint', __name__)

@throw_blueprint.route('/throw/<int:gameid>', methods=['GET', 'POST'])
def throw(gameid):      # podzielic funkcję na 3 czesci w zaleznosci od wybranego submita???
    turn = 1
    list_diceroll_1, list_diceroll_2, list_diceroll_3 = [], [], []
    if session.get('diceroll_1_id'):
        class_diceroll_1 = Diceroll.query.get(session['diceroll_1_id'])
        list_diceroll_1 = class_diceroll_1.return_dices_as_list()
        turn = 2
        if session.get('diceroll_2_id'):
            class_diceroll_2 = Diceroll.query.get(session['diceroll_2_id'])
            list_diceroll_2 = class_diceroll_2.return_dices_as_list()
            turn = 3
    form = ThrowForm()
    if form.validate_on_submit():
        if form.throw_sel.data:
            if turn > 1:
                diceroll_to_db = Diceroll()
                if turn == 2:
                    diceroll_to_db = class_diceroll_1
                elif turn == 3:
                    diceroll_to_db = class_diceroll_2
                if form.dice1.data:
                    diceroll_to_db.dice1 = random.randint(1, 6)
                if form.dice2.data:
                    diceroll_to_db.dice2 = random.randint(1, 6)
                if form.dice3.data:
                    diceroll_to_db.dice3 = random.randint(1, 6)
                if form.dice4.data:
                    diceroll_to_db.dice5 = random.randint(1, 6)
                if form.dice5.data:
                    diceroll_to_db.dice5 = random.randint(1, 6)
                flash('Selected dices thrown')
                db.session.add(diceroll_to_db)
                db.session.commit()
                if turn == 2:
                    session['diceroll_2_id'] = diceroll_to_db.id
                    class_diceroll_2 = Diceroll.query.get(session['diceroll_2_id'])
                    list_diceroll_2 = class_diceroll_2.return_dices_as_list()
                elif turn == 3:
                    session['diceroll_3_id'] = diceroll_to_db.id
                    class_diceroll_3 = Diceroll.query.get(session['diceroll_3_id'])
                    list_diceroll_3 = class_diceroll_3.return_dices_as_list()
                turn += 1
                return render_template('throw.html', title='Throw', form=form, turn=turn, dices_1=list_diceroll_1,dices_2=list_diceroll_2, dices_3=list_diceroll_3)
        elif form.throw_all.data:
            diceroll_to_db = Diceroll()
            diceroll_to_db.generate_all_rand_dices()
            if turn == 1:
                list_diceroll_1 = diceroll_to_db.return_dices_as_list()
                db.session.add(diceroll_to_db)
                db.session.commit()
                session['diceroll_1_id'] = diceroll_to_db.id
            elif turn == 2:
                list_diceroll_2 = diceroll_to_db.return_dices_as_list()
                db.session.add(diceroll_to_db)
                db.session.commit()
                session['diceroll_2_id'] = diceroll_to_db.id
            elif turn == 3:
                list_diceroll_3 = diceroll_to_db.return_dices_as_list()
                db.session.add(diceroll_to_db)
                db.session.commit()
                session['diceroll_3_id'] = diceroll_to_db.id
            turn +=1
            flash('All dices thrown')
            return render_template('throw.html', title='Throw', form=form, turn=turn, dices_1=list_diceroll_1, dices_2=list_diceroll_2, dices_3=list_diceroll_3)
        elif form.keep.data or form.cat_sel.data:
            return redirect(url_for('category',gameid=gameid)) # todo complete
    return render_template('throw.html', title='Throw', form=form, turn=turn)