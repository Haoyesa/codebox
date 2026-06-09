import requests
from typing import Optional


UNSPLASH_ACCESS_KEY = "demo"  # 替换为你的Unsplash API Key


def search_image(keyword: str) -> Optional[str]:
    """
    从Unsplash图库搜索图片，返回URL
    如果没有API Key，使用占位图
    """
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "demo":
        # 使用placeholder图片
        return f"https://source.unsplash.com/800x600/?{keyword.replace(' ', ',')}"

    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": keyword,
            "per_page": 1,
            "orientation": "landscape"
        }
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data["results"]:
                return data["results"][0]["urls"]["regular"]
    except Exception:
        pass

    return f"https://source.unsplash.com/800x600/?{keyword.replace(' ', ',')}"


def fetch_image_as_base64(url: str) -> Optional[str]:
    """下载图片并转为base64"""
    import base64
    import io
    from PIL import Image

    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content))
            # 压缩到合理大小
            img = img.convert("RGB")
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=85)
            return base64.b64encode(output.getvalue()).decode()
    except Exception:
        pass
    return None