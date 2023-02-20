import logging
import os
import zipfile

import configs
from configs import path_define
from utils import fs_util

logger = logging.getLogger('publish-service')


def make_release_zips(font_formats=None):
    if font_formats is None:
        font_formats = configs.font_formats

    fs_util.make_dirs_if_not_exists(path_define.releases_dir)
    for font_format in font_formats:
        zip_file_path = os.path.join(path_define.releases_dir, f'zelda-pixel-font-{font_format}-v{configs.font_version}.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(os.path.join(path_define.project_root_dir, 'LICENSE-CC0'), 'CC0.txt')
            for font_config in configs.font_configs:
                font_file_name = f'{font_config.full_output_name}.{font_format}'
                zip_file.write(os.path.join(font_config.outputs_dir, font_file_name), os.path.join(font_config.output_name, font_file_name))
        logger.info(f'make {zip_file_path}')
