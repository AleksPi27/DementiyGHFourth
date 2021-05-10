import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        # PUT YOUR CODE HERE
        values = (self.ctime_s, self.ctime_n, self.mtime_s, self.mtime_n,
                  self.dev, self.ino, self.mode, self.uid,
                  self.gid, self.size, self.sha1, self.flags, self.name.encode())
        packed = struct.pack("!10i20sh" + str(len(self.name)) + "s" + str(8 - (62 + len(self.name)) % 8) + "x", *values)
        return packed

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        # PUT YOUR CODE HERE
        first_part = struct.unpack("!10i20sh", data[:62])
        # print("first part is " + str(first_part))
        second_part = struct.unpack(str(len(data) - 62) + "s", data[62:])
        # print("second part is " + str(second_part))

        name = second_part[0]
        name = str(name)
        # print(type(name))
        # name=name.replace('\x00','')
        first_slash_index = 0
        for i in range(len(name)):
            if name[i].__eq__('\\'):
                first_slash_index = i
                break
        if first_slash_index > 0:
            name = name[:first_slash_index]
        name = name[2:]
        # print("second part after seecond cleaning is " + name)
        ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1, flags = first_part

        return GitIndexEntry(ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1, flags, name)
        # return GitIndexEntry(struct.unpack("!10i20sh"+str(len(data.name))+"s"+str(8-(62+len(data.name))%8)+"x", data))


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    # PUT YOUR CODE HERE
    entries = []
    if not (gitdir / "index").exists():
        return entries
    with open(gitdir / "index", mode="rb") as f:
        header = f.read(12)
        main_part = f.read()
    unpacked_header = struct.unpack("!L", header[8:])
    for i in range(unpacked_header[0]):
        end = len(main_part) - 1
        for j in range(63, len(main_part), 8):
            if main_part[j] == 0:
                end = j
                break
        entries.append(GitIndexEntry.unpack(main_part[:end + 1]))
        if len(main_part) != end - 1:
            main_part = main_part[end + 1:]
    return entries


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    # PUT YOUR CODE HERE
    # strdd=b"DIRC"+" "+str(2)+" "+str(len(entries))
    header = struct.pack("!4sLL", b"DIRC", 2, len(entries))
    data = b""
    for i in entries:
        data = data + GitIndexEntry.pack(i)
        # print("write index is "+str(GitIndexEntry.pack(i).hex()))
    sha1 = hashlib.sha1(header + data).digest()
    with open(gitdir / "index", "wb") as f:
        f.write(header + data + sha1)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    # PUT YOUR CODE HERE
    if not "GIT_DIR" in os.environ:
        pathToGitDir = ".git"
    else:
        pathToGitDir = os.environ.get("GIT_DIR")
        print((gitdir / "index").exists())
    # print("path to git is"+pathToGitDir)
    if not details:
        if not (gitdir / "index").exists():
            print()
        else:
            names = []
            with open(gitdir / "index", mode="rb") as f:
                header = f.read(12)
                main_part = f.read()
            unpacked_header = struct.unpack("!L", header[8:])
            for i in range(unpacked_header[0]):
                end = len(main_part) - 1
                for j in range(63, len(main_part), 8):
                    if main_part[j] == 0:
                        end = j
                        break
                names.append((GitIndexEntry.unpack(main_part[:end + 1])).name)
                if len(main_part) != end - 1:
                    main_part = main_part[end + 1:]
            string_with_names = ""
            for i in range(unpacked_header[0]):
                string_with_names = string_with_names + "\n" + names[i]

            print(string_with_names)
    else:
        entries = []
        with open(gitdir / "index", mode="rb") as f:
            header = f.read(12)
            main_part = f.read()
        unpacked_header = struct.unpack("!L", header[8:])
        for i in range(unpacked_header[0]):
            end = len(main_part) - 1
            for j in range(63, len(main_part), 8):
                if main_part[j] == 0:
                    end = j
                    break
            entries.append(str(oct((GitIndexEntry.unpack(main_part[:end + 1])).mode)[2:])+" "+str((GitIndexEntry.unpack(main_part[:end + 1])).sha1.hex()[:40])+" 0\t"+str((GitIndexEntry.unpack(main_part[:end + 1])).name))
            if len(main_part) != end - 1:
                main_part = main_part[end + 1:]
        string_with_names = ""
        for i in range(unpacked_header[0]):
            string_with_names = string_with_names + "\n" + str(entries[i])


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    # PUT YOUR CODE HERE
    entry = {entry.name: entry for entry in read_index(gitdir)}
    for path in paths:
        if str(path) in entry:
            del entry[str(path)]
        with path.open("rb") as f:
            data = f.read()
        stat = os.stat(path)
        sha1 = hash_object(data, "blob", write=True)
        entry.update(
            {
                str(path): GitIndexEntry(
                    ctime_s=int(stat.st_ctime),
                    ctime_n=stat.st_ctime_ns % len(str(int(stat.st_ctime))),
                    mtime_s=int(stat.st_mtime),
                    mtime_n=stat.st_mtime_ns % len(str(int(stat.st_mtime))),
                    dev=stat.st_dev,
                    ino=stat.st_ino,
                    mode=stat.st_mode,
                    uid=stat.st_uid,
                    gid=stat.st_gid,
                    size=stat.st_size,
                    sha1=bytes.fromhex(sha1),
                    flags=7,
                    name=str(path).replace('\\', '/')
                )
            }
        )
    if write:
        entry_list = []
        for name in sorted(entry.keys()):
            entry_list.append((entry[name]))
        write_index(gitdir, entry_list)
