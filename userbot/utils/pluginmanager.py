import importlib
import sys
from pathlib import Path

from userbot import CMD_HELP, LOAD_PLUG

from ..Config import Config
from ..core import LOADED_CMDS, PLG_INFO
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..core.session import catub
from ..helpers.utils import _format

LOGS = logging.getLogger("CatUserbot")


def load_module(shortname, plugin_path=None):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        path = Path(f"userbot/plugins/{shortname}.py")
        checkplugins(path)
        name = "userbot.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        LOGS.info(f"Successfully imported {shortname}")
    else:
        if plugin_path is None:
            path = Path(f"userbot/plugins/{shortname}.py")
            name = f"userbot.plugins.{shortname}"
        else:
            path = Path((f"{plugin_path}/{shortname}.py"))
            name = f"{plugin_path}/{shortname}".replace("/", ".")
        checkplugins(path)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        mod.bot = catub
        mod.LOGS = LOGS
        mod.Config = Config
        mod._format = _format
        mod.tgbot = catub.tgbot
        mod.CMD_HELP = CMD_HELP
        mod.edit_delete = edit_delete
        od.parse_pre = _format.parse_pre
        mod.edit_or_reply = edit_or_reply
        mod.logger = logging.getLogger(shortname)
        mod.borg = catub
        spec.loader.exec_module(mod)
        # for imports
        sys.modules[f"userbot.plugins.{shortname}"] = mod
        LOGS.info(f"Successfully imported {shortname}")


def checkplugins(filename):
    with open(filename, "r") as f:
        filedata = f.read()
    filedata = filedata.replace("sendmessage", "send_message")
    filedata = filedata.replace("sendfile", "send_file")
    filedata = filedata.replace("editmessage", "edit_message")
    with open(filename, "w") as f:
        f.write(filedata)
