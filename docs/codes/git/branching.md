---
title: Branching
---

# Branching

Branches are cheap pointers, so make one for every change. This covers moving
between them, landing them, and getting unstuck when a merge conflicts.

## When to use what

| Situation | Reach for |
| --- | --- |
| Starting a change in isolation | [`git switch -c`](#creating-and-switching) |
| Bringing a finished branch in | [Merge](#merging) |
| Replaying work on top of a moved base | [Rebase](#rebasing) |
| Copying one specific commit onto the current branch | [Cherry-picking](#cherry-picking) |
| A merge stopped with conflicts | [Resolving conflicts](#resolving-conflicts) |
| Ticking off a merged branch | [Delete a branch](#deleting-branches) |

## Creating and switching

```bash
git switch -c feature/search     # create and switch (modern)
git switch main                  # switch to an existing branch
git branch feature/search        # create without switching

# Pre-2.23 Git used checkout for both jobs:
git checkout -b feature/search
git checkout main
```

Keeping the branch name and the work tied together makes the history readable.
`switch` cannot lose uncommitted changes silently, which is why it replaced
`checkout` for this job.

## Listing branches

```bash
git branch            # local
git branch -a         # include remote-tracking branches
git branch -vv        # upstream and last commit per branch
```

`-vv` is the quickest way to spot a branch that is ahead of or behind its
upstream.

## Merging

Merge keeps both histories and adds a merge commit. Fast-forward (the default)
just slides the pointer when the target has not moved.

```bash
git switch main
git merge feature/search        # fast-forward when possible
git merge --no-ff feature/search  # force a merge commit
git merge --squash feature/search # stage the changes, commit once yourself
```

`--no-ff` keeps the fact that a group of commits came from one branch; `--squash`
collapses them into a single commit on the target.

## Rebasing

Rebase replays your commits on top of another branch, producing a straight line
instead of a merge commit. Use it on branches that only you have pushed.

```bash
git switch feature/search
git rebase main                 # replay this branch on top of main
git rebase main feature/search  # same, without switching first
```

Never rebase a branch others have pulled — the rewritten commits leave their
copies behind and the next pull fights over them.

## Cherry-picking

Reach for this when one commit from another branch is wanted here, but the rest
of that branch is not — pulling a single bugfix out of an unfinished feature, or
copying a hotfix back to a release branch.

```bash
git switch release
git cherry-pick <sha>            # copy that commit onto the current branch

git cherry-pick <older>^..<newer>  # a range of commits
git cherry-pick -n <sha>         # apply the changes without committing yet
```

Like rebase, cherry-pick writes a *new* commit with a new SHA — the original
stays where it was, so the same change ends up in two places. Do not use it to
move a whole branch; that is what merge and rebase are for. Finding the SHA is
usually `git log --oneline <branch>` first.

A cherry-pick that overlaps the current code pauses with the same conflict
markers as a merge, and continues the same way:

```bash
git cherry-pick --continue
git cherry-pick --abort
git cherry-pick --skip
```

## Resolving conflicts

Merge, rebase and cherry-pick all pause and mark the overlapping files with
`<<<<<<<` markers. Edit each file to the final content, then tell Git to
continue.

```bash
git status                 # lists the conflicted files
# edit the files, keep the code you want, delete the markers
git add <file>
git merge --continue       # or: git rebase --continue / git cherry-pick --continue
```

A conflict is not a corruption — the markers are plain text:

```text
<<<<<<< HEAD
value = compute_fast()
=======
value = compute_correct()
>>>>>>> feature/search
```

Resolve by picking a side or combining both, then `git add`. To back out of the
operation entirely and return to the state before it started:

```bash
git merge --abort
git rebase --abort
git rebase --skip          # drop the commit being replayed and move on
```

When `rebase --continue` reports no changes, it means the commit is already
present upstream; `--skip` is the answer.

## Deleting branches

```bash
git branch -d feature/search          # only if fully merged
git branch -D feature/search          # force, discarding unmerged commits
git push origin --delete feature/search   # remove the remote one too
```

`-D` throws away commits that exist nowhere else — check `git branch --merged`
or the reflog first. See [Undo](undo.md) for recovering a branch that was
deleted by mistake.

## Related

- [Basics](basics.md) — the commit loop that fills a branch
- [Undo](undo.md) — amending and squashing what a branch contains
- [Remotes](remote.md) — pushing a branch and opening a pull request
