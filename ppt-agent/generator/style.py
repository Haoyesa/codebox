SCENE_STYLES = {
    "投融资汇报": {
        "name": "商务专业",
        "primary": "1A365D",
        "secondary": "2D5A87",
        "accent": "D69E2E",
        "highlight": "E53E3E",
        "font_title": "微软雅黑",
        "font_body": "微软雅黑",
        "layouts": ["center", "left", "split", "grid"],
        "template": "formal",
        "cover_bg": "gradient"
    },
    "内部培训": {
        "name": "学院清新",
        "primary": "2F855A",
        "secondary": "38A169",
        "accent": "ED8936",
        "highlight": "DD6B20",
        "font_title": "微软雅黑",
        "font_body": "微软雅黑",
        "layouts": ["left", "center", "cards", "two-col"],
        "template": "educational",
        "cover_bg": "solid"
    },
    "产品介绍": {
        "name": "科技感",
        "primary": "553C9A",
        "secondary": "6B46C1",
        "accent": "38B2AC",
        "highlight": "319795",
        "font_title": "微软雅黑",
        "font_body": "微软雅黑",
        "layouts": ["center", "split", "modern", "carousel"],
        "template": "modern",
        "cover_bg": "gradient"
    }
}


def get_style(scene: str) -> dict:
    return SCENE_STYLES.get(scene, SCENE_STYLES["投融资汇报"])


def get_layout_for_slide(scene: str, slide_index: int) -> str:
    """根据场景和页码返回不同布局"""
    style = get_style(scene)
    layouts = style["layouts"]
    return layouts[slide_index % len(layouts)]