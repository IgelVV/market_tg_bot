import asyncio
import platform
import signal
import logging

from collections.abc import Coroutine, Iterable
from typing import Optional

from telegram.ext import Application
from telegram._utils.defaultvalue import (
    DEFAULT_NONE,
    DefaultValue,
)
from telegram._utils.warnings import warn

logger = logging.getLogger(__name__)


# copy-paste from Application
# with additional opportunity to run coroutines with application.start()
def run_polling(
        application: Application,
        side_coroutines: Optional[Iterable[Coroutine]] = None,
        poll_interval: float = 0.0,
        timeout: int = 10,
        bootstrap_retries: int = -1,
        read_timeout: float = 2,
        write_timeout=DEFAULT_NONE,
        connect_timeout=DEFAULT_NONE,
        pool_timeout=DEFAULT_NONE,
        allowed_updates=None,
        drop_pending_updates=None,
        close_loop: bool = True,
        stop_signals=DEFAULT_NONE,
) -> None:
    def error_callback(exce) -> None:
        application.create_task(
            application.process_error(error=exce, update=None))

    updater_coroutine = application.updater.start_polling(
        poll_interval=poll_interval,
        timeout=timeout,
        bootstrap_retries=bootstrap_retries,
        read_timeout=read_timeout,
        write_timeout=write_timeout,
        connect_timeout=connect_timeout,
        pool_timeout=pool_timeout,
        allowed_updates=allowed_updates,
        drop_pending_updates=drop_pending_updates,
        # error_callback=None,
        error_callback=error_callback,
        # if there is an error in fetching updates
    )

    # Calling get_event_loop() should still be okay even in py3.10+ as long as there is a
    # running event loop or we are in the main thread, which are the intended use cases.
    # See the docs of get_event_loop() and get_running_loop() for more info
    loop = asyncio.get_event_loop()

    if stop_signals is DEFAULT_NONE and platform.system() != "Windows":
        stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)

    try:
        if not isinstance(stop_signals, DefaultValue):
            for sig in stop_signals or []:
                loop.add_signal_handler(sig, application._raise_system_exit)
    except NotImplementedError as exc:
        warn(
            f"Could not add signal handlers for the stop signals {stop_signals} due to "
            f"exception `{exc!r}`. If your event loop does not implement `add_signal_handler`,"
            f" please pass `stop_signals=None`.",
            stacklevel=3,
        )

    try:
        loop.run_until_complete(application.initialize())
        if application.post_init:
            loop.run_until_complete(application.post_init(application))
        loop.run_until_complete(
            updater_coroutine)  # one of updater.start_webhook/polling

        async def gather_main_coro(side_coro: Optional[Iterable[Coroutine]]):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(application.start())
                if side_coro:
                    for coro in side_coro:
                        print(side_coro)
                        tg.create_task(coro)

        # main proces
        # loop.run_until_complete(application.start())
        loop.run_until_complete(gather_main_coro(side_coroutines))

        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.debug("Application received stop signal. Shutting down.")
    except Exception as exc:
        # In case the coroutine wasn't awaited, we don't need to bother the user with a warning
        updater_coroutine.close()
        raise exc
    finally:
        # We arrive here either by catching the exceptions above or if the loop gets stopped
        try:
            # Mypy doesn't know that we already check if updater is None
            if application.updater.running:  # type: ignore[union-attr]
                loop.run_until_complete(
                    application.updater.stop())  # type: ignore[union-attr]
            if application.running:
                loop.run_until_complete(application.stop())
            if application.post_stop:
                loop.run_until_complete(application.post_stop(application))
            loop.run_until_complete(application.shutdown())
            if application.post_shutdown:
                loop.run_until_complete(application.post_shutdown(application))
        finally:
            if close_loop:
                loop.close()
