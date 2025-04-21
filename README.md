# Wiznote Data Extractor

[English](README.md) | [中文](README_CN.md)

A tool for extracting and saving notes from Wiznote (note.wiz.cn) as Markdown files with proper formatting.

## Features

<video width="1280" height="720" controls>
  <source src="WiznoteExtractor.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

- Extracts note title, content, tags, and last modified date
- Converts HTML content to Markdown format
- Downloads and saves embedded images locally
- Properly formats code blocks
- Preserves metadata in YAML frontmatter

## Requirements

- Python 3.6+
- Chrome browser
- ChromeDriver
- Required Python packages (see Installation)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/WiznoteExtractor.git
   cd WiznoteExtractor
   ```

2. Install required Python packages:
   ```
   pip install selenium beautifulsoup4 html2text requests
   ```

3. Install ChromeDriver:
   - Download the ChromeDriver version that matches your Chrome browser from [ChromeDriver official site](https://sites.google.com/chromium.org/driver/)
   - For Windows:
     - Extract the downloaded zip file
     - Add the ChromeDriver location to your PATH environment variable, or
     - Place chromedriver.exe in a directory that's already in your PATH

   - For macOS:
     ```
     brew install chromedriver
     ```
   
   - For Linux:
     ```
     sudo apt install chromium-chromedriver
     ```
     or download the Linux version from the official site and add it to your PATH

4. Configure the user data directory:
   - Open `WiznoteDataExtractor.py` and modify the `user_data_dir` path in the `init_driver()` function to a location on your system

## Usage

1. Run the script:
   ```
   python WiznoteDataExtractor.py
   ```

2. A Chrome browser window will open. You need to manually log in to your Wiznote account when prompted.

3. After logging in, navigate to the note you want to collect.

4. Press Enter in the terminal to collect the current page.

5. The script will extract the note content, convert it to Markdown, download any embedded images, and save everything to a Markdown file in the same directory as the script.

6. Continue navigating to other notes and press Enter to collect them, or type 'exit' to quit the program.

## Notes

- The script creates a user profile for Chrome to maintain login sessions.
- Images are saved in an `index_files` folder adjacent to the Markdown files.
- If image download fails using the browser method, it will fall back to using the requests library.

## License

[Add your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
