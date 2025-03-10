document.addEventListener('DOMContentLoaded', function() {
    // 初始化语法高亮
    hljs.highlightAll();
    
    // 侧边栏宽度调整功能
    setupSidebarResize();

    // 为所有代码标签按钮添加事件监听器
    setupCodeTabs();
});

// 添加侧边栏宽度调整功能
function setupSidebarResize() {
    const sidebar = document.querySelector('.sidebar');
    let startX, startWidth;

    // 创建调整器元素
    const resizer = document.createElement('div');
    resizer.className = 'sidebar-resizer';
    sidebar.appendChild(resizer);

    // 鼠标按下事件
    resizer.addEventListener('mousedown', function(e) {
        startX = e.clientX;
        startWidth = parseInt(document.defaultView.getComputedStyle(sidebar).width, 10);
        document.documentElement.addEventListener('mousemove', doDrag, false);
        document.documentElement.addEventListener('mouseup', stopDrag, false);
    });

    // 拖动处理
    function doDrag(e) {
        const newWidth = startWidth + e.clientX - startX;
        const minWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-min-width'), 10);
        const maxWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-max-width'), 10);
        
        if (newWidth >= minWidth && newWidth <= maxWidth) {
            sidebar.style.width = newWidth + 'px';
            document.documentElement.style.setProperty('--sidebar-width', newWidth + 'px');
            document.querySelector('main').style.marginLeft = newWidth + 'px';
            document.querySelector('main').style.width = `calc(100% - ${newWidth}px)`;
        }
    }

    // 停止拖动
    function stopDrag() {
        document.documentElement.removeEventListener('mousemove', doDrag, false);
        document.documentElement.removeEventListener('mouseup', stopDrag, false);
    }
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

// 处理空代码块
function handleEmptyCodeBlocks() {
    // 查找所有代码占位符
    const codePlaceholders = document.querySelectorAll('code-placeholder');
    
    codePlaceholders.forEach(placeholder => {
        const lang = placeholder.getAttribute('lang');
        const index = placeholder.getAttribute('index');
        const content = placeholder.textContent;
        
        // 查找最近的代码容器
        const container = placeholder.closest('p').previousElementSibling;
        if (container && container.classList.contains('code-container')) {
            // 查找对应语言的代码块
            const codeBlock = container.querySelector(`.code-block[data-lang="${lang}"]`);
            if (codeBlock) {
                // 如果代码块为空，填充内容
                if (!codeBlock.textContent.trim()) {
                    const codeElement = codeBlock.querySelector('code');
                    if (codeElement) {
                        codeElement.textContent = content || '// 此部分代码待实现';
                        hljs.highlightElement(codeElement);
                    }
                }
            }
        }
    });
    
    // 移除所有占位符
    codePlaceholders.forEach(placeholder => {
        placeholder.remove();
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