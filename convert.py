#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将Markdown文件转换为HTML，同时提取代码块到外部文件
使用说明：
1. 将此脚本与需要转换的LeetCode笔记.md文件放在同一目录下
2. 确保template.html文件在同一目录
3. 运行脚本即可生成index.html
"""

import re
import markdown, html
from bs4 import BeautifulSoup

# 配置信息
INPUT_MD = "LeetCode笔记.md"  # 输入的Markdown文件
OUTPUT_HTML = "index.html"    # 输出的HTML文件
TEMPLATE_HTML = "template.html"  # 模板HTML文件

class CodeBlockExtractor:
    """代码块提取器"""
    
    def __init__(self):
        """初始化代码块提取器"""
        self.code_pairs = []  # 存储代码对：[(python_code, cpp_code), ...]
        self.current_pair = [None, None]  # [python_code, cpp_code]
        self.current_pair_index = 0
    
    def process_code_blocks(self, md_content):
        """
        提取Markdown中的代码块并保存到外部文件
        返回替换了代码块的Markdown内容和代码块信息
        """
        # 正则表达式匹配代码块: ```语言 代码 ```
        code_block_pattern = r'```(python|c\+\+)\n(.*?)```'
        
        # 查找所有代码块
        matches = list(re.finditer(code_block_pattern, md_content, re.DOTALL))
        
        # 语言映射函数 - 将c++映射为cpp
        def map_language(lang):
            return 'cpp' if lang == 'c++' else lang
        
        # 用于跟踪已处理的代码块
        processed_blocks = set()
        
        # 从前向后查找相邻的Python/C++代码块对
        i = 0
        while i < len(matches):
            match = matches[i]
            language = map_language(match.group(1))
            code = match.group(2).strip()
            if i not in processed_blocks:
                # 查找下一个代码块是否是配对的语言
                next_lang = None
                if i + 1 < len(matches):
                    next_match = matches[i + 1]
                    next_lang = map_language(next_match.group(1))
                
                if language == 'python' and next_lang == 'cpp':
                    # 找到Python+C++对
                    self.code_pairs.append([
                        code,  # Python代码
                        next_match.group(2).strip()  # C++代码
                    ])
                    # 标记这两个代码块为已处理
                    processed_blocks.add(i)
                    processed_blocks.add(i + 1)
                    i += 2
                else:
                    # 单独的代码块
                    if language == 'python':
                        self.code_pairs.append([code, ""])  # Python有代码，C++为空
                    else:  # cpp
                        self.code_pairs.append(["", code])  # Python为空，C++有代码
                    processed_blocks.add(i)
                    i += 1
            else:
                # 已经处理过的代码块
                i += 1
        
        # 替换Markdown中的代码块
        result_md = md_content
        placeholder_mapping = {}
        code_index = 0
        
        for i in range(len(matches)):
            if i in processed_blocks:
                match = matches[i]
                match_lang = map_language(match.group(1))
                
                # 如果是Python+C++对的第二个，跳过
                if i > 0 and i - 1 in processed_blocks and \
                map_language(matches[i-1].group(1)) == 'python' and match_lang == 'cpp':
                    continue
                    
                # 记录当前位置对应的代码对索引
                placeholder_mapping[i] = code_index
                code_index += 1
        
        # 从后向前替换，以避免位置变化
        for i in reversed(range(len(matches))):
            if i in processed_blocks:
                match = matches[i]
                start, end = match.span()
                match_lang = map_language(match.group(1))
                
                # 如果是Python+C++对的第二个 (C++)，删除
                if i > 0 and i - 1 in processed_blocks and \
                map_language(matches[i-1].group(1)) == 'python' and match_lang == 'cpp':
                    result_md = result_md[:start] + "" + result_md[end:]
                else:
                    # 使用映射表获取正确的索引
                    pair_index = placeholder_mapping[i]
                    placeholder = f"<code-placeholder index='{pair_index}'></code-placeholder>"
                    result_md = result_md[:start] + placeholder + result_md[end:]
        
        return result_md
    
    def get_code_container(self, index):
        """生成代码容器HTML"""
        if index >= len(self.code_pairs):
            return ""
        
        python_code, cpp_code = self.code_pairs[index]
        
        # 如果代码为空，添加默认内容
        if not python_code.strip():
            python_code = "# 此部分代码待实现"
        if not cpp_code.strip():
            cpp_code = "// 此部分代码待实现"
        
        # 对代码进行HTML转义，特别是处理<, >, &等特殊字符
        python_code = html.escape(python_code)
        cpp_code = html.escape(cpp_code)
            
        # 生成代码容器HTML
        return f"""
<div class="code-container">
    <div class="code-tabs">
        <button class="tab-btn active" data-lang="python">Python</button>
        <button class="tab-btn" data-lang="cpp">C++</button>
    </div>
    
    <div class="code-blocks">
        <pre class="code-block active" data-lang="python"><code class="language-python">{python_code}</code></pre>
        <pre class="code-block" data-lang="cpp"><code class="language-cpp">{cpp_code}</code></pre>
    </div>
