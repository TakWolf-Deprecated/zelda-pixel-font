from configs.font_config import FontConfig

font_configs = FontConfig.loads()
outputs_name_to_config = {font_config.outputs_name: font_config for font_config in font_configs}

font_formats = ['otf', 'woff2', 'ttf', 'bdf']
