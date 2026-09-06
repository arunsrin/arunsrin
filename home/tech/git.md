---
title: "Git"
tags:
  - git
  - vcs
---

# :material-database:{ .anim-fade } Git

## Separate git configurations for work and play

Put something like this in your `~/.gitconfig`:

```
[includeIf "gitdir:~/work/"]
    path = ~/.gitconfig.work

[includeIf "gitdir:~/code/"]
    path = ~/.gitconfig.personal
```
If your work repos are in `~/work`, you can have a separate user/email etc for
repos in that folder.

## Delete a tag that's already pushed

```sh
git tag -d <tag_name>
git push --delete origin <tag_name>
```

## Signing commited commits

If you want to sign the last `N` commits that you have already pushed:

```sh
git rebase --signoff -S HEAD~N
git push -f
```

## Create an empty commit

`git commit --allow-empty -m "blah blah"`

Useful if you have a gitops workflow and just want to raise a PR to trigger
something from there.

## Show parents of a merge commit

``` sh
git cat-file -p <commit>
```

or

``` sh
git show --pretty=raw <commit>
```

Both these show similar information: the committer, the parent(s),
commit text and so on.

## Show files changed between two commit IDs

Now that you have the two parents of a merged request (see above tip),
you can see all files changed between its two parents with a command
like this:

``` sh
git diff --name-only <sha1> <sha2>
```

## Color coded git output

``` sh
git config --global color.ui true
```

## Git objects

-   Tree
-   Blob
-   Commit
-   Tag

## Reverting a reverted commit in git

If you've reverted a recent commit with:

``` sh
git reset HEAD^
```

You can undo the revert with this:

``` sh
git reset HEAD@{1}
```

## Some great ones to investigate a repo

These are all from [this excellent post](https://piechowski.io/post/git-commands-before-reading-code/):

What changes the most:

```sh
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20
```

Who built this:

```sh
git shortlog -sn --no-merges
```

Where do bugs cluster:

```sh
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20
```

Is this project accelerating or dying:

```sh
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

How often is the team firefighting:

```sh
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'
```

## Using git stash to save changes temporarily

-   First do a `git add` (if its a new file to be tracked), then `git stash`
-   Check with `git stash list`
-   Reapply with `git stash apply`
-   Otherwise use `git stash pop` to recover the files and discard the stash
-   Creating a branch from a stash:

``` sh
git stash branch testchanges
```

## View commits that aren't in master

-   To see commits that have not yet merged to master:

``` sh
git log --no-merges master..
```

## Bitbucket: checkout a pull request

-   From here: <https://gist.github.com/hongymagic/6339056>

First add this to `.git/config` under the `origin` section:

``` git
    fetch = +refs/pull-requests/*:refs/remotes/origin/pull-requests/*
```

Then fetch the pull requests:

``` sh
## Modern Git: switch and restore

Instead of the overloaded `git checkout`, use:

- `git switch <branch-name>` - Switch to a branch.
- `git switch -c <new-branch>` - Create and switch to a new branch.
- `git restore <file>` - Unstage or discard changes in a file.

## View commits that aren't in main

-   To see commits that have not yet merged to main:

``` sh
git log --no-merges main..
```

...

## Git rebase vs normal pull

-   Instead of a normal pull, try this:

`git pull --rebase origin main`

-   And make it permanent with this: `git config --global pull.rebase true`
-   This removes the superfluous 'merge commit' that comes up normally.
-   Finally:

``` sh
git push origin main
```
## Git log on a file

``` sh
git log -p filename
```

actually do this:

``` sh
git log --follow filename
```

## Submodules

-   To update all submodules:

``` sh
git submodule update --init --recursive
```

-   To fetch the latest code from a submodule:

``` sh
    cd <submodule-folder>
    git pull
    cd ..
    git commit -am "bumping up submodule version"
```

Then merge the code. The next time the parent repository is pulled,
updating the submodule will get the latest commit in it.

## Working with remotes

-   Changing a remote's name

``` sh
git remote origin set-url http://some-other-url
```

-   Adding a remote

``` sh
git remote add newremote http://newremote-url
```

-   Then as usual push/pull to and from these remotes

``` sh
git pull origin master

git push newremote master
```

## Leaderboards

``` sh
git shortlog -sn
```

## Hide Whitespace Noise

Good when some one changes indentations and a whole lot of rubbish
comes).

``` sh
git diff -w
```

## Show words that have changed inline

``` sh
git diff --word-diff
```

## See what everyone is up to

``` sh
git log --all --oneline --no-merges
```

## Generate a changelog

``` sh
git log --oneline --no-merges <last tag>..HEAD
```

## View complex logs

``` sh
git log --graph --all --decorate --stat --date=iso
```

## Handy aliases

Put something like this in your *.gitconfig*

    [alias]
        st = status --branch --short
        wat = log --graph --decorate --oneline -15
        follow = log --follow -p

