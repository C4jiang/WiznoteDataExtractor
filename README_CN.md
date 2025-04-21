# 为知笔记数据采集器

[English](README.md) | [中文](README_CN.md)

一个用于从为知笔记(note.wiz.cn)提取笔记并将其保存为Markdown文件的工具，保留格式和图片。

## 功能特点

- 提取笔记标题、内容、标签和最后修改日期
- 将HTML内容转换为Markdown格式
- 下载并本地保存嵌入的图片
- 正确格式化代码块
- 在YAML前言中保留元数据

## 环境要求

- Python 3.6+
- Chrome浏览器
- ChromeDriver
- 必需的Python包（见安装部分）

## 安装方法

1. 克隆此仓库：
   ```
   git clone https://github.com/你的用户名/WiznoteExtractor.git
   cd WiznoteExtractor
   ```

2. 安装所需的Python包：
   ```
   pip install selenium beautifulsoup4 html2text requests
   ```

3. 安装ChromeDriver：
   - 从[ChromeDriver官方网站](https://sites.google.com/chromium.org/driver/)下载与你的Chrome浏览器版本匹配的ChromeDriver
   - Windows系统：
     - 解压下载的zip文件
     - 将ChromeDriver位置添加到PATH环境变量，或者
     - 将chromedriver.exe放置在已经在PATH中的目录中

   - macOS系统：
     ```
     brew install chromedriver
     ```
   
   - Linux系统：
     ```
     sudo apt install chromium-chromedriver
     ```
     或从官方网站下载Linux版本并将其添加到PATH中

4. 配置用户数据目录：
   - 打开`WiznoteDataExtractor.py`并修改`init_driver()`函数中的`user_data_dir`路径为你系统上的一个位置

## 使用方法

1. 运行脚本：
   ```
   python WiznoteDataExtractor.py
   ```

2. 一个Chrome浏览器窗口将会打开。当提示时，你需要手动登录到你的为知笔记账户。

3. 登录后，导航到你想要采集的笔记页面。

4. 在终端中按回车键采集当前页面。

5. 脚本将提取笔记内容，转换为Markdown格式，下载任何嵌入的图片，并将所有内容保存到与脚本同一目录下的Markdown文件中。

6. 继续导航到其他笔记并按回车键采集它们，或者输入'exit'退出程序。

## 注意事项

- 该脚本为Chrome创建一个用户配置文件以维持登录会话。
- 图片保存在Markdown文件旁边的`index_files`文件夹中。
- 如果使用浏览器方法下载图片失败，它将退而使用requests库。

## 许可证

[在此添加你的许可证信息]

## 贡献

欢迎贡献！请随时提交Pull Request。
