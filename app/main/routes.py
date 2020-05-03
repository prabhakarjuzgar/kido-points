from datetime import datetime
from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request,
                   g,
                   jsonify,
                   current_app,
                   session)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse
from sqlalchemy import func
# from app.main.forms import EditProfileForm, PostForm
from app import db
from app.models import User, Child, Activity, Target
from app.main.forms import (LoginForm,
                            RegisterationForm,
                            RegisterationFormChild,
                            RegisterationFormActivity,
                            SetTarget,
                            RegisterationFormActivityModify)
from app.main import bp
from app import logger

@bp.errorhandler(405)
def method_not_allowed():
    import pdb; pdb.set_trace()
    return make_response(render_template("405.html"), 400)

@bp.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/<username>', methods=['GET', 'POST'])
@login_required
def index(username: str):
    children = Child.query.filter_by(parentid=current_user.id).all()
    logger.debug('Home page')
    return render_template('index.html', title='Home', children=children)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("Login")
    if current_user.is_authenticated:
        return redirect(url_for('main.index', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index', username=current_user.username)
        return redirect(next_page)
    return render_template('login.html', title='LogIn', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    logger.debug('Register. Request.method %s', request.method)
    if current_user.is_authenticated:
        return redirect(url_for('main.index', username=current_user.username))
    form = RegisterationForm()
    logger.debug('validate_on_submit - %d', form.validate_on_submit())
    if form.validate_on_submit():
        logger.debug('Register User POST %s', form.username.data)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering')
        return redirect(url_for('main.login'))

    logger.debug('Register User GET %s', form.username.data)
    return render_template('register.html', title='SignIn', form=form)

@bp.route('/<username>/addchild', methods=['GET', 'POST'])
@login_required
def addchild(username: str):
    logger.debug('AddChild. Request.method %s', request.method)
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    form = RegisterationFormChild()
    logger.debug('validate_on_submit - %d', form.validate_on_submit())
    if form.validate_on_submit():
        logger.debug('Add child %s', form.childname.data)
        logger.debug(current_user)
        user = User.query.filter_by(username=current_user.username).first()
        child = Child(childname=form.childname.data, parentid=user.id)
        db.session.add(child)
        db.session.commit()
        return redirect(url_for('main.index', username=current_user.username))
    return render_template('addchild.html', title='AddChild', form=form)

@bp.route('/<username>/child/<childname>', methods=['GET', 'POST'])
@login_required
def child(username: str, childname: str):
    logger.debug('Child. Request.method %s', request.method)
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
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
        return redirect(url_for('main.login'))

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

@bp.route('/<username>/<childname>/activity/<id>', methods=['GET', 'POST'])
@login_required
def activity(username:str, childname: str, id: int):
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    act = Activity.query.filter_by(id=id).first_or_404()

    return render_template('activity.html',
                           title='Activity',
                           act=act,
                           username=username,
                           childname=childname,
                           id=id)

@bp.route('/<username>/<childname>/modify-activity/<id>', methods=['GET', 'POST'])
@login_required
def modify_activity(username:str, childname: str, id: int):
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

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
        return redirect(url_for('main.login'))

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
