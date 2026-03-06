# Routes package
# Import to register routes with Flask app

from backend.routes import auth
from backend.routes import sessions
from backend.routes import rolls
from backend.routes import analytics
from backend.routes import diagnostics

# TODO: Uncomment as routes are built
# from backend.routes import analytics
# from backend.routes import dice_sets
# from backend.routes import training
# from backend.routes import skills
# from backend.routes import profile
# from backend.routes import elevenlabs
# from backend.routes import stripe_routes

__all__ = ['auth', 'sessions', 'rolls', 'analytics', 'diagnostics']
