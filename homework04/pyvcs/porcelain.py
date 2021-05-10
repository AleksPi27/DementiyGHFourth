import os
import pathlib
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    # PUT YOUR CODE HERE
    update_index(gitdir, paths)


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    # PUT YOUR CODE HERE
    commit_sha = commit_tree(gitdir, write_tree(gitdir, read_index(gitdir)), message, author)
    if is_detached(gitdir):
        ref = gitdir / "HEAD"
    else:
        ref = pathlib.Path(get_ref(gitdir))
    f = open(gitdir / ref, "w")
    f.write(commit_sha)
    f.close()
    return commit_sha


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    # PUT YOUR CODE HERE
    ref = get_ref(gitdir)
    if os.path.isfile(gitdir / ref):
        branch_head = open(gitdir / ref, "r")
        ref = branch_head.read()
        branch_head.close()
    _, old_store_bytes = read_object(ref, gitdir)
    old_store_string = old_store_bytes.decode()
    objects = find_tree_files(old_store_string[5:25], gitdir)
    project_dir = gitdir.absolute().parent
    for obj in objects:
        os.remove(project_dir / obj[0])
        par_path = pathlib.Path(obj[0]).parent
        while len(par_path.parents) > 0:
            os.rmdir(par_path)
            par_path = pathlib.Path(par_path).parent
    f_ref = open(gitdir / "HEAD", "w")
    f_ref.write(obj_name)
    f_ref.close()
    fmt, new_store_bytes = read_object(obj_name, gitdir)
    new_store_string = new_store_bytes.decode()
    objects = find_tree_files(new_store_string[5:25], gitdir)
    for obj in objects:
        parents_number = len(pathlib.Path(obj[0]).parents)
        par_path = project_dir
        for par in range(parents_number - 2, -1, -1):
            par_path /= pathlib.Path(obj[0]).parents[par]
            if not os.path.isdir(par_path):
                os.mkdir(par_path)
        fmt, obj_store = read_object(obj[1], gitdir)
        if fmt.__eq__("blob"):
            f = open(pathlib.Path(project_dir / obj[0]), "x")
            f.write(obj_store.decode())
            f.close()
        else:
            os.mkdir(project_dir / obj[0])
