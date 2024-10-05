const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const personaSelect = document.getElementById('persona');
const modelSelect = document.getElementById('model');
const newChatBtn = document.getElementById('newChatBtn');
const homeTab = document.getElementById('homeTab');
const historyTab = document.getElementById('historyTab');
const historyList = document.getElementById('historyList');
const attachButton = document.getElementById('attachButton');
const loading = document.getElementById('loading');

let currentChatId = null;
let chatHistory = [];
let isLoadingHistory = false;
let isHistoryExpanded = false;

// 获取 Persona 数据
async function fetchPersonas() {
    try {
        const response = await fetch('/api/roles');
        const personas = await response.json();
        // console.log('Fetched personas:', personas);
        personaSelect.innerHTML = ''; // 清空现有选项
        if (Array.isArray(personas)) {
            personas.forEach(persona => {
                const option = document.createElement('option');
                option.value = persona.value || persona.id || persona;
                option.textContent = persona.name || persona.label || persona;
                personaSelect.appendChild(option);
            });
        } else {
            console.error('Personas data is not an array:', personas);
        }
        if (personaSelect.options.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'No personas available';
            personaSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error fetching personas:', error);
        const option = document.createElement('option');
        option.textContent = 'Error loading personas';
        personaSelect.appendChild(option);
    }
}

// 获取 Model 数据
async function fetchModels() {
    try {
        const response = await fetch('/api/models');
        const models = await response.json();
        console.log('Fetched models:', models);
        modelSelect.innerHTML = ''; // 清空现有选项
        if (Array.isArray(models)) {
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.value || model.id || model;
                option.textContent = model.name || model.label || model;
                modelSelect.appendChild(option);
            });
        } else {
            console.error('Models data is not an array:', models);
        }
        if (modelSelect.options.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'No models available';
            modelSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error fetching models:', error);
        const option = document.createElement('option');
        option.textContent = 'Error loading models';
        modelSelect.appendChild(option);
    }
}

 // 添加消息到聊天区域
function addMessage(sender, content, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerHTML = `
        <div class="message-header">${sender}</div>
        <div class="message-content">${marked.parse(content)}</div>
    `;
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;

    // 为代码块添加复制按钮
    messageDiv.querySelectorAll('pre').forEach((preBlock) => {
        const codeBlock = preBlock.querySelector('code');
        if (codeBlock) {
            const language = codeBlock.className.replace('language-', '');
            hljs.highlightElement(codeBlock);

            const wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';
            preBlock.parentNode.insertBefore(wrapper, preBlock);
            wrapper.appendChild(preBlock);
            
            // 添加语言标签
            const languageTag = document.createElement('span');
            languageTag.className = 'language-tag';
            languageTag.textContent = language;
            wrapper.appendChild(languageTag);

            // 添加复制按钮
            const copyButton = document.createElement('button');
            copyButton.textContent = 'Copy';
            copyButton.className = 'copy-button';
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                    copyButton.textContent = 'Copied!';
                    setTimeout(() => {
                        copyButton.textContent = 'Copy';
                    }, 2000);
                });
            });
            wrapper.appendChild(copyButton);
        }
    });
}

// 发送消息到 AI 并接收响应
async function sendMessage() {
    loading.style.display = 'block';
    const message = userInput.value.trim();
    if (message) {
        addMessage('YOU', message, 'you');
        userInput.value = '';
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    role: personaSelect.value,
                    model: modelSelect.value,
                    chatId: currentChatId,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiResponse = '';
            let lastContent = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim();
                        if (data === '[DONE]') {
                            updateAIMessage(aiResponse);
                            return;
                        }
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.choices && parsed.choices[0].delta && parsed.choices[0].delta.content) {
                                const newContent = parsed.choices[0].delta.content;
                                // 检查新内容是否与上一次的内容重复
                                if (newContent !== lastContent) {
                                    aiResponse += newContent;
                                    updateAIMessage(aiResponse);
                                    lastContent = newContent;
                                }
                            }
                        } catch (error) {
                            console.error('Error parsing JSON:', error);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Thor AI', `Error: ${error.message}`, 'Thor AI');
        } finally {
            loading.style.display = 'none';
            saveChatToHistory();
            if (isHistoryExpanded) {
                updateHistoryList();
            }
        }
    }
}

// 更新 AI 消息
function updateAIMessage(content) {
    let aiMessage = chatArea.querySelector('.message.thor:last-child');
    if (!aiMessage) {
        aiMessage = document.createElement('div');
        aiMessage.className = 'message thor';
        aiMessage.innerHTML = '<div class="message-header">Thor AI</div><div class="message-content"></div>';
        chatArea.appendChild(aiMessage);
    }
    
    // 使用 DOMParser 来解析新内容
    const parser = new DOMParser();
    const doc = parser.parseFromString(marked.parse(content), 'text/html');
    
    // 处理代码块
    doc.querySelectorAll('pre code').forEach((block) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';
        block.parentNode.parentNode.insertBefore(wrapper, block.parentNode);
        wrapper.appendChild(block.parentNode);
        
        if (!wrapper.querySelector('.copy-btn')) {
            const button = document.createElement('button');
            button.textContent = 'Copy';
            button.className = 'copy-btn';
            button.addEventListener('click', () => {
                navigator.clipboard.writeText(block.textContent).then(() => {
                    button.textContent = 'Copied!';
                    setTimeout(() => {
                        button.textContent = 'Copy';
                    }, 2000);
                });
            });
            wrapper.insertBefore(button, wrapper.firstChild);
        }
        
        hljs.highlightElement(block);
    });
    
    // 更新消息内容
    aiMessage.querySelector('.message-content').innerHTML = doc.body.innerHTML;
    
    // 平滑滚动到底部
    chatArea.scrollTo({
        top: chatArea.scrollHeight,
        behavior: 'smooth'
    });
}

