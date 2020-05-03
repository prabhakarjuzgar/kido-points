"""Class representing login form"""
from flask import g, current_app
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Child, Activity, Target
from app import logger


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('UserName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('LogIn')

class RegisterationForm(FlaskForm):
    username = StringField('UserName', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),
                                                             EqualTo('password')])
    submit = SubmitField('SignUp')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        logger.debug('User is %s', username.data)
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        logger.debug('Email is %s', email.data)
        if user is not None:
            raise ValidationError('Please use a different email address')

class RegisterationFormChild(FlaskForm):
    childname = StringField('ChildName', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_childname(self, childname):
        child = Child.query.filter_by(childname=childname.data, parentid=current_user.id).first()

        logger.debug('Child is %s', childname.data)
        if child is not None:
            raise ValidationError('Please use a different childname')

class RegisterationFormActivity(FlaskForm):
    activity = StringField('Activity', validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired()])
    submit = SubmitField('Add')
    childid: int = None

    def validate_activity(self, activity):
        logger.debug('Activity is %s', activity.data)
        logger.debug('CHILD ID %d', self.childid)
        act = Activity.query.filter_by(activity=activity.data, childid=self.childid).first()
        if act is not None:
            raise ValidationError('Activity already exists')

    def validate_points(self, points):
        logger.debug("Target is %d", points.data)
        if points.data < 0:
            raise ValidationError('Must be positive value')

class RegisterationFormActivityModify(FlaskForm):
    activity = StringField('Activity', render_kw={'readonly': True})
    points = IntegerField('Points', validators=[DataRequired()])
    submit = SubmitField('Modify')

    def validate_points(self, points):
        logger.debug("Target is %d", points.data)
        if points.data < 0:
            raise ValidationError('Must be positive value')


class SetTarget(FlaskForm):
    # activity = StringField('Activity', validators=[DataRequired()])
    target = IntegerField('Target', validators=[DataRequired()])
    submit = SubmitField('Set Target')
    childid: int = None

    def validate_target(self, target):
        tar = Target.query.filter_by(target=target.data, childid=self.childid).first()
        if tar is not None:
            raise ValidationError('Target is already set')

        if target.data < 0:
            raise ValidationError('Target points should be positive number')
