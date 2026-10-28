---
title: Remotes
---

# Remotes

A remote is a named URL — usually `origin` — that the local repository fetches
from and pushes to. This covers keeping the two in sync and contributing back.

## When to use what

| Situation | Reach for |
| --- | --- |
| Seeing or changing a remote URL | [`git remote`](#remotes) |
| Checking for upstream changes without changing files | [`git fetch`](#fetch-vs-pull) |
| Updating the current branch | [Pull](#fetch-vs-pull) |
| Publishing a branch for the first time | [Push and set upstream](#push-and-set-upstream) |
| Contributing to someone else's repo | [Forks and upstream](#forks-and-upstream) |
| Marking a release | [Tags](#tags) |

## Remotes

```bash
git remote -v                                  # list with fetch/push URLs
git remote add origin git@github.com:user/repo.git
git remote set-url origin git@github.com:user/other.git
git remote remove origin
```

Use SSH URLs (`git@github.com:…`) so pushes authenticate with a key rather than
a password; see [Config](config.md).

## Fetch vs pull

`fetch` downloads new commits and updates the remote-tracking branches
(`origin/main`) without touching your working tree. `pull` is `fetch` followed
by a merge or rebase into the current branch.

```bash
git fetch origin
git fetch --prune              # also delete remote-tracking branches that are gone
git pull                       # fetch + merge
git pull --ff-only             # refuse unless it can fast-forward
git pull --rebase              # replay your commits on top
```

Make the safe default explicit once:

```bash
git config --global pull.rebase true
git config --global fetch.prune true
```

## Push and set upstream

```bash
git push -u origin feature/search   # first push of a new branch
git push                            # later pushes of a tracked branch
git push origin HEAD                # push current branch under its own name
git push origin --delete feature/search
```

`-u` (short for `--set-upstream`) records the link, so `git status` can report
how far ahead or behind you are and later pushes need no arguments.

After amending or rebasing a branch you already pushed, the remote rejects the
diverged history. Replace it safely — `--force-with-lease` refuses if someone
else pushed in the meantime, unlike a bare `--force`:

```bash
git push --force-with-lease
```

## Forks and upstream

On a fork, `origin` points at your copy and `upstream` at the original. Pull the
original in, then push to your fork.

```bash
git remote add upstream git@github.com:owner/repo.git
git fetch upstream
git switch main
git rebase upstream/main       # or: git merge upstream/main
git push origin main
```

A pull request is then just a branch on the fork with an upstream set:
`git push -u origin feature/search`.

## Tags

Tags name a specific commit, typically a release. Push them separately — `git
push` does not send tags.

```bash
git tag                        # list
git tag -a v1.0.0 -m "First release"
git push origin v1.0.0         # one tag
git push --tags               # every tag
```

## Related

- [Basics](basics.md) — the commits a push carries
- [Branching](branching.md) — the branch behind a pull request
- [Config](config.md) — SSH keys and credential helpers
