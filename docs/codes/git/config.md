---
title: Config
---

# Git config

One-time setup per machine: who you are, shortcuts for the long commands, and
what should never be committed. Everything here is written to `~/.gitconfig`
with `--global`; drop the flag for a single repository.

## Identity

Set this before the first commit; the author is baked into every one.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Check what is in effect, and where each value came from:

```bash
git config --list --show-origin
```

## Aliases

Short names for the commands typed most. The pattern is `git config --global
alias.<name> "<command>"`, then use it as `git <name>`.

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.unstage "restore --staged"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
```

A shell alias is the other option, but a Git alias travels with `~/.gitconfig`
to every terminal:

```bash
git lg
```

## Ignoring files

`.gitignore` in the repository root lists patterns Git should leave untracked.
Commit it so the team shares the rules.

```gitignore
# .gitignore
__pycache__/
.venv/
.env
*.log
node_modules/
```

Patterns starting with `/` are anchored to the repo root; a trailing `/` matches
only directories. Keep machine-specific paths out of the shared file and in a
global one instead:

```bash
git config --global core.excludesfile ~/.gitignore_global
```

Two things `.gitignore` cannot do, because it only affects untracked files:

```bash
git rm --cached secret.env      # a file that is already tracked
git update-index --skip-worktree config/local.py  # keep local edits out of a commit
```

## Line endings

Mixed Windows and Unix contributors otherwise produce whole-file diffs. Pick one
strategy — the `.gitattributes` file is the portable one.

=== "`.gitattributes` (recommended)"

    ```gitattributes
    * text=auto
    *.sh text eol=lf
    *.bat text eol=crlf
    *.png binary
    ```

=== "Per-machine"

    ```bash
    # Windows: convert to CRLF on checkout, LF in the repo
    git config --global core.autocrlf true

    # macOS / Linux: store LF, leave the working tree alone
    git config --global core.autocrlf input
    ```

## SSH keys

```bash
ssh-keygen -t ed25519 -C "you@example.com"
ssh-add ~/.ssh/id_ed25519
ssh -T git@github.com          # verify the key is accepted
```

Add the public key (`~/.ssh/id_ed25519.pub`) to the host once. With HTTPS remotes
instead, a credential helper caches the token:

```bash
git config --global credential.helper osxkeychain   # macOS
git config --global credential.helper store         # Linux, plaintext
```

## Related

- [Basics](basics.md) — the commands those aliases shorten
- [Remotes](remote.md) — SSH remotes the keys authenticate
