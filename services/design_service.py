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
            for i in range((height - font_config.line_height_px) // 2):
                glyph_data.pop(0)
                glyph_data.pop()
        elif height < font_config.line_height_px:
            for i in range((font_config.line_height_px - height) // 2):
                glyph_data.insert(0, [0 for _ in range(width)])
                glyph_data.append([0 for _ in range(width)])

        glyph_util.save_glyph_data_to_png(glyph_data, glyph_file_path)
        logger.info(f'format glyph file {glyph_file_path}')


def collect_glyph_files(font_config):
    alphabet = set()
    glyph_file_paths = {}

    glyphs_dir = os.path.join(path_define.glyphs_dir, font_config.output_name)
    for glyph_file_name in os.listdir(glyphs_dir):
        if not glyph_file_name.endswith('.png'):
            continue
        glyph_file_path = os.path.join(glyphs_dir, glyph_file_name)
        c_name = glyph_file_name.removesuffix('.png')
        if c_name == 'notdef':
            glyph_file_paths['.notdef'] = glyph_file_path
            continue
        elif c_name == 'space':
            c = ' '
        elif c_name == 'full_stop':
            c = '.'
        else:
            c = c_name
        alphabet.add(c)
        glyph_file_paths[ord(c)] = glyph_file_path

    fallback_letter_offsets = [code_point - ord('A') for code_point in [ord('a'), ord('Ａ'), ord('ａ')]]
    for code_point in range(ord('A'), ord('Z') + 1):
        c = chr(code_point)
        if c not in alphabet:
            continue
        for fallback_letter_offset in fallback_letter_offsets:
            fallback_code_point = code_point + fallback_letter_offset
            fallback_c = chr(fallback_code_point)
            alphabet.add(fallback_c)
            glyph_file_paths[fallback_code_point] = glyph_file_paths[code_point]

    fallback_number_offset = ord('０') - ord('0')
    for code_point in range(ord('0'), ord('9') + 1):
        c = chr(code_point)
        if c not in alphabet:
            continue
        fallback_code_point = code_point + fallback_number_offset
        fallback_c = chr(fallback_code_point)
        alphabet.add(fallback_c)
        glyph_file_paths[fallback_code_point] = glyph_file_paths[code_point]

    alphabet = list(alphabet)
    alphabet.sort()
    return alphabet, glyph_file_paths
