from selenium import webdriver
from bs4 import BeautifulSoup
import os
import re
import html2text
import requests
import shutil
from urllib.parse import urlparse, parse_qs
import time


user_data_dir = r'C:\Users\C14sama\AppData\Local\Google\Chrome\User Data\CollectBot'


def get_data_from_page(driver, url):
    data = {}
    return data


def extract_tags(soup):
    """Extract tags from the page"""
    tags = []
    # Find all spans with class MuiChip-label
    tag_elements = soup.select('span.MuiChip-label')
    
    if tag_elements:
        for tag_element in tag_elements:
            tags.append(tag_element.text)
        print(f"Found {len(tags)} tags: {', '.join(tags)}")
    else:
        print("No tags found")
    
    return tags


def extract_title_and_content(driver):
    """Extract title and content from the current page"""
    # Extract title from main page
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract tags from main page before switching to iframe
    tags = extract_tags(soup)
    
    # Extract last modified date
    modified_date = None
    modified_elements = soup.select('p.MuiTypography-root.MuiTypography-body2 span')
    for element in modified_elements:
        text = element.text
        if '最近修改' in text:
            # Extract the date part
            date_match = re.search(r'最近修改：(\d{4}/\d{1,2}/\d{1,2})', text)
            if date_match:
                modified_date = date_match.group(1)
                print(f"Found last modified date: {modified_date}")
                break
    
    # Extract title - improved to target only the title within header
    title = "Untitled"
    
    # First locate the header element
    header_element = soup.select_one('header.MuiPaper-root.MuiAppBar-root')
    
    if header_element:
        # Now find the paragraph within the header
        title_element = header_element.select_one('p.MuiTypography-root.MuiTypography-body2')
        if title_element:
            title = title_element.text
            print(f"Found title within header: {title}")
        else:
            print("No title paragraph found within header")
    else:
        print("Header element not found, trying alternative selectors")
        # Fallback to the original approach if header not found
        title_elements = soup.select('p.MuiTypography-root.MuiTypography-body2')
        if title_elements:
            for title_element in title_elements:
                # Use the first non-empty title element
                if title_element.text.strip():
                    title = title_element.text
                    print(f"Found title using fallback: {title}")
                    break
    
    # IMPORTANT: Content is inside an iframe
    try:
        print("Attempting to switch to iframe...")
        # Find the iframe and switch to it
        iframe = driver.find_element('css selector', 'iframe.wiz-editor-iframe')
        driver.switch_to.frame(iframe)
        print("Successfully switched to iframe")
        
        # Now extract content from within the iframe
        iframe_content = driver.page_source
        iframe_soup = BeautifulSoup(iframe_content, 'html.parser')
        
        # Look for content div inside iframe
        content_container = iframe_soup.select_one('div.content, div.wiz-template-editable')
        
        if not content_container:
            print("Content container not found in iframe, trying to get entire body...")
            content_container = iframe_soup.find('body')
        
        if content_container:
            content = content_container.decode_contents()
            print(f"Content extracted from iframe: {len(content)} characters")
        else:
            # If still nothing, get the entire iframe HTML
            content = iframe_content
            print(f"Using entire iframe content: {len(content)} characters")
        
        # Switch back to main document
        driver.switch_to.default_content()
        
    except Exception as e:
        print(f"Error accessing iframe: {str(e)}")
        content = ""
        # Switch back to main document if there was an error
        try:
            driver.switch_to.default_content()
        except e:
            pass
    
    return title, content, tags, modified_date


def html_to_markdown(html_content):
    """Convert HTML content to markdown format"""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.bypass_tables = False
    converter.ignore_images = False
    
    # Convert HTML to markdown
    markdown_content = converter.handle(html_content)
    
    # Fix code blocks formatting
    # Look for <pre> and <code> blocks that might not be properly formatted
    markdown_content = fix_code_blocks(markdown_content)
    
    return markdown_content

