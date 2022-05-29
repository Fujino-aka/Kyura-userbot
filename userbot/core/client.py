import asyncio
import datetime
import inspect
import re
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Union

from telethon import TelegramClient, events
from telethon.errors import (
    AlreadyInConversationError,
    BotInlineDisabledError,
    BotResponseTimeoutError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageIdInvalidError,
    MessageNotModifiedError,
)

from ..Config import Config
from ..utils.utils import runcmd
from . import BOT_INFO, CMD_INFO, GRP_INFO, LOADED_CMDS, PLG_INFO
from .cmdinfo import _format_about
from .data import blacklist_chats_list
from .events import *
from .logger import logging
from .managers import edit_delete
from .pluginManager import get_message_link, restart_script

LOGS = logging.getLogger(__name__)


class REGEX:
    def __init__(self):
        self.regex = ""
        self.regex1 = ""
        self.regex2 = ""


REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()


class CatUserBotClient(TelegramClient):
    def cat_cmd(
        self: TelegramClient,
        pattern: str or tuple = None,
        info: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]
        or tuple = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        edited: bool = True,
        forword=False,
        disable_errors: bool = False,
        command: str or tuple = None,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)
        if gvarstatus("blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()
        stack = inspect.stack()
        previous_stack_frame = stack[1]
        file_test = Path(previous_stack_frame.filename)
        file_test = file_test.stem.replace(".py", "")
        
        def decorator(func):  # sourcery no-metrics
            async def wrapper(check):  # sourcery no-metrics
                if groups_only and not check.is_group:
                    return await edit_delete(
                        check, "`I don't think this is a group.`", 10
                    )
                if private_only and not check.is_private:
                    return await edit_delete(
                        check, "`I don't think this is a personal Chat.`", 10
                    )
                try:
                    await func(check)
                except events.StopPropagation as e:
                    raise events.StopPropagation from e
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("Message was same as previous message")
                except MessageIdInvalidError:
                    LOGS.error("Message was deleted or cant be found")
                except BotInlineDisabledError:
                    await edit_delete(check, "`Turn on Inline mode for our bot`", 10)
                except ChatSendStickersForbiddenError:
                    await edit_delete(
                        check, "`I guess i can't send stickers in this chat`", 10
                    )
                except BotResponseTimeoutError:
                    await edit_delete(
                        check, "`The bot didnt answer to your query in time`", 10
                    )
                except ChatSendMediaForbiddenError:
                    await edit_delete(check, "`You can't send media in this chat`", 10)
                except AlreadyInConversationError:
                    await edit_delete(
                        check,
                        "`A conversation is already happening with the given chat. try again after some time.`",
                        10,
                    )
                except ChatSendInlineForbiddenError:
                    await edit_delete(
                        check, "`You can't send inline messages in this chat.`", 10
                    )
                except FloodWaitError as e:
                    LOGS.error(
                        f"A flood wait of {e.seconds} occured. wait for {e.seconds} seconds and try"
                    )
                    await check.delete()
                    await asyncio.sleep(e.seconds + 5)
                except BaseException as e:
                    LOGS.exception(e)
                    
            from .session import catub

            if not func.__doc__ is None:
                CMD_INFO[command[0]].append((func.__doc__).strip())
            if pattern is not None:
                if command is not None:
                    if command[0] in LOADED_CMDS and wrapper in LOADED_CMDS[command[0]]:
                        return None
                    try:
                        LOADED_CMDS[command[0]].append(wrapper)
                    except BaseException:
                        LOADED_CMDS.update({command[0]: [wrapper]})
                if edited:
                    catub.add_event_handler(
                        wrapper,
                        MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                    )
                catub.add_event_handler(
                    wrapper,
                    NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                )
                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        if edited:
                            catub.add_event_handler(
                                wrapper,
                                MessageEdited(
                                    pattern=REGEX_.regex2,
                                    from_users=_sudousers_list(),
                                    **kwargs,
                                ),
                            )
                        catub.add_event_handler(
                            wrapper,
                            NewMessage(
                                pattern=REGEX_.regex2,
                                from_users=_sudousers_list(),
                                **kwargs,
                            ),
                        )
            else:
                if file_test in LOADED_CMDS and func in LOADED_CMDS[file_test]:
                    return None
                try:
                    LOADED_CMDS[file_test].append(func)
                except BaseException:
                    LOADED_CMDS.update({file_test: [func]})
                if edited:
                    catub.add_event_handler(func, events.MessageEdited(**kwargs))
                catub.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper

        return decorator

    def bot_cmd(
        self: TelegramClient,
        disable_errors: bool = False,
        edited: bool = False,
        forword=False,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)

        def decorator(func):
            async def wrapper(check):
                try:
                    await func(check)
                except events.StopPropagation as e:
                    raise events.StopPropagation from e
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("Message was same as previous message")
                except MessageIdInvalidError:
                    LOGS.error("Message was deleted or cant be found")
                except BaseException as e:
                    # Check if we have to disable error logging.
                    LOGS.exception(e)  # Log the error in console
                    if not disable_errors:

            from .session import catub

            if edited is True:
                catub.tgbot.add_event_handler(func, events.MessageEdited(**kwargs))
            else:
                catub.tgbot.add_event_handler(func, events.NewMessage(**kwargs))

            return wrapper

        return decorator

    async def get_traceback(self, exc: Exception) -> str:
        return "".join(
            traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
        )

    def _kill_running_processes(self) -> None:
        """Kill all the running asyncio subprocessess"""
        for _, process in self.running_processes.items():
            try:
                process.kill()
                LOGS.debug("Killed %d which was still running.", process.pid)
            except Exception as e:
                LOGS.debug(e)
        self.running_processes.clear()


CatUserBotClient.fast_download_file = download_file
CatUserBotClient.fast_upload_file = upload_file
CatUserBotClient.reload = restart_script
CatUserBotClient.get_msg_link = get_message_link
CatUserBotClient.check_testcases = checking
try:
    send_message_check = TelegramClient.send_message
except AttributeError:
    CatUserBotClient.send_message = send_message
    CatUserBotClient.send_file = send_file
    CatUserBotClient.edit_message = edit_message
