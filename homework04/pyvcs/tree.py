import os
import pathlib
import time
import typing as tp

from pyvcs.index import GitIndexEntry
from pyvcs.objects import hash_object


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    # PUT YOUR CODE HERE
    content = b""
    for entry in index:
        if "/" in entry.name:
            content += b"40000 "
            ford = entry.name[:entry.name.find("/")]
            content += ford.encode() + b"\0"
            sha_of = b""
            sha_of += oct(entry.mode)[2:].encode() + b" "
            ford1 = entry.name[entry.name.find("/") + 1:]
            sha_of += ford1.encode() + b"\0"
            sha_of += entry.sha1
            sha_of_end = hash_object(sha_of, "tree", True)
            content += bytes.fromhex(sha_of_end)
        else:
            content += oct(entry.mode)[2:].encode() + b" "
            content += entry.name.encode() + b"\0"
            content += entry.sha1
    tree = hash_object(content, "tree", True)
    return tree


# print("index is " + str(data))

# pathToFile = pathlib.Path(".git/objects/" + str(hashlib.sha1(store.encode()).hexdigest()[:2]))
# os.makedirs(pathToFile, exist_ok=True)
# pathToFile = ".git/objects/" + str(hashlib.sha1(store.encode()).hexdigest()[:2]) + "/" + str(hashlib.sha1(
#         store.encode()).hexdigest()[2:])
# hash_file = open(pathToFile, "wb")
# str_compressed = zlib.compress(store.encode())
# hash_file.write(str_compressed)
# print("index is " + str(str_compressed.hex()))
# hash_file.close()
# return hashlib.sha1(store.encode()).hexdigest()


def commit_tree(
        gitdir: pathlib.Path,
        tree: str,
        message: str,
        parent: tp.Optional[str] = None,
        author: tp.Optional[str] = None,
) -> str:
    if author is None and "GIT_AUTHOR_NAME" in os.environ and "GIT_AUTHOR_EMAIL" in os.environ:
        author = os.environ["GIT_AUTHOR_NAME"] + " " + os.environ["GIT_AUTHOR_EMAIL"]
    if author is None:
        author = "Aleksandr Piliakin aleksandrpiliakin@gmail.com"
    time_of_commit = (
            str(int(time.mktime(time.localtime()))) + " " + str(time.strftime("%z", time.gmtime()))
    )
    store = (
            "tree "
            + tree
            + "\nauthor "
            + author
            + " "
            + time_of_commit
            + "\ncommitter "
            + author
            + " "
            + time_of_commit
            + "\n\n"
            + message
            + "\n"
    )
    return hash_object(store.encode(), "commit", True)
