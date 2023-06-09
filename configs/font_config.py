import os
import tomllib

from configs import path_define

full_display_name_format = 'Zelda Pixel - {name}'
full_unique_name_format = 'Zelda-Pixel-{name}'
full_output_name_format = 'zelda-pixel-{name}'
style_name = 'Regular'
version = '1.0.0'
copyright_string = 'This Font Software is made by TakWolf (https://takwolf.com). The Copyright of Alphabet belongs to Nintendo.'
designer = 'TakWolf'
description_format = 'The Legend of Zelda - Pixel Font: {alphabet_name}'
vendor_url = 'https://zelda-pixel-font.takwolf.com'
designer_url = 'https://takwolf.com'
license_description = 'This Font Software is licensed under the Creative Commons Zero v1.0 Universal. The Copyright of Alphabet belongs to Nintendo.'
license_info_url = 'https://creativecommons.org/publicdomain/zero/1.0/'


class VerticalMetrics:
    def __init__(self, ascent, descent, x_height, cap_height):
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height


class FontConfig:
    @staticmethod
    def loads():
        font_configs = []
        for output_name in os.listdir(path_define.glyphs_dir):
            glyphs_dir = os.path.join(path_define.glyphs_dir, output_name)
            if not os.path.isdir(glyphs_dir):
                continue
            config_file_path = os.path.join(glyphs_dir, 'config.toml')
            if not os.path.isfile(config_file_path):
                continue
            with open(config_file_path, 'rb') as config_file:
                config_data = tomllib.load(config_file)['font']
            font_config = FontConfig(config_data, output_name)
            font_configs.append(font_config)
        font_configs.sort(key=lambda x: x.output_name)
        return font_configs

    def __init__(self, config_data, output_name, px_units=100):
        self.display_name = config_data['display_name']
        self.unique_name = config_data['unique_name']
        self.alphabet_name = config_data['alphabet_name']

        self.output_name = output_name
        self.outputs_dir = os.path.join(path_define.outputs_dir, output_name)
        self.full_display_name = full_display_name_format.format(name=self.display_name)
        self.full_unique_name = full_unique_name_format.format(name=self.unique_name)
        self.full_output_name = full_output_name_format.format(name=output_name)

        self.px = config_data['px']
        self.line_height_px = config_data['line_height_px']
        assert (self.line_height_px - self.px) % 2 == 0, output_name
        self.box_origin_y_px = config_data['box_origin_y_px']
        self.x_height_px = config_data['x_height_px']
        self.cap_height_px = config_data['cap_height_px']
        self.px_units = px_units

    def get_name_strings(self):
        return {
            'copyright': copyright_string,
            'familyName': self.full_display_name,
            'styleName': style_name,
            'uniqueFontIdentifier': f'{self.full_unique_name}-{style_name};{version}',
            'fullName': self.full_display_name,
            'version': version,
            'psName': f'{self.full_unique_name}-{style_name}',
            'designer': designer,
            'description': description_format.format(alphabet_name=self.alphabet_name),
            'vendorURL': vendor_url,
            'designerURL': designer_url,
            'licenseDescription': license_description,
            'licenseInfoURL': license_info_url,
        }

    def get_units_per_em(self):
        return self.px * self.px_units

    def get_box_origin_y(self):
        return self.box_origin_y_px * self.px_units

    def get_vertical_metrics(self):
        ascent = (self.box_origin_y_px + (self.line_height_px - self.px) // 2) * self.px_units
        descent = ascent - self.line_height_px * self.px_units
        x_height = self.x_height_px * self.px_units
        cap_height = self.cap_height_px * self.px_units
        return VerticalMetrics(ascent, descent, x_height, cap_height)
