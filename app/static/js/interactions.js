// 加载评论的回复
function loadReplies(reviewId) {
    fetch(`/interactions/review/${reviewId}/replies`)
        .then(response => response.json())
        .then(replies => {
            const repliesSection = document.getElementById(`replies-${reviewId}`);
            repliesSection.innerHTML = replies.map(reply => `
                <div class="reply mb-2">
                    <small class="fw-bold">${reply.username}</small>
                    <small class="text-muted"> - ${new Date(reply.created_at).toLocaleString()}</small>
                    <p class="mb-1">${reply.content}</p>
                </div>
            `).join('');
        });
}

// 提交回复
function submitReply(event, reviewId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input');
    
    fetch(`/interactions/review/${reviewId}/reply`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `content=${encodeURIComponent(input.value)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            input.value = '';
            loadReplies(reviewId);
        }
    });
}

// 初始化所有功能
document.addEventListener('DOMContentLoaded', () => {
    // 点赞功能
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', () => {
            if (button.disabled) return;
            
            const reviewId = button.dataset.reviewId;
            const action = button.querySelector('.bi-heart-fill') ? 'unlike' : 'like';
            
            fetch(`/interactions/review/${reviewId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `action=${action}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    loadLikeCount(reviewId);
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to like/unlike review');
            });
        });
    });

    // 举报功能
    document.querySelectorAll('.report-btn').forEach(button => {
        button.removeEventListener('click', reportHandler); // 移除可能存在的旧事件监听器
        button.addEventListener('click', reportHandler);
    });

    // 回复按钮功能
    document.querySelectorAll('.reply-btn').forEach(button => {
        button.addEventListener('click', () => {
            const reviewId = button.dataset.reviewId;
            const replyForm = document.getElementById(`reply-form-${reviewId}`);
            replyForm.classList.toggle('d-none');
            loadReplies(reviewId);
        });
    });

    // 初始化所有回复区域
    document.querySelectorAll('.replies-section').forEach(section => {
        const reviewId = section.id.split('-')[1];
        loadReplies(reviewId);
    });
});

// 举报处理函数
function reportHandler() {
    const reviewId = this.dataset.reviewId;
    if (confirm('Are you sure you want to report this review?')) {
        fetch(`/interactions/review/${reviewId}/report`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Review has been reported.');
                this.disabled = true;
                this.textContent = 'Reported';
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to report review');
        });
    }
} 