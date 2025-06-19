document.addEventListener('DOMContentLoaded', () => {
    console.log("Script loaded correctly!");
    
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const clearButton = document.getElementById('clear-button');
    
    // Get the tool name from URL path
    const pathParts = window.location.pathname.split('/');
    const toolName = pathParts[pathParts.length - 2] || 'django'; 
    console.log("Using tool name:", toolName);
    
    // Chat history management
    let chatHistory = [];

    // Save messages to chat history
    function saveToHistory(sender, content) {
        chatHistory.push({
            sender: sender,
            content: content,
            timestamp: new Date().toISOString()
        });
        
        // Store in localStorage for persistence
        localStorage.setItem(`docMedia_${toolName}_chatHistory`, JSON.stringify(chatHistory));
    }

    // Modify the appendMessage function to save history
    const originalAppendMessage = appendMessage;
    appendMessage = function(sender, content) {
        // Call the original function
        originalAppendMessage(sender, content);
        
        // Save to history
        saveToHistory(sender, content);
    };

    // Share chat functionality
    const shareChatBtn = document.getElementById('share-chat-btn');
    if (shareChatBtn) {
        shareChatBtn.addEventListener('click', async () => {
            try {
                // Get the CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Prepare data for server
                const chatData = {
                    tool_name: toolName,
                    messages: chatHistory,
                    created_at: new Date().toISOString()
                };
                
                // Show loading state
                shareChatBtn.disabled = true;
                shareChatBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Generating Link...</span>';
                
                try {
                    // Save chat to server
                    const response = await fetch('/api/shared-chats/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(chatData)
                    });
                    
                    if (!response.ok) {
                        throw new Error('Server error');
                    }
                    
                    const data = await response.json();
                    const shareableUrl = `${window.location.origin}/ai-chat/${toolName}/?share=${data.chat_id}`;
                    
                    // Copy to clipboard
                    await navigator.clipboard.writeText(shareableUrl);
                    
                    // Show success notification
                    const notification = document.createElement('div');
                    notification.className = 'fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded shadow-lg z-50';
                    notification.textContent = 'Chat link copied to clipboard!';
                    document.body.appendChild(notification);
                    
                    // Remove after 2 seconds
                    setTimeout(() => {
                        notification.remove();
                    }, 2000);
                    
                } catch (error) {
                    console.error('Error sharing chat:', error);
                    
                    // Fallback to local sharing if server fails
                    const chatId = Date.now().toString(36) + Math.random().toString(36).substr(2);
                    localStorage.setItem(`docMedia_shared_${chatId}`, JSON.stringify(chatData));
                    
                    const shareableUrl = `${window.location.origin}/ai-chat/${toolName}/?share_local=${chatId}`;
                    await navigator.clipboard.writeText(shareableUrl);
                    
                    // Show notification
                    const notification = document.createElement('div');
                    notification.className = 'fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded shadow-lg z-50';
                    notification.textContent = 'Local chat link copied to clipboard!';
                    document.body.appendChild(notification);
                    
                    // Remove after 2 seconds
                    setTimeout(() => {
                        notification.remove();
                    }, 2000);
                } finally {
                    // Reset button
                    shareChatBtn.disabled = false;
                    shareChatBtn.innerHTML = '<i class="fas fa-share-alt mr-2"></i><span>Share Chat</span>';
                }
            } catch (err) {
                console.error('Error in chat sharing:', err);
                alert('Failed to share chat. Please try again.');
            }
        });
    }

    // Open in ChatGPT functionality
    const openChatGPTBtn = document.getElementById('open-chatgpt-btn');
    if (openChatGPTBtn) {
        openChatGPTBtn.addEventListener('click', () => {
            // Format chat history for ChatGPT
            let chatGptPrompt = `Previous conversation about ${toolName} documentation:\n\n`;
            
            chatHistory.forEach(msg => {
                const role = msg.sender === 'user' ? 'User' : 'Assistant';
                chatGptPrompt += `${role}: ${msg.content}\n\n`;
            });
            
            // Add instruction for continuation
            chatGptPrompt += "Please continue helping with this conversation based on the above context.";
            
            // Encode the prompt for URL
            const encodedPrompt = encodeURIComponent(chatGptPrompt);
            
            // Open ChatGPT with this prompt
            window.open(`https://chat.openai.com/?prompt=${encodedPrompt}`, '_blank');
        });
    }

    // Open in Google AI Studio functionality
    const openAIStudioBtn = document.getElementById('open-ai-studio-btn');
    if (openAIStudioBtn) {
        openAIStudioBtn.addEventListener('click', () => {
            // Format chat history for Google AI Studio
            let aiStudioPrompt = `# ${toolName.toUpperCase()} Documentation Assistant\n\nPrevious conversation:\n\n`;
            
            chatHistory.forEach(msg => {
                const role = msg.sender === 'user' ? 'USER' : 'ASSISTANT';
                aiStudioPrompt += `${role}: ${msg.content}\n\n`;
            });
            
            // Add instruction for continuation
            aiStudioPrompt += "USER: Please continue helping with my questions about " + toolName;
            
            // Encode the prompt for URL
            const encodedPrompt = encodeURIComponent(aiStudioPrompt);
            
            // Open Google AI Studio with this prompt
            window.open(`https://makersuite.google.com/app/prompts/new?text=${encodedPrompt}`, '_blank');
        });
    }

    // Check for shared chat in URL parameters
    function loadSharedChat() {
        const urlParams = new URLSearchParams(window.location.search);
        const serverChatId = urlParams.get('share');
        const localChatId = urlParams.get('share_local');
        
        if (serverChatId) {
            // Try to load from server API
            fetch(`/api/shared-chats/${serverChatId}/`)
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Chat not found on server');
                    }
                })
                .then(data => {
                    if (data && data.messages && data.messages.length > 0) {
                        restoreChat(data.messages);
                        showSharedChatBanner(data.created_at);
                    }
                })
                .catch(error => {
                    console.error('Error loading shared chat:', error);
                });
        } else if (localChatId) {
            // Try loading from localStorage
            const savedChat = localStorage.getItem(`docMedia_shared_${localChatId}`);
            if (savedChat) {
                try {
                    const parsedChat = JSON.parse(savedChat);
                    if (parsedChat && parsedChat.messages && parsedChat.messages.length > 0) {
                        restoreChat(parsedChat.messages);
                        showSharedChatBanner(parsedChat.created_at);
                    }
                } catch (e) {
                    console.error('Error parsing shared chat:', e);
                }
            }
        } else {
            // Try to load previous session
            const savedHistory = localStorage.getItem(`docMedia_${toolName}_chatHistory`);
            if (savedHistory) {
                try {
                    const parsedHistory = JSON.parse(savedHistory);
                    if (parsedHistory && parsedHistory.length > 0) {
                        // Only restore if there's real content (ignore empty arrays)
                        restoreChat(parsedHistory);
                    }
                } catch (e) {
                    console.error('Error parsing chat history:', e);
                }
            }
        }
    }

    // Restore chat from history
    function restoreChat(messages) {
        if (!messages || !Array.isArray(messages) || messages.length === 0) return;
        
        // Clear existing messages
        chatMessages.innerHTML = '';
        
        // Restore each message
        messages.forEach(msg => {
            // Use the original function to avoid recursively adding to history
            originalAppendMessage(msg.sender, msg.content);
        });
        
        // Set current chat history
        chatHistory = messages;
    }

    // Show banner for shared chat
    function showSharedChatBanner(timestamp) {
        const banner = document.createElement('div');
        banner.className = 'bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-3 mb-4';
        banner.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <p class="font-medium">You're viewing a shared conversation</p>
                    <p class="text-sm">${new Date(timestamp).toLocaleString()}</p>
                </div>
                <button class="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700" id="new-chat-btn">
                    Start New Chat
                </button>
            </div>
        `;
        
        chatMessages.prepend(banner);
        
        // Add event listener to new chat button
        document.getElementById('new-chat-btn').addEventListener('click', () => {
            // Clear URL parameters but keep the correct path
            window.history.replaceState({}, document.title, `/ai-chat/${toolName}/`);
            
            // Clear messages
            chatMessages.innerHTML = '';
            
            // Reset chat history
            chatHistory = [];
            
            // Add welcome message back
            appendDefaultWelcomeMessage();
        });
    }

    // Add the default welcome message
    function appendDefaultWelcomeMessage() {
        const welcomeMsg = `
        <div class="flex items-start">
            <div class="bg-blue-50 border border-blue-100 rounded-2xl py-3 px-4 message-bubble ai-message">
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center">
                        <div class="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center mr-2">
                            <i class="fas fa-robot text-blue-600"></i>
                        </div>
                        <span class="font-medium text-blue-800">AI Assistant</span>
                    </div>
                </div>
                <div class="prose prose-blue max-w-none">
                    <p>👋 Welcome to the ${toolName.charAt(0).toUpperCase() + toolName.slice(1)} Documentation Assistant!</p>
                    <p>Ask me anything about ${toolName.charAt(0).toUpperCase() + toolName.slice(1)} and I'll help you find answers from the official documentation.</p>
                </div>
            </div>
        </div>
        `;
        
        chatMessages.innerHTML = welcomeMsg;
    }

    // Load shared chat on page load
    loadSharedChat();

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const userQuestion = userInput.value.trim();
        if (!userQuestion) return;
        
        // Add user message to chat
        appendMessage('user', userQuestion);
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        const typingIndicatorId = showTypingIndicator();
        
        try {
            // Get the CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Send request to the backend
            const response = await fetch('/chat-api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    question: userQuestion,
                    tool_name: toolName
                })
            });
            
            // Remove typing indicator
            removeTypingIndicator(typingIndicatorId);
            
            if (response.ok) {
                const data = await response.json();
                appendMessage('ai', data.answer);
            } else {
                appendMessage('ai', 'Sorry, I encountered an error while processing your request.');
            }
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator(typingIndicatorId);
            appendMessage('ai', 'Sorry, there was an error connecting to the server.');
        }
    });
    
    // Helper function to add a message to the chat
    function appendMessage(sender, content) {
        const messageId = `msg-${Date.now()}`;
        const isUser = sender === 'user';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start mb-4';
        
        if (isUser) {
            messageDiv.className += ' justify-end';
        }
        
        const messageBubble = document.createElement('div');
        messageBubble.className = isUser 
            ? 'bg-blue-600 text-white rounded-2xl py-3 px-4 message-bubble user-message max-w-3xl' 
            : 'bg-blue-50 border border-blue-100 rounded-2xl py-3 px-4 message-bubble ai-message max-w-3xl';
        messageBubble.style.whiteSpace = 'pre-wrap';
        
        if (isUser) {
            messageBubble.textContent = content;
        } else {
            // Process markdown for AI responses
            messageBubble.innerHTML = formatMarkdown(content);
            
            // Add syntax highlighting to code blocks
            setTimeout(() => {
                const codeBlocks = messageBubble.querySelectorAll('pre code');
                codeBlocks.forEach(block => {
                    addCopyButton(block);
                    highlightCode(block);
                });
            }, 0);
        }
        
        messageDiv.appendChild(messageBubble);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Format citations in the responses
    function formatCitations(text) {
        // Check if we have citations section
        if (text.includes('Cited documentation sections:')) {
            const parts = text.split('Cited documentation sections:');
            const mainContent = parts[0].trim();
            let citations = parts[1];
            
            // Format citation entries
            const citationItems = [];
            const regex = /\s*Section:\s*(.*?)(?:¶|\n|$)/g;
            let match;
            
            while ((match = regex.exec(citations)) !== null) {
                const sectionName = match[1].trim();
                if (sectionName) {
                    const toolSpecificUrl = toolName === 'flask' 
                        ? `https://flask.palletsprojects.com/en/latest/search/?q=${encodeURIComponent(sectionName)}`
                        : `https://docs.python.org/3/search.html?q=${encodeURIComponent(sectionName)}`;
                    
                    citationItems.push(`<li><a href="${toolSpecificUrl}" target="_blank" class="text-blue-600 hover:underline">${sectionName}</a></li>`);
                }
            }
            
            // Build citation HTML without extra spaces
            if (citationItems.length > 0) {
                const citationHtml = `<div class="citation-list">
                    <h3>References</h3>
                    <ul class="list-disc">${citationItems.join('')}</ul>
                </div>`;
                
                return mainContent + citationHtml;
            }
            
            return mainContent;
        }
        
        return text;
    }
    
    // Helper function to format markdown
    function formatMarkdown(text) {
        // Process code blocks with language
        text = text.replace(/```([a-z]*)\n([\s\S]*?)```/g, function(match, lang, code) {
            const language = lang || 'python'; // Default to python if no language specified
            return `<pre class="bg-gray-900 rounded-md p-4 my-4 overflow-x-auto w-full">
                      <code class="language-${language} block text-left">${escapeHtml(code.trim())}</code>
                    </pre>`;
        });
        
        // Process inline code
        text = text.replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-pink-600">$1</code>');
        
        // Process headers
        text = text.replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>');
        text = text.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-6 mb-2">$1</h2>');
        text = text.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-6 mb-3">$1</h1>');
        
        // Process bold
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Process italics
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Process lists
        text = text.replace(/^- (.*$)/gm, '<li class="ml-4 list-disc">$1</li>');
        text = text.replace(/^(\d+)\. (.*$)/gm, '<li class="ml-4 list-decimal">$2</li>');
        
        // Process paragraphs
        text = text.replace(/\n\n/g, '</p><p class="mb-3">');
        
        // Process citations
        text = formatCitations(text);
        
        return `<div class="prose max-w-none text-gray-800"><p class="mb-3">${text}</p></div>`;
    }
    
    // Helper function to escape HTML
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // Function to copy text to clipboard
    function copyText(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const text = element.innerText || element.textContent;
        
        navigator.clipboard.writeText(text).then(() => {
            // Show feedback
            const notification = document.createElement('div');
            notification.className = 'fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded shadow-lg z-50';
            notification.textContent = 'Copied to clipboard';
            document.body.appendChild(notification);
            
            // Remove after 2 seconds
            setTimeout(() => {
                notification.remove();
            }, 2000);
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    }
    
    // Add copy button to code blocks
    function addCopyButton(codeBlock) {
        const container = codeBlock.parentNode;
        
        // Check if container already has a copy button
        if (container.querySelector('.code-copy-button')) {
            return; // Skip if button already exists
        }
        
        container.style.position = 'relative';
        
        const button = document.createElement('button');
        button.className = 'absolute top-2 right-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md px-2 py-1 text-xs code-copy-button';
        button.textContent = 'Copy';
        button.addEventListener('click', () => {
            // Get text content from the code block
            const codeText = codeBlock.textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(codeText).then(() => {
                // Visual feedback
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
                button.textContent = 'Error';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            });
        });
        
        container.appendChild(button);
    }
    
    // Add syntax highlighting to code blocks using Prism.js
    function highlightCode(codeBlock) {
        // Skip if already processed
        if (codeBlock.classList.contains('prism-highlighted')) {
            return;
        }
        
        // Mark as processed
        codeBlock.classList.add('prism-highlighted');
        
        // Existing highlight code...
        const preElement = codeBlock.parentElement;
        
        // Rest of your highlighting code...
        Prism.highlightElement(codeBlock);
        preElement.style.backgroundColor = '#1e293b';
    }
    
    // Helper function to show typing indicator
    function showTypingIndicator() {
        const indicatorId = `typing-${Date.now()}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start mb-4';
        messageDiv.id = indicatorId;
        
        messageDiv.innerHTML = `
            <div class="bg-blue-50 border border-blue-100 rounded-2xl py-3 px-4">
                <div class="flex space-x-2">
                    <div class="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
                    <div class="w-2 h-2 rounded-full bg-blue-400 animate-pulse" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 rounded-full bg-blue-400 animate-pulse" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return indicatorId;
    }
    
    // Helper function to remove typing indicator
    function removeTypingIndicator(indicatorId) {
        const indicator = document.getElementById(indicatorId);
        if (indicator) {
            indicator.remove();
        }
    }
    
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            userInput.value = '';
            userInput.focus();
        });
    }
    
    // Help modal functionality
    const helpButton = document.getElementById('help-button');
    const helpModal = document.getElementById('help-modal');
    const closeHelp = document.getElementById('close-help');
    const closeHelpBtn = document.getElementById('close-help-btn');
    
    if (helpButton && helpModal) {
        helpButton.addEventListener('click', () => {
            helpModal.classList.remove('hidden');
        });
        
        if (closeHelp) {
            closeHelp.addEventListener('click', () => {
                helpModal.classList.add('hidden');
            });
        }
        
        if (closeHelpBtn) {
            closeHelpBtn.addEventListener('click', () => {
                helpModal.classList.add('hidden');
            });
        }
    }
    
    // Initialize with focus on input
    if (userInput) {
        userInput.focus();
    }
});
