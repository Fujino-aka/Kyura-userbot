# config values will be loaded from here

import os

ENV = bool(os.environ.get("ENV", False))

if ENV:
    from config import Config  # noqa
elif os.path.exists("config.py"):
    from config import Development as Config  # noqa