def fix_code_blocks(markdown_content):
    """Ensure code blocks are properly formatted with triple backticks"""
    
    # Pattern 1: Find indented code blocks (4+ spaces) not already in backtick blocks
    pattern1 = re.compile(r'(?<!\n```\n)(?:^( {4,}).*?$(?:\n\1.*?$)*)', re.MULTILINE)
    
    def replace_indented_block(match):
        block = match.group(0)
        # Remove common indentation
        dedented = re.sub(r'^ {4}', '', block, flags=re.MULTILINE)
        return f"\n```\n{dedented}\n```\n"
    
    # Replace indented code blocks
    markdown_content = pattern1.sub(replace_indented_block, markdown_content)
    
    # Pattern 2: Find HTML-like code blocks with <pre> or <code> tags that weren't properly converted
    pattern2 = re.compile(r'<pre>(.+?)</pre>', re.DOTALL)
    pattern3 = re.compile(r'<code>(.+?)</code>', re.DOTALL)
    
    def replace_html_block(match):
        code = match.group(1).strip()
        return f"\n```\n{code}\n```\n"
    
    # Replace HTML code blocks
    markdown_content = pattern2.sub(replace_html_block, markdown_content)
    markdown_content = pattern3.sub(replace_html_block, markdown_content)
    
    # Pattern 3: Check if there are any lines starting with 4+ spaces not inside backtick blocks
    # This is a more complex pattern to ensure we don't double-format
    
    # Make sure all code blocks have empty lines around them for better rendering
    markdown_content = re.sub(r'([^\n])\n```', r'\1\n\n```', markdown_content)
    markdown_content = re.sub(r'```\n([^\n])', r'```\n\n\1', markdown_content)
    
    return markdown_content


def extract_url_parameters(url):
    """Extract folder_id and doc_guid from the Wiznote URL"""
    parsed_url = urlparse(url)
    
    # Extract folder_id from path
    path_parts = parsed_url.path.split('/')
    folder_id = None
    for part in path_parts:
        if re.match(r'^[a-f0-9-]{36}$', part):
            folder_id = part
            break
    
    # Extract doc_guid from query parameters
    query_params = parse_qs(parsed_url.query)
    doc_guid = None
    if 'docGuid' in query_params:
        doc_guid = query_params['docGuid'][0]
    
    print(f"Extracted folder_id: {folder_id}, doc_guid: {doc_guid}")
    return folder_id, doc_guid


def construct_image_url(folder_id, doc_guid, image_path):
    """Construct full image URL from relative path"""
    # Remove any leading "./" from the image path
    image_path = re.sub(r'^\./', '', image_path)
    
    # Construct the base URL for images
    base_url = f"https://kshttps0.wiz.cn/ks/note/view/{folder_id}/{doc_guid}/"
    
    # Combine with image path
    full_url = base_url + image_path
    
    print(f"Constructed image URL: {full_url}")
    return full_url


def download_image(image_url, save_dir, driver=None):
    """Download an image and save it to the specified directory"""
    try:
        # Create the index_files directory if it doesn't exist
        images_dir = os.path.join(save_dir, 'index_files')
        os.makedirs(images_dir, exist_ok=True)
        
        # Extract filename from URL
        image_filename = os.path.basename(image_url)
        
        # Full path to save the image
        save_path = os.path.join(images_dir, image_filename)
        
        print(f"Downloading image from {image_url}")
        
        # Try to download using the browser's session first (to handle authentication)
        if driver:
            try:
                # Store current URL to return to later
                current_url = driver.current_url
                
                # Navigate to the image URL
                driver.get(image_url)
                
                # Get the image content
                image_content = driver.find_element('tag name', 'img').screenshot_as_png
                
                # Save the image
                with open(save_path, 'wb') as f:
                    f.write(image_content)
                
                print(f"Image downloaded using browser to: {save_path}")
                
                # Return to the original page
                driver.get(current_url)
                
                return os.path.join('index_files', image_filename)
            except Exception as browser_error:
                print(f"Failed to download using browser: {str(browser_error)}, trying with requests")
                # Continue with requests method if browser method fails
        
        # Download using requests as fallback
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            
        print(f"Image downloaded with requests to: {save_path}")
        
        # Return the local path to use in markdown
        return os.path.join('index_files', image_filename)
        
    except Exception as e:
        print(f"Error downloading image {image_url}: {str(e)}")
        # Return the original URL as fallback
        return image_url


