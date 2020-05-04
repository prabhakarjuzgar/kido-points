from datetime import datetime
from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)
from flask_login import current_user, login_required
from sqlalchemy import func
from app import db
from app.models import User, Child, Activity, Target
from app.main.forms import (RegisterationFormChild,
                            RegisterationFormActivity,
                            SetTarget,
                            RegisterationFormActivityModify)
from app.main import bp
from app import logger


@bp.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('base.html', title='Home')

@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    children = Child.query.filter_by(parentid=user.id).all()
    logger.debug('Home page')
    return render_template('user.html', title='Home', children=children)

@bp.route('/<username>/addchild', methods=['GET', 'POST'])
@login_required
def addchild(username: str):
    logger.debug('AddChild. Request.method %s', request.method)
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = RegisterationFormChild()
    logger.debug('validate_on_submit - %d', form.validate_on_submit())
    if form.validate_on_submit():
        logger.debug('Add child %s', form.childname.data)
        logger.debug(current_user)
        user = User.query.filter_by(username=current_user.username).first()
        child = Child(childname=form.childname.data, parentid=user.id)
        db.session.add(child)
        db.session.commit()
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('addchild.html', title='AddChild', form=form)

@bp.route('/<username>/child/<childname>', methods=['GET', 'POST'])
@login_required
def child(username: str, childname: str):
    logger.debug('Child. Request.method %s', request.method)
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=current_user.username).first_or_404()
    child1 = Child.query.filter_by(childname=childname, parentid=user.id).first_or_404()
    activities = Activity.query.filter_by(childid=child1.id).all()
    cur_points = Activity.query.with_entities(
        func.sum(Activity.points).label("sum")).filter_by(childid=child1.id).first()
    target = Target.query.filter_by(childid=child1.id).first()

    print("CURRENT POINTS {}".format(cur_points.sum))

    return render_template('child.html', title=childname,
                           activity=activities,
                           target=target,
                           childname=childname,
#                           childid=child1.id,
                           cur_points=cur_points)

@bp.route('/<username>/<childname>/addactivity', methods=['GET', 'POST'])
@login_required
def addactivity(username: str, childname: str):
    logger.debug('AddActivity. Request.method %s', request.method)
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=current_user.username).first_or_404()
    child1 = Child.query.filter_by(childname=childname, parentid=user.id).first_or_404()

    form = RegisterationFormActivity()
    form.childid = child1.id


    if form.validate_on_submit():
        logger.debug('Add activity %s', form.activity.data)
        logger.debug('childname %s, childid %d', childname, child1.id)
        logger.debug(current_user)
        activity = Activity(activity=form.activity.data, points=form.points.data, childid=child1.id)
        db.session.add(activity)
        db.session.commit()
        return redirect(url_for('main.child',
                                childname=childname,
                                username=current_user.username))
    return render_template('addactivity.html', title='AddActivity', form=form)

@bp.route('/<username>/<childname>/activity/<int:id>', methods=['GET', 'POST'])
@login_required
def activity(username:str, childname: str, id: int):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    act = Activity.query.filter_by(id=id).first_or_404()

    return render_template('activity.html',
                           title='Activity',
                           act=act,
                           username=username,
                           childname=childname,
                           id=id)

@bp.route('/<username>/<childname>/modify-activity/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_activity(username:str, childname: str, id: int):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=current_user.username).first_or_404()
    child1 = Child.query.filter_by(childname=childname, parentid=user.id).first_or_404()
    form = RegisterationFormActivityModify()

    act = Activity.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        print("UPDATE POINTS {}".format(form.points.data))
        act.points = form.points.data
        db.session.commit()
        return redirect(url_for('main.activity',
                        username=username,
                        childname=childname,
                        id=id))

    form.activity.data = act.activity
    form.points.data = act.points

    return render_template('modifyactivity.html',
                           title='Modify Activity Points',
                           form=form, 
                           act=act,
                           username=username,
                           childname=childname,
                           id=id)


@bp.route('/<username>/<childname>/target', methods=['GET', 'POST'])
@login_required
def set_target(username: str, childname: str):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    print("RENDER TARGET.HTML qqqq")
    user = User.query.filter_by(username=current_user.username).first_or_404()
    child1 = Child.query.filter_by(childname=childname, parentid=user.id).first_or_404()
    form = SetTarget()
    form.childid = child1.id

    target = Target.query.filter_by(childid=child1.id).first()
    if target is not None:
        flash('Target has already been set')

    if form.validate_on_submit():
        target = Target(target=form.target.data, childid=child1.id)
        db.session.add(target)
        db.session.commit()
        return redirect(url_for('main.child',
                                childname=childname,
                                username=username))

    print("RENDER TARGET.HTML")
    return render_template('settarget.html', title='Set Target', form=form)
