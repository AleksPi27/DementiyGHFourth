import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    # PUT YOUR CODE HERE
    path_to_ref = gitdir / ref
    f = open(path_to_ref, "x")
    f.write(new_value)
    f.close()


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    # PUT YOUR CODE HERE
    f = open(gitdir / name, "w")
    f.write()
    f.close()


def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:
    # PUT YOUR CODE HERE
    if refname.__eq__("HEAD"):
        f = open(gitdir / "HEAD", "r")
        refname = f.read()
        refname = refname[5:-1]
        f.close()
    f = open(gitdir / refname, "r")
    data = f.read()
    f.close()
    return data


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    # PUT YOUR CODE HERE
    if pathlib.Path.exists(gitdir / get_ref(gitdir)):
        return ref_resolve(gitdir, "HEAD")
    return None


def is_detached(gitdir: pathlib.Path) -> bool:
    # PUT YOUR CODE HERE
    if not pathlib.Path.exists(gitdir / "HEAD"):
        return False
    f = open(gitdir / "HEAD", "r")

    data = f.read()
    f.close()
    if type(data) == str and len(data) == 40 and not data[:5].__eq__("ref: "):
        return True
    return False


def get_ref(gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    f = open(gitdir / "HEAD", "r")
    ref = f.read()
    f.close()
    if ref[:5].__eq__("ref: "):
        ref = ref[5:-1]
    return ref
