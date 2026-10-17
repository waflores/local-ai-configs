"""CLI for the LLM manager's ORM-configured workflows.

Commands:
- save:        Build the current configuration and persist it to local_config.db
- list:        List the profiles stored in the database
- delete:      Remove the currently saved snapshot
- export:      Emit the saved configuration as a llama-swap config.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config_store import (
    build_and_persist,
    delete_config,
    export_llama_swap_config,
    list_profiles,
    load_config,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm_manager", description="LLM manager ORM persistence CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Build and persist the current configuration")
    p_save.set_defaults(func=_cmd_save)

    p_list = sub.add_parser("list", help="List the profiles stored in the database")
    p_list.add_argument(
        "--fields",
        nargs="*",
        default=["model_name", "model_id", "ctx_size", "fit_status"],
        help="Columns to display (default: model_name model_id ctx_size fit_status)",
    )
    p_list.set_defaults(func=_cmd_list)

    p_delete = sub.add_parser("delete", help="Remove the currently saved snapshot")
    p_delete.set_defaults(func=_cmd_delete)

    p_export = sub.add_parser(
        "export",
        help="Emit the saved configuration as a llama-swap config.yaml",
    )
    p_export.add_argument(
        "output",
        nargs="?",
        default="llama-swap/config.generated.yaml",
        help="Output YAML path (default: llama-swap/config.generated.yaml)",
    )
    p_export.set_defaults(func=_cmd_export)

    return parser


def _cmd_save(args) -> int:
    cfg = build_and_persist()
    print(
        f"Saved {len(cfg.profiles)} profiles across {len(cfg.models)} models to local_config.db"
    )
    return 0


def _cmd_list(args) -> int:
    profiles = list_profiles(fields=tuple(args.fields))
    if not profiles:
        print("No persisted profiles.")
        return 0
    for profile in profiles:
        print(profile)
    return 0


def _cmd_delete(args) -> int:
    delete_config()
    print("Deleted saved snapshot.")
    return 0


def _cmd_export(args) -> int:
    cfg = load_config()
    if cfg is None:
        print("No persisted config to export. Run 'save' first.", file=sys.stderr)
        return 1
    out = Path(args.output)
    export_llama_swap_config(cfg, out)
    print(f"Exported llama-swap config to {out}")
    return 0


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
