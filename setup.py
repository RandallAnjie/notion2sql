from setuptools import setup, find_packages

# 直接定义依赖项，不从requirements.txt读取
requirements = [
    "notion-client>=2.0.0",
    "requests>=2.25.1",
    "python-dotenv>=0.19.0",
    "SQLAlchemy>=1.4.0",
    "pytest>=6.2.5"
]

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Notion2SQL - 一个将Notion数据库转换为SQL接口的工具"

setup(
    name="notion2sql",
    version="0.1.0",
    author="Randall",
    author_email="randall@randallanjie.com",
    description="一个将Notion数据库转换为SQL接口的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/randallanjie/notion2sql",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
