#! /usr/bin/env python3
#
# (c) Copyright 2016 - 2024 HP Development Company L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from typing import List
from pathlib import Path

assert sys.version_info >= (3, 8)


def is_modified(file_path: Path) -> bool:
    """Return True if the given file has local modifications, False otherwise"""
    proc = subprocess.run(
        ["git", "status", "--short", file_path.name],
        cwd=file_path.parent,
        encoding="utf-8",
        capture_output=True,
    )

    proc.check_returncode()

    is_modified = False
    if proc.stdout:
        status, _ = proc.stdout.strip().split()
        is_modified = status == "M"

    return is_modified


def get_files(dir: Path) -> List[Path]:
    """Return all the files in the given dir and sub dirs."""
    files = []
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            files.append(Path(dirpath) / filename)

    return files


def apply_fixups(workspace: Path, fixups_root: Path) -> None:
    workspace = workspace.resolve()
    fixups_root = fixups_root.resolve()

    override_files = get_files(fixups_root)
    overrides_and_targets = [
        (override, workspace / override.relative_to(fixups_root))
        for override in override_files
    ]

    # Protect from overwriting local modifications
    targets_with_local_modifications = [
        target
        for (override, target) in overrides_and_targets
        if target.is_file()
        and not filecmp.cmp(target, override, shallow=False)
        and is_modified(target)
    ]

    if targets_with_local_modifications:
        print("Stashing modified files before applying fixups")
        print("(Use `git stash pop` to restore the modified files)")
        repos = set(get_repo_root(file) for file in targets_with_local_modifications)
        for repo in repos:
            subprocess.run(
                ["git", "stash", "push", "-m", "Auto stash by fixup.py"],
                cwd=repo,
                check=True,
            )

    # Check for "dead" fixups (fixups that are the same as the target file)
    dead_fixups = [
        override
        for (override, target) in overrides_and_targets
        if target.is_file()
        and filecmp.cmp(target, override, shallow=False)
        and not is_modified(target)
    ]

    if dead_fixups:
        print("WARNING: Possible dead fixups")
        for override in dead_fixups:
            print(f"   {override}")

    # If we made it this far, copy all overrides
    for override, target in overrides_and_targets:
        try:
            shutil.copy(override, target)
            print(f"Copied fixup to {target}")
        except FileNotFoundError:
            print(f"Copying Failed. File {target} does not exist")


def get_repo_root(path: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path.parent,
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    return proc.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Copies fixups from FIXUPS_ROOT to WORKSPACE. Auto stashes any files with local modifications that would be overwritten by fixups."
    )
    parser.add_argument(
        "-w",
        "--workspace",
        help="The root of the project working copy, ex: C:/FW/Travolta",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--fixups-root",
        help="The location of the actual fixup files, ex: C:/FW/Travolta/HpPlatformPkg/Fixup/Override",
        required=True,
    )
    args = parser.parse_args()

    workspace = Path(args.workspace)
    fixups_root = Path(args.fixups_root)

    apply_fixups(workspace, fixups_root)


if __name__ == "__main__":
    main()