</div>
"""

def convert_markdown_to_html(md_content):
    """转换Markdown为HTML"""
    # 处理代码块
    code_extractor = CodeBlockExtractor()
    processed_md = code_extractor.process_code_blocks(md_content)
    
    # 使用markdown库转换为HTML
    html_content = markdown.markdown(
        processed_md,
        extensions=[
            'markdown.extensions.tables',     # 表格支持
            'markdown.extensions.fenced_code', # 代码块支持
            'markdown.extensions.nl2br',       # 换行支持
            'markdown.extensions.toc'          # 目录支持
        ]
    )
    
    # 替换代码块占位符为实际代码容器
    placeholder_pattern = r"<code-placeholder index='(\d+)'></code-placeholder>"
    
    def replace_placeholder(match):
        index = int(match.group(1))
        return code_extractor.get_code_container(index)
    
    # 替换占位符
    html_content = re.sub(placeholder_pattern, replace_placeholder, html_content)
    # 处理行内LaTeX公式
    html_content = re.sub(r'&lt;span class="math inline"&gt;\\(.*?)\\&lt;\/span&gt;', r'$\1$', html_content)
    html_content = re.sub(r'&lt;span class="math display"&gt;\\(.*?)\\&lt;\/span&gt;', r'$$\1$$', html_content)
    
    return html_content

def process_html_content(html_content):
    """处理HTML内容，添加section标签和ID等"""
    # 在这里，我们直接处理html_content字符串，而不是使用BeautifulSoup解析整个HTML
    soup = BeautifulSoup(f"<div>{html_content}</div>", 'html.parser')
    root_div = soup.div
    
    # 处理标题，为其添加ID和section包装
    current_section = None
    current_section_level = 0
    content_elements = list(root_div.children)
    
    # 创建新的结构化内容
    new_content = BeautifulSoup('<div></div>', 'html.parser')
    new_root = new_content.div
    
    for element in content_elements:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            
            # 为标题添加ID（如果没有）
            if not element.get('id'):
                element_id = re.sub(r'\s+', '-', element.text.lower())
                element_id = re.sub(r'[^\w\-]', '', element_id)
                element['id'] = element_id
            
            # 如果是更高级别的标题，创建新的section
            if level <= current_section_level or current_section is None:
                current_section = soup.new_tag('section')
                current_section['id'] = element['id']
                new_root.append(current_section)
                current_section_level = level
            
            current_section.append(element)
        elif current_section is not None:
            # 非标题元素，添加到当前section
            current_section.append(element)
        else:
            # 在任何section之前的内容
            new_root.append(element)
    
    # 处理图片标签，确保保留样式
    for img in new_content.find_all('img'):
        # 确保src正确
        src = img.get('src', '')
        if src.startswith('.'):
            # 相对路径保持不变
            pass
        
        # 处理样式和缩放
        style = img.get('style', '')
        if 'zoom' in style and not style.startswith('style='):
            img['style'] = style
    
    # 返回处理后的HTML
    return str(new_root.decode_contents())

def generate_toc(html_content):
    """生成目录HTML"""
    # 使用分割线包装HTML内容，以便BeautifulSoup可以正确解析
    soup = BeautifulSoup(f"<div>{html_content}</div>", 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    toc_html = '<ul id="toc">\n'
    current_levels = [0, 0, 0, 0, 0, 0]  # h1-h6的当前级别
    last_level = 0
    open_lists = 0  # 跟踪打开的列表数量
    
    for heading in headings:
        level = int(heading.name[1])  # h1 -> 1, h2 -> 2, 等
        
        # 获取标题ID
        heading_id = heading.get('id', '')
        if not heading_id:
            heading_id = re.sub(r'\s+', '-', heading.text.lower())
            heading_id = re.sub(r'[^\w\-]', '', heading_id)
        
        # 设置当前级别，重置更低级别
        current_levels[level-1] += 1
        for i in range(level, 6):
            current_levels[i] = 0
        
        # 处理级别变化
        if level > last_level:
            # 级别增加，打开新的ul
            for i in range(level - last_level):
                toc_html += "    " * (last_level + i) + "<ul>\n"
                open_lists += 1
        elif level < last_level:
            # 级别减少，关闭当前ul
            for i in range(last_level - level):
                toc_html += "    " * (last_level - i - 1) + "</ul>\n"
                open_lists -= 1
        
        # 添加目录项
        indent = "    " * level
        toc_html += f'{indent}<li><a href="#{heading_id}">{heading.text}</a></li>\n'
        
        last_level = level
    
    # 关闭所有未关闭的ul标签
    for i in range(open_lists):
        toc_html += "    " * (open_lists - i - 1) + "</ul>\n"
    
    toc_html += "</ul>\n</div>"
    return toc_html

def create_html_from_template(template_path, content_html, toc_html):
    """使用模板生成最终HTML"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替换目录和内容
        template = template.replace('<ul id="toc">\n            <!-- 目录将由JavaScript生成 -->\n        </ul>', toc_html)
        template = template.replace('<main id="content">\n        <!-- 内容将在这里插入 -->\n    </main>', f'<main id="content">\n        {content_html}\n    </main>')
        
        return template
    except Exception as e:
        print(f"模板处理错误: {e}")
        # 返回基本HTML作为备选
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeetCode笔记</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;700&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2>目录</h2>
        </div>
        {toc_html}
    </nav>
    
    <main id="content">
        {content_html}
    </main>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/languages/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/languages/cpp.min.js"></script>
    <script src="script.js"></script>
</body>
</html>
"""

def main():
    """主函数"""
    print(f"开始转换 {INPUT_MD} 为 {OUTPUT_HTML}...")
    
    # 读取Markdown文件
    try:
        with open(INPUT_MD, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {INPUT_MD}")
        return
    
    # 转换Markdown为HTML
    html_content = convert_markdown_to_html(md_content)
    
    # 处理HTML内容（添加section等）
    processed_html = process_html_content(html_content)
    
    # 生成目录
    toc_html = generate_toc(html_content)
    
    # 使用模板生成最终HTML
    final_html = create_html_from_template(TEMPLATE_HTML, processed_html, toc_html)
    
    # 写入HTML文件
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"转换完成! HTML文件已保存为 {OUTPUT_HTML}")

if __name__ == "__main__":
    main()