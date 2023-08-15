#!/usr/bin/env python3
import glob
import os
import socket
from functools import lru_cache
from typing import Any, List

from dotbot import Plugin
from dotbot.dispatcher import Dispatcher
from dotbot.plugins import Clean, Create, Link, Shell
from dotbot.util import module


@lru_cache(1)
def get_hostname() -> str:
    """Returns the short hostname of the current system."""
    return socket.gethostname().split(".")[0]


class IfHostname(Plugin):
    _directive = "ifhostname"

    def can_handle(self, directive: str) -> bool:
        """Return true if the directive can be handled by this plugin."""
        return directive == self._directive

    def handle(self, directive: str, data: Any) -> bool:
        """Process the provided data if the directive matches
        the one handled by this plugin."""
        if not self.can_handle(directive):
            raise ValueError(f'Can not handle {directive} for "ifhostname" directive')

        return self.handle_ifplatform(data)

    def handle_ifplatform(self, data: Any) -> bool:
        """Process the provided data under the ifhostname directive."""
        expected = data.get("hostname")

        if not expected:
            raise ValueError('Missing "hostname" parameter for "ifhostname" directive')

        if not isinstance(expected, str):
            raise ValueError(
                f'Wrong type ({type(expected)}) on "hostname" parmeter '
                + 'for "ifhostname" directive'
            )

        if "met" not in data or "unmet" not in data:
            self._log.warning('ifhostname: "met" or "unmet" missing')

        if get_hostname() == expected:
            return self._run_internal(data["met"]) if "met" in data else True

        return self._run_internal(data["unmet"]) if "unmet" in data else True

    def _load_plugins(self) -> List[Plugin]:
        plugin_paths = self._context.options().plugins
        plugins = []
        for dir in self._context.options().plugin_dirs:
            for path in glob.glob(os.path.join(dir, "*.py")):
                plugin_paths.append(path)
        for path in plugin_paths:
            abspath = os.path.abspath(path)
            plugins.extend(module.load(abspath))
        if not self._context.options().disable_built_in_plugins:
            plugins.extend([Clean, Create, Link, Shell])
        return plugins

    def _run_internal(self, data: Any) -> bool:
        dispatcher = Dispatcher(
            self._context.base_directory(),
            only=self._context.options().only,
            skip=self._context.options().skip,
            options=self._context.options(),
            plugins=self._load_plugins(),
        )
        return dispatcher.dispatch(data)
