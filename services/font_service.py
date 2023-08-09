import logging
import math
import os

from pixel_font_builder import FontBuilder, Glyph, StyleName, SerifMode, WidthMode
from pixel_font_builder.opentype import Flavor

from configs import path_define, FontConfig
from utils import fs_util, glyph_util

logger = logging.getLogger('font-service')


def format_glyph_files(font_config: FontConfig):
    root_dir = os.path.join(path_define.glyphs_dir, font_config.outputs_name)
    for glyph_file_dir, glyph_file_name in fs_util.walk_files(root_dir):
        if not glyph_file_name.endswith('.png'):
            continue
        glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
        glyph_data, glyph_width, glyph_height = glyph_util.load_glyph_data_from_png(glyph_file_path)
        assert (glyph_height - font_config.size) % 2 == 0, f"Incorrect glyph data: '{glyph_file_path}'"
        if glyph_height > font_config.line_height:
            for i in range((glyph_height - font_config.line_height) // 2):
                glyph_data.pop(0)
                glyph_data.pop()
        elif glyph_height < font_config.line_height:
            for i in range((font_config.line_height - glyph_height) // 2):
                glyph_data.insert(0, [0 for _ in range(glyph_width)])
                glyph_data.append([0 for _ in range(glyph_width)])
        glyph_util.save_glyph_data_to_png(glyph_data, glyph_file_path)
        logger.info("Format glyph file: '%s'", glyph_file_path)


def collect_glyph_files(font_config: FontConfig) -> tuple[dict[int, str], list[tuple[str, str]]]:
    root_dir = os.path.join(path_define.glyphs_dir, font_config.outputs_name)

    registry = {}
    for glyph_file_dir, glyph_file_name in fs_util.walk_files(root_dir):
        if not glyph_file_name.endswith('.png'):
            continue
        glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
        c_name = glyph_file_name.removesuffix('.png')
        if c_name == 'notdef':
            code_point = -1
        elif c_name == 'space':
            code_point = ord(' ')
        elif c_name == 'full_stop':
            code_point = ord('.')
        else:
            code_point = ord(c_name)
        registry[code_point] = glyph_file_path

    sequence = list(registry.keys())
    sequence.sort()

    character_mapping = {}
    glyph_file_infos = []
    for code_point in sequence:
        if code_point == -1:
            glyph_name = '.notdef'
        else:
            glyph_name = f'uni{code_point:04X}'
            character_mapping[code_point] = glyph_name
        glyph_file_infos.append((glyph_name, registry[code_point]))

    fallback_letter_offsets = [code_point - ord('A') for code_point in [ord('a'), ord('Ａ'), ord('ａ')]]
    for code_point in range(ord('A'), ord('Z') + 1):
        if code_point not in character_mapping:
            continue
        glyph_name = character_mapping[code_point]
        for fallback_letter_offset in fallback_letter_offsets:
            fallback_code_point = code_point + fallback_letter_offset
            character_mapping[fallback_code_point] = glyph_name

    fallback_number_offset = ord('０') - ord('0')
    for code_point in range(ord('0'), ord('9') + 1):
        if code_point not in character_mapping:
            continue
        glyph_name = character_mapping[code_point]
        fallback_code_point = code_point + fallback_number_offset
        character_mapping[fallback_code_point] = glyph_name

    return character_mapping, glyph_file_infos


def _create_builder(font_config: FontConfig, character_mapping: dict[int, str], glyph_file_infos: list[tuple[str, str]]) -> FontBuilder:
    builder = FontBuilder()

    builder.metrics.size = font_config.size
    builder.metrics.ascent = font_config.ascent
    builder.metrics.descent = font_config.descent
    builder.metrics.x_height = font_config.x_height
    builder.metrics.cap_height = font_config.cap_height

    builder.meta_infos.version = FontConfig.VERSION
    builder.meta_infos.family_name = font_config.family_name
    builder.meta_infos.style_name = StyleName.REGULAR
    builder.meta_infos.serif_mode = SerifMode.SANS_SERIF
    builder.meta_infos.width_mode = WidthMode.MONOSPACED
    builder.meta_infos.manufacturer = FontConfig.MANUFACTURER
    builder.meta_infos.designer = FontConfig.DESIGNER
    builder.meta_infos.description = font_config.description
    builder.meta_infos.copyright_info = FontConfig.COPYRIGHT_INFO
    builder.meta_infos.license_info = FontConfig.LICENSE_INFO
    builder.meta_infos.vendor_url = FontConfig.VENDOR_URL
    builder.meta_infos.designer_url = FontConfig.DESIGNER_URL
    builder.meta_infos.license_url = FontConfig.LICENSE_URL

    builder.character_mapping.update(character_mapping)

    for glyph_name, glyph_file_path in glyph_file_infos:
        glyph_data, glyph_width, glyph_height = glyph_util.load_glyph_data_from_png(glyph_file_path)
        offset_y = math.floor((font_config.ascent + font_config.descent - glyph_height) / 2)
        builder.glyphs.append(Glyph(
            name=glyph_name,
            advance_width=glyph_width,
            offset=(0, offset_y),
            data=glyph_data,
        ))

    return builder


def make_font_files(font_config: FontConfig, character_mapping: dict[int, str], glyph_file_infos: list[tuple[str, str]]):
    fs_util.make_dirs(font_config.outputs_dir)

    builder = _create_builder(font_config, character_mapping, glyph_file_infos)

    otf_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.otf')
    builder.save_otf(otf_file_path)
    logger.info("Make font file: '%s'", otf_file_path)

    woff2_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.woff2')
    builder.save_otf(woff2_file_path, flavor=Flavor.WOFF2)
    logger.info("Make font file: '%s'", woff2_file_path)

    ttf_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.ttf')
    builder.save_ttf(ttf_file_path)
    logger.info("Make font file: '%s'", ttf_file_path)

    bdf_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.bdf')
    builder.save_bdf(bdf_file_path)
    logger.info("Make font file: '%s'", bdf_file_path)
