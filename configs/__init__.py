from configs.font_config import FontConfig

font_configs = FontConfig.loads()
font_config_map = {font_config.output_name: font_config for font_config in font_configs}

font_formats = ['otf', 'woff2', 'ttf']
