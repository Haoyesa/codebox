import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


async def generate_content(keywords: str, background: str, scene: str, style: dict) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = f"""你是一个专业的PPT内容生成助手。根据用户提供的关键词、背景信息和使用场景，生成完整的PPT内容。

当前场景：{scene}
风格要求：{style['name']}，配色方案 {style['primary']}/{style['secondary']}，布局多样

请生成包含以下结构的PPT内容：
1. 封面页：主题、副标题
2. 目录页（可选）
3. 内容页（3-5页）：每页有标题、要点
4. 结束页

内容要求：
- 专业、逻辑清晰
- 扩写关键词为完整语句
- 每页内容精炼，适合演示阅读

输出格式为JSON：
{{
  "title": "PPT标题",
  "subtitle": "副标题",
  "slides": [
    {{"type": "cover", "title": "", "subtitle": ""}},
    {{"type": "content", "title": "页面标题", "bullets": ["要点1", "要点2", ...]}},
    {{"type": "ending", "title": "", "subtitle": ""}}
  ]
}}"""

    user_message = f"""关键词：{keywords}
背景信息：{background}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    import json
    # 过滤出文本类型的block，避免thinking block
    text_blocks = [block for block in response.content if block.type == "text"]
    content_text = text_blocks[0].text if text_blocks else ""

    # 尝试解析JSON
    try:
        # 尝试提取markdown代码块中的JSON
        if "```json" in content_text:
            start = content_text.find("```json") + 7
            end = content_text.find("```", start)
            content_text = content_text[start:end].strip()
        elif "```" in content_text:
            start = content_text.find("```") + 3
            end = content_text.find("```", start)
            content_text = content_text[start:end].strip()

        return json.loads(content_text)
    except json.JSONDecodeError:
        # 如果解析失败，返回结构化降级内容
        return {
            "title": keywords,
            "subtitle": background[:50] if background else "",
            "slides": [
                {"type": "cover", "title": keywords, "subtitle": background[:100] if background else ""},
                {"type": "content", "title": "内容概述", "bullets": [background] if background else ["内容待补充"]},
                {"type": "ending", "title": "谢谢", "subtitle": ""}
            ]
        }