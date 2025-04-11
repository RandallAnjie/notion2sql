# Notion2SQL

一个将Notion数据库转换为SQL接口的工具，让您可以像操作传统数据库一样操作Notion页面中的数据库。

## 特性

- 将Notion数据库映射为SQL表
- 支持对Notion数据库进行CRUD操作
- 简单易用的API接口
- 支持所有Notion属性类型，包括：
  - 文本、数字、选择器、多选、日期等基本类型
  - 自增ID（unique_id类型）
  - JSON格式数据自动解析
  - 文件、人员和关系类型
  - 特殊类型处理（按钮、时间戳等）

## 安装

```bash
pip install notion2sql
```

## 使用方法

### 基本用法

```python
from notion2sql import NotionClient

# 初始化客户端
client = NotionClient(api_key="your_notion_api_key")

# 连接到Notion页面
page = client.connect_page(page_id="your_page_id")

# 获取数据库
db = page.get_database_by_name("数据库名称")

# 获取数据库信息
print(f"数据库名称: {db.name}")
print(f"列数: {db.column_count}")
print(f"行数: {db.row_count}")

# 获取列信息
columns = db.get_columns()
for col_name, col_type in columns.items():
    print(f"{col_name}: {col_type}")

# 获取样本数据
sample_data = db.get_sample_data(limit=2)
for item in sample_data:
    print(f"\n记录:")
    for key, value in item['properties'].items():
        print(f"  {key}: {value}")

# 添加新记录
new_item = db.add_item({
    "Name": "新项目",
    "选择": "选择1",
    "文本": "测试文本",
    "电话": "12345678900",
    "数字": 100,
    "复选框1": True,
    "复选框2": False,
    "多选": ["多选1", "多选2"],
    "电子邮件": "test@example.com"
})

# 查询记录
results = db.query(filter={
    "property": "Name",
    "title": {
        "equals": "新项目"
    }
})

# 更新记录
updated_item = db.update_item(
    item_id=new_item['id'],
    properties={
        "Name": "更新后的项目",
        "数字": 200,
        "复选框1": False,
        "复选框2": True
    }
)

# 删除记录
delete_result = db.delete_item(new_item['id'])
```

### 特殊类型处理

Notion2SQL会自动处理以下特殊类型：

- `unique_id`: 自增ID类型，在SQL操作中自动跳过
- `button`: 按钮类型，在SQL操作中自动跳过
- `files`: 文件类型，提供专门的文件操作方法
- `people`: 人员类型，提供专门的人员管理方法
- `last_edited_time`: 最后编辑时间，在SQL操作中自动跳过
- `created_time`: 创建时间，在SQL操作中自动跳过

### 文件操作

```python
# 获取文件列表
if "File" in item['properties']:
    files = item['properties']['File']
    print(f"文件列表: {files}")

# 下载文件
if files:
    for file in files:
        print(f"文件名: {file['name']}, URL: {file['url']}")
        # 使用requests库下载文件
        import requests
        response = requests.get(file['url'])
        with open(f"downloads/{file['name']}", 'wb') as f:
            f.write(response.content)
```

### 人员管理

```python
# 获取人员列表
if "人员" in item['properties']:
    people = item['properties']['人员']
    print(f"人员列表: {people}")
```

### SQL接口

```python
from notion2sql import NotionSQLInterface

# 创建SQL接口
sql = NotionSQLInterface(db)

# 执行SQL查询
results = sql.execute_sql("SELECT * FROM notion_data WHERE Name LIKE '%项目%'")

# 插入数据
sql.insert({"Name": "SQL插入的项目", "Status": "计划中"})

# 更新数据
sql.update(item_id="item_id_here", values={"Status": "已完成"})

# 删除数据
sql.delete(item_id="item_id_here")

# 刷新数据（从Notion同步到SQL表）
sql.refresh()
```

## 环境变量

在项目根目录创建`.env`文件，并添加以下内容：

```
NOTION_API_KEY=your_notion_integration_token
NOTION_PAGE_ID=your_page_id_here
```

## Notion API 访问设置

1. 创建Notion集成：访问 https://www.notion.so/my-integrations
2. 获取API密钥
3. 在Notion页面中，点击右上角"共享"按钮，将您的集成添加到页面中并授予"可以编辑"权限

## 依赖项

- `notion-client`: Notion API客户端
- `sqlalchemy`: SQL数据库操作
- `requests`: 文件下载功能
- `python-dotenv`: 环境变量管理

## 授权

该项目基于MIT许可证开源。
