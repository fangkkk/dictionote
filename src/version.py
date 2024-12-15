VERSION = '1.0.0'
BUILD_NUMBER = '1'
RELEASE_DATE = '2024-03-20'

def get_version_string():
    return f"{VERSION}.{BUILD_NUMBER}"

def get_about_text():
    return f"""DictiNote v{VERSION}
    
构建版本：{BUILD_NUMBER}
发布日期：{RELEASE_DATE}

作者：Your Name
主页：https://github.com/yourusername/dictionote

Copyright © 2024 Your Name
""" 