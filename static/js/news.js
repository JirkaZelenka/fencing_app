// News functionality
(function() {
    let currentNewsId = null;
    let newsData = [];
    let unreadCount = 0;

    // Initialize news on page load
    document.addEventListener('DOMContentLoaded', function() {
        loadNews();
        
        // Setup hover for dropdown
        const newsDropdown = document.getElementById('newsDropdown');
        const newsDropdownMenu = document.getElementById('newsDropdownMenu');
        
        if (newsDropdown && newsDropdownMenu) {
            let hoverTimeout;
            
            newsDropdown.addEventListener('mouseenter', function() {
                clearTimeout(hoverTimeout);
                const bsDropdown = new bootstrap.Dropdown(document.getElementById('newsDropdownLink'));
                bsDropdown.show();
            });
            
            newsDropdown.addEventListener('mouseleave', function() {
                hoverTimeout = setTimeout(function() {
                    const bsDropdown = bootstrap.Dropdown.getInstance(document.getElementById('newsDropdownLink'));
                    if (bsDropdown) {
                        bsDropdown.hide();
                    }
                }, 200);
            });
            
            // Prevent dropdown from closing when hovering over it
            newsDropdownMenu.addEventListener('mouseenter', function() {
                clearTimeout(hoverTimeout);
            });
            
            newsDropdownMenu.addEventListener('mouseleave', function() {
                hoverTimeout = setTimeout(function() {
                    const bsDropdown = bootstrap.Dropdown.getInstance(document.getElementById('newsDropdownLink'));
                    if (bsDropdown) {
                        bsDropdown.hide();
                    }
                }, 200);
            });
        }
        
        // Setup modal events
        const newsModal = document.getElementById('newsModal');
        if (newsModal) {
            newsModal.addEventListener('hidden.bs.modal', function() {
                currentNewsId = null;
                loadNews(); // Reload to update read status
            });
        }
        
        // Setup mark as read button
        const markReadBtn = document.getElementById('markNewsReadBtn');
        if (markReadBtn) {
            markReadBtn.addEventListener('click', function() {
                if (currentNewsId) {
                    markNewsAsRead(currentNewsId);
                }
            });
        }
    });

    function loadNews() {
        fetch('/news/list/')
            .then(response => response.json())
            .then(data => {
                newsData = data.news;
                unreadCount = data.unread_count;
                renderNewsDropdown();
                updateUnreadIcon();
            })
            .catch(error => {
                console.error('Error loading news:', error);
            });
    }

    function renderNewsDropdown() {
        const loadingItem = document.getElementById('newsLoadingItem');
        const emptyItem = document.getElementById('newsEmptyItem');
        const dropdownMenu = document.getElementById('newsDropdownMenu');
        
        if (!dropdownMenu) return;
        
        // Remove existing news items (keep header and divider)
        const existingItems = dropdownMenu.querySelectorAll('.news-item');
        existingItems.forEach(item => item.remove());
        
        if (newsData.length === 0) {
            if (loadingItem) loadingItem.style.display = 'none';
            if (emptyItem) emptyItem.style.display = 'block';
            return;
        }
        
        if (loadingItem) loadingItem.style.display = 'none';
        if (emptyItem) emptyItem.style.display = 'none';
        
        // Add news items
        newsData.forEach(news => {
            const li = document.createElement('li');
            li.className = 'news-item';
            
            const a = document.createElement('a');
            a.className = 'dropdown-item news-dropdown-item';
            if (!news.is_read) {
                a.classList.add('news-unread');
            }
            a.href = '#';
            a.innerHTML = `
                <div class="news-item-title">${escapeHtml(news.title)}</div>
                <div class="news-item-preview">${escapeHtml(news.text)}</div>
                <div class="news-item-date">${news.date}</div>
            `;
            
            a.addEventListener('click', function(e) {
                e.preventDefault();
                // Close dropdown
                const bsDropdown = bootstrap.Dropdown.getInstance(document.getElementById('newsDropdownLink'));
                if (bsDropdown) {
                    bsDropdown.hide();
                }
                showNewsModal(news.id);
            });
            
            li.appendChild(a);
            dropdownMenu.appendChild(li);
        });
    }

    function showNewsModal(newsId) {
        currentNewsId = newsId;
        
        fetch(`/news/${newsId}/`)
            .then(response => response.json())
            .then(data => {
                const modal = new bootstrap.Modal(document.getElementById('newsModal'));
                document.getElementById('newsModalTitle').textContent = data.title;
                document.getElementById('newsModalDate').textContent = data.date;
                document.getElementById('newsModalText').textContent = data.text;
                
                const markReadBtn = document.getElementById('markNewsReadBtn');
                if (data.is_read) {
                    markReadBtn.style.display = 'none';
                } else {
                    markReadBtn.style.display = 'block';
                }
                
                modal.show();
            })
            .catch(error => {
                console.error('Error loading news detail:', error);
            });
    }

    function markNewsAsRead(newsId) {
        fetch(`/news/${newsId}/mark-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the news item in the dropdown
                    const newsItem = newsData.find(n => n.id === newsId);
                    if (newsItem) {
                        newsItem.is_read = true;
                    }
                    unreadCount = data.unread_count;
                    renderNewsDropdown();
                    updateUnreadIcon();
                    
                    // Hide the mark as read button
                    document.getElementById('markNewsReadBtn').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error marking news as read:', error);
            });
    }

    function updateUnreadIcon() {
        const icon = document.getElementById('newsUnreadIcon');
        if (icon) {
            if (unreadCount > 0) {
                icon.style.display = 'inline-block';
            } else {
                icon.style.display = 'none';
            }
        }
    }

    function formatNewsText(text) {
        // Convert newlines to <br> tags and preserve paragraphs
        const escaped = escapeHtml(text);
        return escaped.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
})();

