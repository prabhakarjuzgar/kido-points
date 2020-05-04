"""Class representing login form"""
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from app.models import Child, Activity, Target
from app import logger


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
