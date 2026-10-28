---
title: Basics
---

# Git basics

The everyday loop: look at what changed, stage the part you want, commit it,
and read the history back.

## When to use what

| Situation | Reach for |
| --- | --- |
| Starting from an existing project | [`git clone`](#start-a-repository) |
| Turning a folder into a repository | [`git init`](#start-a-repository) |
| Seeing what changed but is not staged | [`git status` / `git diff`](#the-daily-loop) |
| Committing only part of a file | [`git add -p`](#staging-part-of-a-change) |
| Removing a file that is already tracked | [`git rm`](#removing-and-moving-files) |
| Shelving work to switch tasks | [Stash](#stash) |

## Start a repository

```bash
# Existing project from a remote
git clone git@github.com:user/repo.git

# Clone into a named folder, or shallow for a one-off build
git clone git@github.com:user/repo.git myfolder
git clone --depth 1 git@github.com:user/repo.git

# Fresh repository, with `main` as the first branch
git init
git init -b main
```

`git init` is safe to run in a folder that already has files — it only creates
the `.git/` directory and leaves the working tree alone.

## The daily loop

The four commands used most often, in order. `status` is cheap; run it often.

```bash
git status                 # what is staged, modified and untracked
git add app/               # stage a path (repeatable)
git commit -m "Add search endpoint"
git log --oneline --graph --decorate --all
```

`git diff` shows unstaged changes; `--staged` (or `--cached`) shows what a
commit would capture:

```bash
git diff                   # working tree vs index
git diff --staged          # index vs last commit
git diff main..feature     # two branches
git diff -- path/to/file   # limit to one path
```

Read a single commit or file history with:

```bash
git show <sha>             # message + diff
git log -p -- app/main.py  # every change to one file
git blame app/main.py      # who last touched each line
```

## Staging part of a change

Reach for this when a single file holds two unrelated edits and they belong in
separate commits. `-p` walks each hunk and asks whether to stage it.

```bash
git add -p                 # stage hunk by hunk
git add -u                 # stage modifications to tracked files only
git add -A                 # stage everything, including deletions
```

## Removing and moving files

Track renames and deletions through Git so history keeps the file's identity.

```bash
git rm old.py              # delete and stage the deletion
git rm --cached secret.env # stop tracking, keep the file on disk
git mv old.py new.py       # rename and stage it
```

## Stash

Reach for this when you need a clean working tree right now — a hotfix on
another branch, a pull that refuses to merge — but the current work is not ready
to commit.

```bash
git stash push -m "wip: search flags"   # shelve tracked changes
git stash -u                            # include untracked files
git stash list
git stash pop                           # apply the top entry and drop it
git stash apply stash@{1}               # apply without dropping
git stash drop stash@{0}
```

Stashes are local and not pushed, so they are a scratchpad rather than a
backup. Commit to a throwaway branch when the work must survive.

## Related

- [Branching](branching.md) — moving the work onto its own branch
- [Config](config.md) — ignoring files that should never be committed