// 开始新对话
function startNewChat() {
    if (currentChatId !== null) {
        saveChatToHistory();
    }
    
    clearChat();
    currentChatId = Date.now();
    
    // Reset selections to default values
    personaSelect.value = personaSelect.options[0].value;
    modelSelect.value = modelSelect.options[0].value;
    
    updateHistoryList();
}

// 清空聊天区域
function clearChat() {
    chatArea.innerHTML = '';
    currentChatId = null;
}

// 保存聊天到历史记录
function saveChatToHistory() {
    if (chatArea.innerHTML.trim() !== '' && !isLoadingHistory) {
        const messages = chatArea.querySelectorAll('.message');
        const firstMessage = messages[0]?.querySelector('.message-content')?.textContent || 'New Chat';
        const chatSummary = firstMessage.slice(0, 50) + (firstMessage.length > 50 ? '...' : '');
        
        const chatData = {
            id: currentChatId,
            summary: chatSummary,
            content: chatArea.innerHTML,
            role: personaSelect.value,
            model: modelSelect.value
        };
        
        const existingChatIndex = chatHistory.findIndex(chat => chat.id === currentChatId);
        if (existingChatIndex !== -1) {
            // Update existing chat
            chatHistory[existingChatIndex] = chatData;
        } else {
            // Add new chat
            chatHistory.unshift(chatData);
        }
        
        updateHistoryList();
    }
}

// 更新历史记录列表
function updateHistoryList(selectedChatId = null) {
    historyList.innerHTML = '';
    chatHistory.forEach(chat => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        if (chat.id === selectedChatId) {
            historyItem.classList.add('selected');
        }
        historyItem.innerHTML = `
            <span class="history-summary">${chat.summary}</span>
        `;
        historyItem.addEventListener('click', () => loadChat(chat.id));
        historyList.appendChild(historyItem);
    });
    
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

// 加载聊天
function loadChat(chatId) {
    const chat = chatHistory.find(c => c.id === chatId);
    if (chat) {
        isLoadingHistory = true;
        chatArea.innerHTML = chat.content;
        currentChatId = chatId;
        
        // Restore role and model selections
        personaSelect.value = chat.role;
        modelSelect.value = chat.model;
       
        
        isLoadingHistory = false;
        
        // Keep History tab active and show chat area
        historyTab.classList.add('active');
        homeTab.classList.remove('active');
        historyList.classList.add('expanded');
        isHistoryExpanded = true;
        chatArea.style.display = 'block';
        
        // Highlight the selected chat in history list
        updateHistoryList(chatId);
    }
}

// 切换历史记录
function toggleHistory() {
    isHistoryExpanded = !isHistoryExpanded;
    if (isHistoryExpanded) {
        historyList.classList.add('expanded');
        if (currentChatId !== null) {
            saveChatToHistory();
        }
        updateHistoryList(currentChatId);
    } else {
        historyList.classList.remove('expanded');
    }
}

// 初始化函数
async function initialize() {
    await Promise.all([fetchPersonas(), fetchModels()]);
    hljs.highlightAll();
    console.log('Initialization complete');
    
    // 从 localStorage 加载历史记录
    const savedHistory = localStorage.getItem('chatHistory');
    if (savedHistory) {
        chatHistory = JSON.parse(savedHistory);
        updateHistoryList();
    }
    
    // 总是清空对话框并开始新对话
    clearChat();
    startNewChat();
}

// 事件监听器
sendButton.addEventListener('click', sendMessage);
newChatBtn.addEventListener('click', startNewChat);
attachButton.addEventListener('click', handleAttachment);

// 主页标签点击事件
homeTab.addEventListener('click', () => {
    homeTab.classList.add('active');
    historyTab.classList.remove('active');
    historyList.classList.remove('expanded');
    isHistoryExpanded = false;
    chatArea.style.display = 'block';
    
    // 总是清空对话框并开始新对话
    clearChat();
    startNewChat();
});

// 历史记录标签点击事件
historyTab.addEventListener('click', () => {
    historyTab.classList.add('active');
    homeTab.classList.remove('active');  // 移除 Home 标签的激活状态
    toggleHistory();
});

// 用户输入事件 
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 页面加载完成后立即初始化
document.addEventListener('DOMContentLoaded', initialize);

// 处理附件的逻辑
function handleAttachment() {
    // 处理附件的逻辑
    console.log('Attachment button clicked');
}