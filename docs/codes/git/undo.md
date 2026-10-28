---
title: Undo
---

# Undo

Almost nothing in Git is permanent. The trick is knowing which command moves
which of the three places a change lives: the working tree, the staging area
(index), and the commit history.

| Mode | Working tree | Index (staged) | Use it for |
| --- | --- | --- | --- |
| `restore` | replaced | untouched | Throw away an edit; re-read the index |
| `reset --soft` | kept | kept | Redo the last commit differently |
| `reset --mixed` | kept | reset | Unstage, then commit again |
| `reset --hard` | reset | reset | Discard commits *and* edits |
| `revert` | untouched | untouched | Undo a commit that is already public |

## Amend the last commit

```bash
git commit --amend                # reword, or fold in staged files
git commit --amend --no-edit      # keep the message while adding files
git add forgotten.py
git commit --amend --no-edit
```

Only amend a commit that has not been pushed; amending rewrites its SHA. Once
amended, `git push --force-with-lease` is needed to update the remote.

## Unstage and discard

```bash
git restore --staged app/main.py   # unstaged, keep the edit
git restore app/main.py            # discard the edit, keep the last commit
git restore .                      # discard every unstaged change

# Pre-2.23 Git used reset and checkout for these:
git reset HEAD app/main.py
git checkout -- app/main.py
```

`git restore` never deletes committed work — it only rewrites the working tree
or the index. A discarded unstaged edit is gone, so confirm with `git diff`
first.

## Reset the branch pointer

```bash
git reset --soft HEAD~1     # undo the last commit, changes stay staged
git reset HEAD~1            # undo it and unstage (default --mixed)
git reset --hard HEAD~1     # undo it and delete the changes
```

Reach for `--soft` to squash several commits into the next one, `--mixed` to
re-stage them by hand, and `--hard` only when the commits are truly disposable.

## Revert a public commit

`revert` does not rewrite history — it adds a new commit that applies the
inverse. Safe on a shared branch.

```bash
git revert <sha>            # new commit undoing <sha>
git revert --no-commit <sha> # stage the undo, edit it, then commit
git revert <older>..<newer> # undo a range
```

## Interactive rebase

Use it to tidy a branch before review: reword messages, squash noisy fixups,
reorder or drop commits. It rewrites the branch, so keep it to commits you
alone have.

```bash
git rebase -i HEAD~3        # edit the last three commits
```

The editor lists each commit with a command to change:

```text
pick   a1b2c3 Add search endpoint
squash d4e5f6 fix typo
reword 7g8h9i Tighten the docstring
drop   j0k1l2 Debugging print
```

| Command | Effect |
| --- | --- |
| `pick` | keep as-is |
| `reword` | keep the change, edit the message |
| `squash` | fold into the previous commit, combine messages |
| `fixup` | fold in but discard this message |
| `drop` | remove the commit |
| `edit` | stop so the commit can be split or amended |

## Recover with the reflog

The reflog records where the branch pointer has been, even after a `reset
--hard` or a deleted branch. It is the safety net.

```bash
git reflog                          # recent positions of HEAD
git reset --hard HEAD@{2}           # go back to an earlier position
git branch recovered HEAD@{4}       # resurrect a deleted branch
```

Reflog entries are local and expire after about 90 days, so recover promptly.

## Related

- [Basics](basics.md) — stash as a reversible way to shelve work
- [Branching](branching.md) — conflicts, and why not to rebase shared branches
- [Remotes](remote.md) — pushing after a rewrite with `--force-with-lease`
