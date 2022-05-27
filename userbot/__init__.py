import signal
import sys
import time

import heroku3

from .Config import Config
from .core.logger import logging
from .core.session import catub
from .helpers.utils.utils import runasync
from .sql_helper.globals import addgvar, delgvar, gvarstatus

__version__ = "3.1.1"
__license__ = "GNU Affero General Public License v3.0"
__author__ = "CatUserBot <https://github.com/TgCatUB/catuserbot>"
__copyright__ = f"CatUserBot Copyright (C) 2020 - 2021  {__author__}"

catub.version = __version__
catub.tgbot.version = __version__
LOGS = logging.getLogger("CatUserbot")
bot = catub

StartTime = time.time()
catversion = "3.1.1"


def close_connection(*_):
    print("Clossing Userbot connection.")
    runasync(catub.disconnect())
    sys.exit(143)


signal.signal(signal.SIGTERM, close_connection)



# Global Configiables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
CMD_LIST = {}
SUDO_LIST = {}
# for later purposes
INT_PLUG = ""
LOAD_PLUG = {}
