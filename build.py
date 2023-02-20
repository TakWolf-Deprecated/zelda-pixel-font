import logging

import configs
from configs import path_define
from services import design_service
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.delete_dir(path_define.build_dir)

    for font_config in configs.font_configs:
        design_service.verify_glyph_files(font_config)
        alphabet, glyph_file_paths = design_service.collect_glyph_files(font_config)


if __name__ == '__main__':
    main()
