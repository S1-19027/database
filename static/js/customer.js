// 初始化WebSocket连接
const socket = new WebSocket(`ws://${window.location.host}/ws/customer/`);

// 发送消息函数
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (message) {
        socket.send(JSON.stringify({
            'type': 'message',
            'content': message
        }));
        input.value = '';
    }
}

// 处理FAQ点击
function sendFAQ(question) {
    socket.send(JSON.stringify({
        'type': 'faq',
        'content': question
    }));
}

// 处理商品操作
function purchaseProduct(productId) {
    // 打开支付模态框
    showPaymentModal(productId);
}

// WebSocket消息处理
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatArea = document.getElementById('chatArea');
    
    // 根据消息类型更新UI
    if (data.type === 'ai_response') {
        chatArea.innerHTML += `<div class="ai-message">${data.content}</div>`;
    } else if (data.type === 'product_info') {
        // 显示商品详情
    }
};