def process_markdown_images(markdown_content, folder_id, doc_guid, save_dir, driver=None):
    """Find all image references in markdown content and download them"""
    # Create images directory
    images_dir = os.path.join(save_dir, 'index_files')
    os.makedirs(images_dir, exist_ok=True)
    
    # Find all image references in the markdown
    image_pattern = r'!\[(.*?)\]\((.*?)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Skip external URLs that are already complete
        if image_path.startswith(('http://', 'https://')):
            return f"![{alt_text}]({image_path})"
        
        # Construct full URL
        full_url = construct_image_url(folder_id, doc_guid, image_path)
        
        # Introduce a delay to avoid being flagged as a bot
        time.sleep(2)
        # Download the image using the browser's session
        local_path = download_image(full_url, save_dir, driver=driver)
        
        # Return the markdown with the local path
        return f"![{alt_text}]({local_path})"
    
    # Replace all image references with local paths
    processed_content = re.sub(image_pattern, replace_image, markdown_content)
    
    return processed_content


def save_to_markdown(title, content, tags=None, folder_path=None, url=None, modified_date=None, driver=None):
    """Save title and content to a markdown file with YAML frontmatter"""
    if folder_path is None:
        # Default to the script directory if no folder specified
        folder_path = os.path.dirname(os.path.abspath(__file__))
    
    # Sanitize the title to create a valid filename
    sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    
    # Create filename
    filename = f"{sanitized_title}.md"
    file_path = os.path.join(folder_path, filename)
    
    # Start with frontmatter
    markdown_content = "---\n"
    
    # Add last modified date if available
    if modified_date:
        markdown_content += f'创建时间: "{modified_date}"\n'
    else:
        markdown_content += '创建时间:\n'
    
    # Add tags if available
    markdown_content += "tags:\n"
    if tags:
        for tag in tags:
            markdown_content += f"  - {tag}\n"
    
    # Close frontmatter
    markdown_content += "---\n\n"
    
    # Add title and content
    full_content = f"# {title}\n\n{content}"
    
    # Process images if URL is provided
    if url:
        folder_id, doc_guid = extract_url_parameters(url)
        if folder_id and doc_guid:
            full_content = process_markdown_images(full_content, folder_id, doc_guid, folder_path, driver=driver)
    
    # Add the processed content
    markdown_content += full_content
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Content saved to: {file_path}")
    return file_path


def init_driver():
    # 设置Chrome浏览器选项
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={user_data_dir}")  # 保存会话状态的目录
    # 设置Selenium WebDriver
    driver = webdriver.Chrome(options=options)  # 确保你已经安装了ChromeDriver
    return driver


def login_with_driver(url, driver=None):
    if driver is None:
        print("driver为空")
        return
    driver.get(url)
    input("请手动登录，登录完成后按Enter键继续...")


def main():
    driver = init_driver()
    login_with_driver('https://note.wiz.cn/web', driver)
    
    print("登录成功！请导航到您想要采集的页面")
    
    while True:
        command = input("请按回车键采集当前页面内容（输入'exit'退出程序）: ")
        if command.lower() == 'exit':
            break
            
        try:
            # Get current URL
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            
            # 提取内容
            title, html_content, tags, modified_date = extract_title_and_content(driver)
            print(f"已提取标题: {title}")
            
            # 转换为Markdown
            markdown_content = html_to_markdown(html_content)
            
            # 保存文件，包含下载图片
            save_to_markdown(title, markdown_content, tags, url=current_url, modified_date=modified_date, driver=driver)
            
        except Exception as e:
            print(f"采集内容时发生错误: {str(e)}")
    
    driver.quit()
    print("程序已退出")


if __name__ == "__main__":
    main()
else:
    driver = init_driver()
    login_with_driver('https://note.wiz.cn/web', driver)