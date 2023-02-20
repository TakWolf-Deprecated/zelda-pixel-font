import logging
import os

from configs import path_define
from utils import glyph_util

logger = logging.getLogger('design-service')


def verify_glyph_files(font_config):
    glyphs_dir = os.path.join(path_define.glyphs_dir, font_config.output_name)
    for glyph_file_name in os.listdir(glyphs_dir):
        if not glyph_file_name.endswith('.png'):
            continue
        glyph_file_path = os.path.join(glyphs_dir, glyph_file_name)
        glyph_data, width, height = glyph_util.load_glyph_data_from_png(glyph_file_path)

        assert (height - font_config.px) % 2 == 0, glyph_file_path
        if height > font_config.line_height_px:
            for i in range(int((height - font_config.line_height_px) / 2)):
                glyph_data.pop(0)
                glyph_data.pop()
        elif height < font_config.line_height_px:
            for i in range(int((font_config.line_height_px - height) / 2)):
                glyph_data.insert(0, [0 for _ in range(width)])
                glyph_data.append([0 for _ in range(width)])

        glyph_util.save_glyph_data_to_png(glyph_data, glyph_file_path)
        logger.info(f'format glyph file {glyph_file_path}')
