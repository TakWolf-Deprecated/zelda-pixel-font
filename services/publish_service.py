import logging
import os
import zipfile

import configs
from configs import path_define, FontConfig
from utils import fs_util

logger = logging.getLogger('publish-service')


def make_release_zips():
    fs_util.make_dirs(path_define.releases_dir)
    for font_format in configs.font_formats:
        file_path = os.path.join(path_define.releases_dir, f'{FontConfig.ZIP_OUTPUTS_NAME}-{font_format}-v{FontConfig.VERSION}.zip')
        with zipfile.ZipFile(file_path, 'w') as file:
            file.write(os.path.join(path_define.project_root_dir, 'LICENSE-CC0'), 'CC0.txt')
            for font_config in configs.font_configs:
                font_file_name = f'{font_config.full_outputs_name}.{font_format}'
                file.write(os.path.join(font_config.outputs_dir, font_file_name), os.path.join(font_config.outputs_name, font_file_name))
        logger.info("Make release zip: '%s'", file_path)
