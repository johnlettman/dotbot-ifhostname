import glob
import os
import socket
from collections.abc import Mapping
from typing import Any

from dotbot import Plugin
from dotbot.dispatcher import Dispatcher
from dotbot.plugins import Clean, Create, Link, Shell
from dotbot.util import module


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

        return self.handle_ifhostname(data)

    def handle_ifhostname(self, data: Any) -> bool:
        """Process the provided data under the ifhostname directive."""
        if not isinstance(data, Mapping):
            raise TypeError(
                'Wrong type for "ifhostname" directive (expected a mapping)'
            )

        expected = data.get("hostname")

        if not expected:
            raise ValueError('Missing "hostname" parameter for "ifhostname" directive')

        if not isinstance(expected, (str, list)):
            raise TypeError(
                f'Wrong type ({type(expected)}) on "hostname" parameter '
                + 'for "ifhostname" directive (expected type str or list of str)'
            )

        # Normalize to a list
        expected = [expected] if isinstance(expected, str) else expected

        if not all(isinstance(host, str) for host in expected):
            raise ValueError(
                'All items in the "hostname" parameter must be str '
                'for "ifhostname" directive'
            )

        if "met" not in data or "unmet" not in data:
            self._log.warning('ifhostname: "met" or "unmet" missing')

        if get_hostname() in expected:
            return self._run_internal(data["met"]) if "met" in data else True

        return self._run_internal(data["unmet"]) if "unmet" in data else True

    def _load_plugins(self) -> list[Plugin]:
        options = self._context.options()
        plugin_paths = list(options.plugins or [])
        plugins = []
        for plugin_dir in options.plugin_dirs or []:
            plugin_paths.extend(glob.glob(os.path.join(plugin_dir, "*.py")))
        for path in dict.fromkeys(plugin_paths):
            abspath = os.path.abspath(path)
            plugins.extend(module.load(abspath))
        if not options.disable_built_in_plugins:
            plugins.extend([Clean, Create, Link, Shell])
        return plugins

    def _run_internal(self, data: Any) -> bool:
        # Dispatcher.dispatch() consumes a sequence of task mappings. Accept a
        # single task mapping too, which is easy to produce when writing a
        # conditional block by hand.
        tasks = [data] if isinstance(data, Mapping) else data
        dispatcher = Dispatcher(
            self._context.base_directory(),
            only=self._context.options().only,
            skip=self._context.options().skip,
            options=self._context.options(),
            plugins=self._load_plugins(),
        )
        return dispatcher.dispatch(tasks)
