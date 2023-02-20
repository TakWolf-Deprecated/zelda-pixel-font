import logging

from configs import path_define
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.delete_dir(path_define.build_dir)


if __name__ == '__main__':
    main()
