"""Command-line interface for the password manager"""

import argparse
import pyperclip
import getpass
import sys
from pathlib import Path

from .exceptions import VaultError
from .generator import generate_password
from .models import Entry
from .vault import Vault

DEFAULT_VAULT_PATH = Path.home() / ".password_manager" / "vault.json"


#  helpers


def ask_master_password(prompt: str = "Master password: ") -> str:
    """Read a password from the terminal without echoing it"""
    return getpass.getpass(prompt)


def resolve_vault_path(args: argparse.Namespace) -> Path:
    """Return the vault path from --vault-path, or the default"""
    if args.vault_path is not None:
        return args.vault_path
    return DEFAULT_VAULT_PATH


def ask_optional(prompt: str, current: str | None = None) -> str | None:
    """Ask the user for a value; empty input keeps the current value"""
    if current is not None:
        raw = input(f"{prompt} [{current}]: ").strip()
        return raw if raw else current
    raw = input(f"{prompt}: ").strip()
    return raw if raw else None


#  commands


def cmd_init(args: argparse.Namespace) -> int:
    """Create a new vault"""
    path = resolve_vault_path(args)
    password = ask_master_password("New master password: ")
    confirm = ask_master_password("Confirm master password: ")

    if password != confirm:
        print("Error: passwords do not match", file=sys.stderr)
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    Vault.init(path, password)
    print(f"Vault created at {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add a new entry to the vault"""
    path = resolve_vault_path(args)
    password = ask_master_password()

    with Vault.open(path, password) as vault:
        if args.generate:
            entry_password = generate_password(length=args.length)
            print(f"Generated password: {entry_password}")
        else:
            entry_password = getpass.getpass("Entry password: ")

        username = input("Username: ").strip()
        notes = input("Notes (optional): ").strip() or None

        vault.add(
            Entry(
                site=args.site, username=username, password=entry_password, notes=notes
            )
        )

    print(f"Added entry for '{args.site}'")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    """Show one entry."""
    path = resolve_vault_path(args)
    password = ask_master_password()

    with Vault.open(path, password) as vault:
        entry = vault.get(args.site)
        if args.copy:
            pyperclip.copy(entry.password)
        if args.show:
            shown = entry.password
        elif args.copy:
            shown = "**** (copied to clipboard)"
        else:
            shown = "****"
            
        print(f"Site:     {entry.site}")
        print(f"Username: {entry.username}")
        print(f"Password: {shown}")
        if entry.notes:
            print(f"Notes:    {entry.notes}")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List every site in the vault"""
    path = resolve_vault_path(args)
    password = ask_master_password()

    with Vault.open(path, password) as vault:
        sites = vault.list_sites()
        if not sites:
            print("Vault is empty")
        else:
            for site in sorted(sites):
                print(site)

    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Update an existing entry."""
    path = resolve_vault_path(args)
    password = ask_master_password()

    with Vault.open(path, password) as vault:
        old = vault.get(args.site)

        username = ask_optional("Username", old.username) or old.username
        new_password = getpass.getpass("New password (empty to keep): ")
        if not new_password:
            new_password = old.password
        notes = ask_optional("Notes", old.notes)

        updated = Entry(
            site=args.site,
            username=username,
            password=new_password,
            notes=notes,
            created_at=old.created_at,
        )
        vault.update(updated)

    print(f"Updated entry for '{args.site}'")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """Delete an entry"""
    path = resolve_vault_path(args)
    password = ask_master_password()

    with Vault.open(path, password) as vault:
        vault.delete(args.site)

    print(f"Deleted entry for '{args.site}'")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate a random password and print it"""
    pw = generate_password(length=args.length)
    print(pw)
    return 0


#  argument parsing

def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser for every subcommand"""
    parser = argparse.ArgumentParser(
        prog="pwm",
        description="A simple encrypted password manager",
    )
    parser.add_argument(
        "--vault-path",
        type=Path,
        default=None,
        help="Path to the vault file (default: ~/.password_manager/vault.json)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new vault")
    p_init.set_defaults(func=cmd_init)

    p_add = sub.add_parser("add", help="Add a new entry")
    p_add.add_argument("site", help="Site name (e.g. github)")
    p_add.add_argument(
        "--generate", action="store_true", help="Generate a random password"
    )
    p_add.add_argument(
        "--length", type=int, default=16, help="Generated password length"
    )
    p_add.set_defaults(func=cmd_add)

    p_get = sub.add_parser("get", help="Show one entry")
    p_get.add_argument("site")
    p_get.add_argument("--show", action="store_true", help="Show the real password")
    p_get.add_argument("--copy",action="store_true",help="Copy the password to the clipboard instead of printing it")
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list", help="List every site")
    p_list.set_defaults(func=cmd_list)

    p_update = sub.add_parser("update", help="Update an entry")
    p_update.add_argument("site")
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="Delete an entry")
    p_delete.add_argument("site")
    p_delete.set_defaults(func=cmd_delete)

    p_generate = sub.add_parser("generate", help="Generate a random password")
    p_generate.add_argument("--length", type=int, default=16)
    p_generate.set_defaults(func=cmd_generate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except VaultError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())