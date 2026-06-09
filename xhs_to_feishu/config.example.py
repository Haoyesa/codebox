# 飞书多维表格配置
# 复制此文件为 config.py 并填入你的实际值

# 飞书开放平台应用凭证
# 获取方式: https://open.feishu.cn/app -> 你的应用 -> 凭证与基础信息
FEISHU_APP_ID = "cli_xxxxxxxxxxxxxx"
FEISHU_APP_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 多维表格信息
# 获取方式: 打开飞书多维表格 -> 右上角分享 -> 复制链接
# 链接格式: https://xxx.feishu.cn/base/xxxxxxxxxxxxx?table=xxxxxxxxxxxxx
#           app_token         ↑ 这个      table_id  ↑ 这个
FEISHU_APP_TOKEN = "xxxxxxxxxxxxxx"
FEISHU_TABLE_ID = "tblxxxxxxxxxxxxxx"

# 获取 Access Token (需要先在飞书开放平台创建应用并开通多维表格权限)
# 临时方案: 可以手动获取 token 填入，或运行 feishu_auth.py 获取
FEISHU_ACCESS_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 如果没有 Access Token，可以让脚本自动获取（需要 App ID 和 App Secret）
# 设置为 True 启用自动获取
AUTO_GET_ACCESS_TOKEN = False