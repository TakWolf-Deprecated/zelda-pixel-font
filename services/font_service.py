import logging
import os

import png
from pixel_font_builder import FontBuilder, Glyph, StyleName, SerifMode, WidthMode

from configs import path_define, FontConfig
from utils import fs_util

logger = logging.getLogger('font-service')


def _load_glyph_data_from_png(file_path: str) -> tuple[list[list[int]], int, int]:
    width, height, bitmap, _ = png.Reader(filename=file_path).read()
    data = []
    for bitmap_row in bitmap:
        data_row = []
        for x in range(0, width * 4, 4):
            alpha = bitmap_row[x + 3]
            if alpha > 127:
                data_row.append(1)
            else:
                data_row.append(0)
        data.append(data_row)
    return data, width, height


def _save_glyph_data_to_png(data: list[list[int]], file_path: str):
    bitmap = []
    for data_row in data:
        bitmap_row = []
        for x in data_row:
            bitmap_row.append(0)
            bitmap_row.append(0)
            bitmap_row.append(0)
            if x == 0:
                bitmap_row.append(0)
            else:
                bitmap_row.append(255)
        bitmap.append(bitmap_row)
    png.from_array(bitmap, 'RGBA').save(file_path)


def format_glyph_files(font_config: FontConfig):
    root_dir = os.path.join(path_define.glyphs_dir, font_config.outputs_name)
    for glyph_file_dir, glyph_file_name in fs_util.walk_files(root_dir):
        if not glyph_file_name.endswith('.png'):
            continue
        glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
        glyph_data, glyph_width, glyph_height = _load_glyph_data_from_png(glyph_file_path)
        assert (glyph_height - font_config.size) % 2 == 0, f"Incorrect glyph data: '{glyph_file_path}'"
        if glyph_height > font_config.line_height:
            for i in range((glyph_height - font_config.line_height) // 2):
                glyph_data.pop(0)
                glyph_data.pop()
        elif glyph_height < font_config.line_height:
            for i in range((font_config.line_height - glyph_height) // 2):
                glyph_data.insert(0, [0 for _ in range(glyph_width)])
                glyph_data.append([0 for _ in range(glyph_width)])
        _save_glyph_data_to_png(glyph_data, glyph_file_path)
        logger.info(f"Format glyph file: '{glyph_file_path}'")


def collect_glyph_files(font_config: FontConfig) -> tuple[dict[int, str], dict[str, str]]:
    character_mapping = {}
    glyph_file_paths = {}

    root_dir = os.path.join(path_define.glyphs_dir, font_config.outputs_name)
    for glyph_file_dir, glyph_file_name in fs_util.walk_files(root_dir):
        if not glyph_file_name.endswith('.png'):
            continue
        glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
        c_name = glyph_file_name.removesuffix('.png')
        if c_name == 'notdef':
            glyph_name = '.notdef'
        else:
            if c_name == 'space':
                code_point = ord(' ')
            elif c_name == 'full_stop':
                code_point = ord('.')
            else:
                code_point = ord(c_name)
            glyph_name = f'uni{code_point:04X}'
            character_mapping[code_point] = glyph_name
        glyph_file_paths[glyph_name] = glyph_file_path

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

    return character_mapping, glyph_file_paths


def _create_builder(font_config: FontConfig, character_mapping: dict[int, str], glyph_file_paths: dict[str, str]) -> FontBuilder:
    builder = FontBuilder(
        font_config.size,
        font_config.ascent,
        font_config.descent,
        font_config.x_height,
        font_config.cap_height,
    )

    builder.character_mapping.update(character_mapping)
    for glyph_name, glyph_file_path in glyph_file_paths.items():
        glyph_data, glyph_width, glyph_height = _load_glyph_data_from_png(glyph_file_path)
        offset_y = font_config.box_origin_y + (glyph_height - font_config.size) // 2 - glyph_height
        builder.add_glyph(Glyph(
            name=glyph_name,
            advance_width=glyph_width,
            offset=(0, offset_y),
            data=glyph_data,
        ))

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

    return builder


def make_font_files(font_config: FontConfig, character_mapping: dict[int, str], glyph_file_paths: dict[str, str]):
    fs_util.make_dirs(font_config.outputs_dir)

    builder = _create_builder(font_config, character_mapping, glyph_file_paths)
    otf_builder = builder.to_otf_builder()
    otf_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.otf')
    otf_builder.save(otf_file_path)
    logger.info(f"Make font file: '{otf_file_path}'")
    otf_builder.font.flavor = 'woff2'
    woff2_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.woff2')
    otf_builder.save(woff2_file_path)
    logger.info(f"Make font file: '{woff2_file_path}'")
    ttf_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.ttf')
    builder.save_ttf(ttf_file_path)
    logger.info(f"Make font file: '{ttf_file_path}'")
    bdf_file_path = os.path.join(font_config.outputs_dir, f'{font_config.full_outputs_name}.bdf')
    builder.save_bdf(bdf_file_path)
    logger.info(f"Make font file: '{bdf_file_path}'")
