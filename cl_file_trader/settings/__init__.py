import os

env = os.environ.get("DJANGO_ENV", "development")

# from .development import *
if env == "production":
    from .production import *
elif env == "testing":
    from .development import *  # tests use dev DB/settings
else:
    from .development import *
