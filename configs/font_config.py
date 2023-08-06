import os
import tomllib
from typing import Final

from configs import path_define


class FontConfig:
    VERSION: Final[str] = '1.2.0'
    FAMILY_NAME_FORMAT: Final[str] = 'Zelda Pixel {font_name}'
    ZIP_OUTPUTS_NAME: Final[str] = 'zelda-pixel-font'
    MANUFACTURER: Final[str] = 'TakWolf'
    DESIGNER: Final[str] = 'TakWolf'
    DESCRIPTION_FORMAT: Final[str] = 'The Legend of Zelda - Pixel Font: {alphabet_name}'
    COPYRIGHT_INFO: Final[str] = 'This Font Software is made by TakWolf (https://takwolf.com). The Copyright of Alphabet belongs to Nintendo.'
    LICENSE_INFO: Final[str] = 'This Font Software is licensed under the Creative Commons Zero v1.0 Universal. The Copyright of Alphabet belongs to Nintendo.'
    VENDOR_URL: Final[str] = 'https://zelda-pixel-font.takwolf.com'
    DESIGNER_URL: Final[str] = 'https://takwolf.com'
    LICENSE_URL: Final[str] = 'https://creativecommons.org/publicdomain/zero/1.0/'

    @staticmethod
    def loads() -> list['FontConfig']:
        configs = []
        for outputs_name in os.listdir(path_define.glyphs_dir):
            config_file_path = os.path.join(path_define.glyphs_dir, outputs_name, 'config.toml')
            if not os.path.isfile(config_file_path):
                continue
            with open(config_file_path, 'rb') as config_file:
                config_data: dict = tomllib.load(config_file)['font']
            config = FontConfig(config_data)
            assert config.outputs_name == outputs_name
            configs.append(config)
        configs.sort(key=lambda x: x.name)
        return configs

    def __init__(self, config_data: dict):
        self.name: str = config_data['name']
        self.family_name = FontConfig.FAMILY_NAME_FORMAT.format(font_name=self.name)
        self.outputs_name = self.name.lower().replace(' ', '-')
        self.full_outputs_name = self.family_name.lower().replace(' ', '-')

        alphabet_name: str = config_data['alphabet_name']
        self.description = FontConfig.DESCRIPTION_FORMAT.format(alphabet_name=alphabet_name)

        self.size: int = config_data['size']
        self.ascent: int = config_data['ascent']
        self.descent: int = config_data['descent']
        assert (self.line_height - self.size) % 2 == 0, f"Font config '{self.name}': the difference between 'line_height' and 'size' must be a multiple of 2"
        self.x_height: int = config_data['x_height']
        self.cap_height: int = config_data['cap_height']

        self.outputs_dir = os.path.join(path_define.outputs_dir, self.outputs_name)

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent
