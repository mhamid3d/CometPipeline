import os


def rec_build(dir, subDirs):
    os.mkdir(dir)
    if subDirs:
        for k, v in subDirs.items():
            rec_build(os.path.join(dir, k), v)