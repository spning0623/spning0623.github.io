"""Build, commit, and push the academic homepage to GitHub Pages."""

from pathlib import Path
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", nargs="?", default="Update academic homepage")
    args = parser.parse_args()

    repository = run("git", "rev-parse", "--show-toplevel", capture_output=True, text=True)
    if Path(repository.stdout.strip()).resolve() != ROOT:
        raise RuntimeError("Run this script from the configured homepage repository.")
    branch = run("git", "branch", "--show-current", capture_output=True, text=True)
    if branch.stdout.strip() != "main":
        raise RuntimeError("Switch to the main branch before publishing.")

    run(sys.executable, "scripts/build.py")
    run("git", "add", "--all")
    changes = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if changes.returncode == 1:
        run("git", "commit", "-m", args.message)
    elif changes.returncode != 0:
        raise RuntimeError("Could not inspect staged changes.")
    else:
        print("No new changes to commit.", flush=True)
    run("git", "push", "origin", "main")
    print("Pushed successfully. Follow deployment progress at:")
    print("https://github.com/spning0623/spning0623.github.io/actions")
    print("Website: https://spning0623.github.io/")


if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Publishing stopped: {error}", file=sys.stderr)
        sys.exit(1)
