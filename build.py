import logging

import configs
from configs import path_define
from services import font_service, publish_service
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.delete_dir(path_define.build_dir)

    for font_config in configs.font_configs:
        font_service.format_glyph_files(font_config)
        character_mapping, glyph_file_paths = font_service.collect_glyph_files(font_config)
        font_service.make_font_files(font_config, character_mapping, glyph_file_paths)
    publish_service.make_release_zips()


if __name__ == '__main__':
    main()
