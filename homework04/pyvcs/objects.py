import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    # PUT YOUR CODE HERE
    header = f"{fmt} {len(data)}\0"
    store = header.encode() + data
    if write:
        pathToFile = pathlib.Path(".git/objects/" + str(hashlib.sha1(store).hexdigest()[:2]))
        os.makedirs(pathToFile, exist_ok=True)

        # print("File exists?: "+pathToFile.exists())
        # print(pathlib.Path((".git/objects" / hashlib.sha1(store.encode()).hexdigest()[:2]).exists()))

        pathToFile = ".git/objects/" + str(hashlib.sha1(store).hexdigest()[:2]) + "/" + str(hashlib.sha1(
            store).hexdigest()[2:])
        hash_file = open(pathToFile, "wb")
        str_compressed = zlib.compress(store)
        hash_file.write(str_compressed)
        hash_file.close()

    return hashlib.sha1(store).hexdigest()


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    # PUT YOUR CODE HERE
    if len(obj_name) < 4 or len(obj_name) > 40:
        raise Exception(f"Not a valid object name {obj_name}")
    else:
        objs = []
        if (pathlib.Path(".git/objects/" + obj_name[:2])).exists():
            for root, dirs, files in os.walk(pathlib.Path(".git/objects/" + obj_name[:2])):
                for file in files:
                    if str(file).__contains__(obj_name[2:]):
                        objs.append(obj_name[:2] + file)
        if len(objs) == 0:
            raise AssertionError(f"Not a valid object name {obj_name}")
        return objs


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    return resolve_object(obj_name,gitdir)[0]


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    # PUT YOUR CODE HERE
    obj_path = find_object(sha, gitdir)
    cur_file = open(pathlib.Path(gitdir / "objects" / obj_path[0:2] / obj_path[2:]), "rb")
    obj_data = zlib.decompress(cur_file.read())
    right, left = obj_data.find(b" "), obj_data.find(b"\x00")
    length = int(obj_data[right:left].decode("ascii"))
    content = obj_data[left + 1:]
    fmt = obj_data[:right].decode()
    cur_file.close()
    return fmt, content


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    # PUT YOUR CODE HERE
    result = []
    while len(data) > 0:
        fmt = data[:6].decode()
        data = data[6:]
        if fmt == "100644":
            data = data[1:]
            sep_ind = data.find(b"\x00")
            # print("Name ---", data[:sep_ind].decode())
            # print("Hash ---", data[sep_ind + 1 : sep_ind + 21].hex())
            result.append((100644, data[:sep_ind].decode(), data[sep_ind + 1: sep_ind + 21].hex()))
            data = data[sep_ind + 21:]
        else:
            sep_ind = data.find(b"\x00")
            # print("Name ---", data[:sep_ind].decode())
            # print("Hash ---", data[sep_ind + 1 : sep_ind + 21].hex())
            result.append((40000, data[:sep_ind].decode(), data[sep_ind + 1: sep_ind + 21].hex()))
            data = data[sep_ind + 21:]
    return result


def cat_file(obj_name: str, pretty: bool = True) -> None:
    # PUT YOUR CODE HERE
    if "GIT_DIR" not in os.environ:
        gitname = pathlib.Path(".git")
    else:
        gitname = pathlib.Path(os.environ["GIT_DIR"])
    fmt, data = read_object(obj_name, gitname)
    if fmt == "blob":
        if pretty:
            print(data.decode())
        else:
            print(data)
        return
    elif fmt == "tree":
        content = read_tree(data)
        if pretty:
            for entry in content:
                if entry[0] == 40000:
                    print("040000", "tree", entry[2] + "\t" + entry[1])
                else:
                    print("100644", "blob", entry[2] + "\t" + entry[1])
        else:
            for entry in content:
                print(entry[2])
    else:
        print(data.decode())


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    # PUT YOUR CODE HERE
    fmt, store=read_object(tree_sha, gitdir)
    objects=read_tree(store)
    files=[]
    for obj in objects:
        if obj[0]==100644 or obj[0]==100755:
            files.append((obj[1], obj[2]))
        else:
            sub_objects=find_tree_files(obj[2],gitdir)
            for sub_obj in sub_objects:
                files.append((obj[1]+"/"+sub_obj[0],sub_obj[1]))
    return files


def commit_parse(raw: bytes, start: int = 0, dct=None):
    # PUT YOUR CODE HERE
    ...
