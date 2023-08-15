#!/usr/bin/env python3
from argparse import Namespace
from os.path import dirname
from unittest.mock import patch

import pytest
from dotbot.context import Context
from dotbot.plugins import Clean, Create, Link, Shell

from ifhostname import IfHostname, get_hostname


def test_get_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_hostname() should return the short DNS name string of the host."""
    hostname = "helloworld.corp.network.co.uk"
    expected = "helloworld"

    monkeypatch.setattr("socket.gethostname", lambda: hostname)

    result = get_hostname()
    assert isinstance(result, str)
    assert get_hostname() == expected


def get_fake_context(disable_builtin: bool = True) -> Context:
    return Context(
        dirname(__file__),
        Namespace(
            only=False,
            skip=False,
            plugins=[],
            plugin_dirs=[],
            disable_built_in_plugins=disable_builtin,
        ),
    )


class TestIfHostname:
    def test_directive(self) -> None:
        """IfHostname._directive must be a string containing "ifhostname"."""
        instance = IfHostname(None)

        assert isinstance(instance._directive, str)
        assert instance._directive == "ifhostname"

    def test_can_handle(self) -> None:
        """IfHostname.can_handle() should return True
        when the directive is "ifhostname"."""
        instance = IfHostname(None)

        assert instance.can_handle("somethingelse") is False
        assert instance.can_handle("ifhostname") is True

    def test_handle(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """IfHostname.handle() should return True
        when the provided directive is "ifhostname" and
        the data has an expected hostname defined."""
        instance = IfHostname(None)

        # it should raise when the directive is wrong
        with pytest.raises(ValueError) as e:
            instance.handle("somethingelse", {})
            assert e.match("Can not handle")

        # it should raise when the directive is not a str
        with pytest.raises(ValueError) as e:
            instance.handle(1234, {})  # type: ignore
            assert e.match("Can not handle")

        # it should raise when the hostname isn't provided
        with pytest.raises(ValueError) as e:
            instance.handle(instance._directive, {})
            assert e.match('Missing "hostname" parameter')

        # it should raise when the hostname is not a str
        with pytest.raises(ValueError) as e:
            for input_type in [1234, {}, 4.2, lambda x: x]:
                instance.handle(instance._directive, {"hostname": input_type})
                assert e.match("Wrong type")

        hostname = "helloworld.corp.network.co.uk"
        expected = "helloworld"

        monkeypatch.setattr("socket.gethostname", lambda: hostname)

        with patch("dotbot.dispatcher.Dispatcher.dispatch") as dispatch:
            instance = IfHostname(get_fake_context())
            dispatch.return_value = True

            # it should handle met and unmet conditions
            # even if "met" and "unmet" are not used
            instance.handle(instance._directive, {"hostname": "asdf"})
            instance.handle(instance._directive, {"hostname": expected})

            # it should call dispatch with "unmet" data
            # if the hostname doesn't match
            instance.handle(
                instance._directive,
                {"hostname": "asdf", "unmet": "unmet", "met": "met"},
            )

            dispatch.assert_called_with("unmet")

            # it should call dispatch with "met" data
            # if the hostname does match
            instance.handle(
                instance._directive,
                {"hostname": expected, "unmet": "unmet", "met": "met"},
            )

            dispatch.assert_called_with("met")

    def test_load_plugins(self) -> None:
        """IfHostname._load_plugins() should populate a list of user plugins."""
        # it should return an empty list if
        # disable_built_in_plugins is True in the context
        instance = IfHostname(get_fake_context(disable_builtin=True))
        result = instance._load_plugins()
        assert len(result) == 0

        # it should return an empty list if
        # disable_built_in_plugins is False in the context
        instance = IfHostname(get_fake_context(disable_builtin=False))
        result = instance._load_plugins()
        assert len(result) > 0
        assert Clean in result
        assert Create in result
        assert Link in result
        assert Shell in result
