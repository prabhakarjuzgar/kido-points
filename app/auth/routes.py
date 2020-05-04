from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.auth.forms import LoginForm, RegisterationForm
# from app.main import bp
from app import logger
from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("Login")
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.user', username=current_user.username)
        return redirect(next_page)
    return render_template('auth/login.html', title='LogIn', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    logger.debug('Register. Request.method %s', request.method)
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    form = RegisterationForm()
    logger.debug('validate_on_submit - %d', form.validate_on_submit())
    if form.validate_on_submit():
        logger.debug('Register User POST %s', form.username.data)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering')
        return redirect(url_for('auth.login'))

    logger.debug('Register User GET %s', form.username.data)
    return render_template('auth/register.html', title='SignIn', form=form)
