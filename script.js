document.addEventListener('DOMContentLoaded', function() {
    // 初始化语法高亮
    hljs.highlightAll();
    
    // 生成目录
    generateTableOfContents();
    
    // 为所有代码标签按钮添加事件监听器
    setupCodeTabs();
});

// 生成目录
function generateTableOfContents() {
    const toc = document.getElementById('toc');
    const sections = document.querySelectorAll('main section');
    
    sections.forEach(section => {
        const heading = section.querySelector('h2, h3, h4');
        if (heading) {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.href = `#${section.id}`;
            link.textContent = heading.textContent;
            
            // 根据标题级别添加缩进
            if (heading.tagName === 'H3') {
                item.style.marginLeft = '15px';
            } else if (heading.tagName === 'H4') {
                item.style.marginLeft = '30px';
            }
            
            item.appendChild(link);
            toc.appendChild(item);
        }
    });
}

// 设置代码标签切换
function setupCodeTabs() {
    const codeContainers = document.querySelectorAll('.code-container');
    
    codeContainers.forEach(container => {
        const tabButtons = container.querySelectorAll('.tab-btn');
        const codeBlocks = container.querySelectorAll('.code-block');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // 移除所有活动类
                tabButtons.forEach(btn => btn.classList.remove('active'));
                codeBlocks.forEach(block => block.classList.remove('active'));
                
                // 获取选中的语言
                const lang = button.getAttribute('data-lang');
                
                // 为当前按钮和相应代码块添加活动类
                button.classList.add('active');
                container.querySelector(`.code-block[data-lang="${lang}"]`).classList.add('active');
            });
        });
    });
}

// 平滑滚动到锚点
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 20,
                behavior: 'smooth'
            });
        }
    });
});

// 添加亮点标记功能
document.addEventListener('mouseup', function() {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
        const range = selection.getRangeAt(0);
        const selectedText = selection.toString();
        
        // 在控制台显示选中的文本（实际应用中可以添加复制或高亮功能）
        console.log('Selected text:', selectedText);
    }
});