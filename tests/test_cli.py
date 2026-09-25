"""Tests for the CLI argument parser and helpers"""

from pathlib import Path

import pytest

from password_manager.cli import (
    DEFAULT_VAULT_PATH,
    build_parser,
    resolve_vault_path,
)


def test_build_parser_recognizes_all_commands():
    """Every subcommand should be registered in the parser"""
    parser = build_parser()
    simple = ["init", "list", "generate"]
    with_site = ["add", "get", "update", "delete"]

    for command in simple:
        args = parser.parse_args([command])
        assert args.command == command

    for command in with_site:
        args = parser.parse_args([command, "example"])
        assert args.command == command


def test_default_vault_path_is_in_home():
    """The default vault path should live under the user's home directory"""
    assert DEFAULT_VAULT_PATH.parent.parent == Path.home()


def test_resolve_vault_path_uses_argument():
    """When --vault-path is given, resolve_vault_path should return it"""
    parser = build_parser()
    custom = Path("custom/location/vault.json")
    args = parser.parse_args(["--vault-path", str(custom), "list"])
    assert resolve_vault_path(args) == custom


def test_resolve_vault_path_falls_back_to_default():
    """Without --vault-path, resolve_vault_path should return the default"""
    parser = build_parser()
    args = parser.parse_args(["list"])
    assert resolve_vault_path(args) == DEFAULT_VAULT_PATH


def test_add_parses_site_argument():
    """`add` should accept a positional site argument"""
    parser = build_parser()
    args = parser.parse_args(["add", "github"])
    assert args.site == "github"
    assert args.generate is False
    assert args.length == 16


def test_add_generate_flag():
    """`add --generate --length 32` should set both options"""
    parser = build_parser()
    args = parser.parse_args(["add", "github", "--generate", "--length", "32"])
    assert args.generate is True
    assert args.length == 32


def test_get_show_flag():
    """`get github --show` should set show to True"""
    parser = build_parser()
    args = parser.parse_args(["get", "github", "--show"])
    assert args.show is True

def test_get_copy_flag():
    """`get github --copy` should set copy to True"""
    parser = build_parser()
    args = parser.parse_args(["get", "github", "--copy"])
    assert args.copy is True

def test_generate_length_option():
    """`generate --length 24` should set length to 24"""
    parser = build_parser()
    args = parser.parse_args(["generate", "--length", "24"])
    assert args.length == 24


def test_missing_command_raises():
    """Calling the parser with no command should exit with an error"""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
