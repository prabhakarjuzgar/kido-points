from app import create_app, db
from app.models import User, Child, Activity

application = create_app()

@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'Child':Child,
            'Activity': Activity}
