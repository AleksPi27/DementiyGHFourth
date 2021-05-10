import os
import pathlib
import typing as tp


def Test2(rootDir):
    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)
        print(path)
        if os.path.isdir(path):
            Test2(path)


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    # PUT YOUR CODE HERE
    if workdir is None and not ".git".exists():
        raise Exception("Not a git repository")
    if (workdir / ".git").exists():
        return workdir / ".git"
    if (workdir.parent).exists():
        return workdir.parent
    else:
        raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    # PUT YOUR CODE HERE
    if os.path.isfile(workdir):
        raise AssertionError(f"{workdir} is not a directory")
    if "GIT_DIR" not in os.environ:
        gitdir = workdir / pathlib.Path(".git")
    else:
        gitdir = workdir / pathlib.Path(os.environ["GIT_DIR"])
    os.mkdir(gitdir)
    os.makedirs(gitdir / "refs" / "heads")
    os.mkdir(gitdir / "refs" / "tags")
    os.mkdir(gitdir / "objects")

    f = open(pathlib.Path(gitdir / "HEAD"), "x")
    f.write("ref: refs/heads/master\n")
    f.close()

    f = open(pathlib.Path(gitdir / "config"), "x")
    f.write("[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n")
    f.close()

    f = open(pathlib.Path(gitdir / "description"), "x")
    f.write("Unnamed pyvcs repository.\n")
    f.close()

    return gitdir
