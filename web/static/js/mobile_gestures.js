/**
 * CORA Mobile Gestures
 * Provides touch gesture support for mobile devices
 */

class MobileGestures {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.touchStartTime = 0;
        this.longPressTimer = null;
        this.longPressThreshold = 500; // 500ms for long press
        this.swipeThreshold = 50; // 50px minimum for swipe
        this.pullToRefreshThreshold = 80; // 80px to trigger refresh
        
        this.init();
    }
    
    init() {
        this.setupGestureListeners();
        this.addGestureStyles();
    }
    
    setupGestureListeners() {
        // Add gesture listeners to common containers
        this.addSwipeGestures();
        this.addPullToRefresh();
        this.addLongPressGestures();
        this.addPinchGestures();
    }
    
    addSwipeGestures() {
        // Add swipe gestures to expense items
        const expenseItems = document.querySelectorAll('.expense-item, .transaction-item');
        expenseItems.forEach(item => {
            this.addSwipeToItem(item);
        });
        
        // Add swipe gestures to job items
        const jobItems = document.querySelectorAll('.job-item, .job-card');
        jobItems.forEach(item => {
            this.addSwipeToItem(item);
        });
        
        // Listen for dynamically added items
        this.observeNewItems();
    }
    
    addSwipeToItem(item) {
        let startX = 0;
        let currentX = 0;
        let isSwiping = false;
        let swipeAction = null;
        
        // Touch start
        item.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            currentX = startX;
            isSwiping = false;
            
            // Reset any existing swipe action
            if (swipeAction) {
                swipeAction.remove();
                swipeAction = null;
            }
        }, { passive: true });
        
        // Touch move
        item.addEventListener('touchmove', (e) => {
            if (!startX) return;
            
            currentX = e.touches[0].clientX;
            const diffX = currentX - startX;
            
            // Only allow horizontal swiping
            if (Math.abs(diffX) > 10) {
                e.preventDefault();
                isSwiping = true;
                
                // Add visual feedback
                item.style.transform = `translateX(${diffX}px)`;
                item.style.transition = 'none';
                
                // Show swipe action background
                if (!swipeAction) {
                    swipeAction = this.createSwipeAction(item, diffX > 0 ? 'right' : 'left');
                    item.parentNode.insertBefore(swipeAction, item);
                }
                
                // Update swipe action position
                if (swipeAction) {
                    swipeAction.style.transform = `translateX(${diffX}px)`;
                }
            }
        }, { passive: false });
        
        // Touch end
        item.addEventListener('touchend', (e) => {
            if (!isSwiping) return;
            
            const diffX = currentX - startX;
            const absDiffX = Math.abs(diffX);
            
            // Reset position
            item.style.transform = '';
            item.style.transition = 'transform 0.3s ease';
            
            // Check if swipe threshold is met
            if (absDiffX > this.swipeThreshold) {
                if (diffX > 0) {
                    // Swipe right - edit
                    this.handleSwipeRight(item);
                } else {
                    // Swipe left - delete
                    this.handleSwipeLeft(item);
                }
            }
            
            // Remove swipe action
            if (swipeAction) {
                swipeAction.remove();
                swipeAction = null;
            }
            
            // Reset
            startX = 0;
            currentX = 0;
            isSwiping = false;
        }, { passive: true });
    }
    
    createSwipeAction(item, direction) {
        const action = document.createElement('div');
        action.className = `swipe-action swipe-action-${direction}`;
        
        if (direction === 'right') {
            action.innerHTML = `
                <div class="swipe-action-content">
                    <div class="swipe-icon">✏️</div>
                    <div class="swipe-text">Edit</div>
                </div>
            `;
        } else {
            action.innerHTML = `
                <div class="swipe-action-content">
                    <div class="swipe-icon">🗑️</div>
                    <div class="swipe-text">Delete</div>
                </div>
            `;
        }
        
        return action;
    }
    
    handleSwipeRight(item) {
        // Handle edit action
        // console.log('Edit item:', item);
        
        // Show edit modal or form
        this.showEditModal(item);
        
        // Haptic feedback
        this.triggerHapticFeedback('light');
    }
    
    handleSwipeLeft(item) {
        // Handle delete action
        // console.log('Delete item:', item);
        
        // Show confirmation dialog
        this.showDeleteConfirmation(item);
        
        // Haptic feedback
        this.triggerHapticFeedback('medium');
    }
    
    addPullToRefresh() {
        const refreshableContainers = document.querySelectorAll('.expenses-list, .transactions-list, .jobs-list');
        
        refreshableContainers.forEach(container => {
            let startY = 0;
            let currentY = 0;
            let isPulling = false;
            let pullIndicator = null;
            
            // Touch start
            container.addEventListener('touchstart', (e) => {
                // Only trigger pull-to-refresh when at the top
                if (container.scrollTop === 0) {
                    startY = e.touches[0].clientY;
                    isPulling = false;
                }
            }, { passive: true });
            
            // Touch move
            container.addEventListener('touchmove', (e) => {
                if (container.scrollTop === 0 && startY) {
                    currentY = e.touches[0].clientY;
                    const diffY = currentY - startY;
                    
                    if (diffY > 0) {
                        e.preventDefault();
                        isPulling = true;
                        
                        // Create pull indicator if not exists
                        if (!pullIndicator) {
                            pullIndicator = this.createPullIndicator(container);
                            container.parentNode.insertBefore(pullIndicator, container);
                        }
                        
                        // Update pull indicator
                        const pullDistance = Math.min(diffY, this.pullToRefreshThreshold);
                        const pullProgress = pullDistance / this.pullToRefreshThreshold;
                        
                        pullIndicator.style.transform = `translateY(${pullDistance}px)`;
                        pullIndicator.style.opacity = pullProgress;
                        
                        // Update icon rotation
                        const icon = pullIndicator.querySelector('.pull-icon');
                        if (icon) {
                            icon.style.transform = `rotate(${pullProgress * 180}deg)`;
                        }
                    }
                }
            }, { passive: false });
            
            // Touch end
            container.addEventListener('touchend', (e) => {
                if (isPulling && startY) {
                    const diffY = currentY - startY;
                    
                    if (diffY > this.pullToRefreshThreshold) {
                        // Trigger refresh
                        this.triggerRefresh(container);
                    }
                    
                    // Reset pull indicator
                    if (pullIndicator) {
                        pullIndicator.style.transform = '';
                        pullIndicator.style.opacity = '';
                        setTimeout(() => {
                            if (pullIndicator && pullIndicator.parentNode) {
                                pullIndicator.parentNode.removeChild(pullIndicator);
                            }
                        }, 300);
                        pullIndicator = null;
                    }
                    
                    // Reset
                    startY = 0;
                    currentY = 0;
                    isPulling = false;
                }
            }, { passive: true });
        });
    }
    
    createPullIndicator(container) {
        const indicator = document.createElement('div');
        indicator.className = 'pull-to-refresh-indicator';
        indicator.innerHTML = `
            <div class="pull-content">
                <div class="pull-icon">🔄</div>
                <div class="pull-text">Pull to refresh</div>
            </div>
        `;
        return indicator;
    }
    
    triggerRefresh(container) {
        // console.log('Refreshing container:', container);
        
        // Show loading state
        const indicator = container.parentNode.querySelector('.pull-to-refresh-indicator');
        if (indicator) {
            const icon = indicator.querySelector('.pull-icon');
            const text = indicator.querySelector('.pull-text');
            
            icon.style.animation = 'spin 1s linear infinite';
            text.textContent = 'Refreshing...';
        }
        
        // Trigger actual refresh based on container type
        if (container.classList.contains('expenses-list')) {
            this.refreshExpenses();
        } else if (container.classList.contains('jobs-list')) {
            this.refreshJobs();
        } else if (container.classList.contains('transactions-list')) {
            this.refreshTransactions();
        }
        
        // Haptic feedback
        this.triggerHapticFeedback('success');
    }
    
    addLongPressGestures() {
        const longPressItems = document.querySelectorAll('.expense-item, .job-item, .transaction-item');
        
        longPressItems.forEach(item => {
            let longPressTimer = null;
            let hasLongPressed = false;
            
            // Touch start
            item.addEventListener('touchstart', (e) => {
                hasLongPressed = false;
                longPressTimer = setTimeout(() => {
                    hasLongPressed = true;
                    this.handleLongPress(item, e);
                }, this.longPressThreshold);
            }, { passive: true });
            
            // Touch move
            item.addEventListener('touchmove', (e) => {
                // Cancel long press if finger moves too much
                if (longPressTimer) {
                    clearTimeout(longPressTimer);
                    longPressTimer = null;
                }
            }, { passive: true });
            
            // Touch end
            item.addEventListener('touchend', (e) => {
                if (longPressTimer) {
                    clearTimeout(longPressTimer);
                    longPressTimer = null;
                }
                
                // Prevent click if long press occurred
                if (hasLongPressed) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }, { passive: false });
        });
    }
    
    handleLongPress(item, event) {
        // console.log('Long press on item:', item);
        
        // Show context menu
        this.showContextMenu(item, event);
        
        // Haptic feedback
        this.triggerHapticFeedback('heavy');
    }
    
    addPinchGestures() {
        // Add pinch-to-zoom for charts and images
        const pinchContainers = document.querySelectorAll('.chart-container, .receipt-image');
        
        pinchContainers.forEach(container => {
            let initialDistance = 0;
            let initialScale = 1;
            let currentScale = 1;
            
            container.addEventListener('touchstart', (e) => {
                if (e.touches.length === 2) {
                    initialDistance = this.getDistance(e.touches[0], e.touches[1]);
                    initialScale = currentScale;
                }
            }, { passive: true });
            
            container.addEventListener('touchmove', (e) => {
                if (e.touches.length === 2) {
                    e.preventDefault();
                    
                    const currentDistance = this.getDistance(e.touches[0], e.touches[1]);
                    const scale = (currentDistance / initialDistance) * initialScale;
                    
                    // Limit scale between 0.5 and 3
                    currentScale = Math.max(0.5, Math.min(3, scale));
                    
                    container.style.transform = `scale(${currentScale})`;
                }
            }, { passive: false });
            
            container.addEventListener('touchend', (e) => {
                // Reset if no fingers left
                if (e.touches.length === 0) {
                    // Snap to bounds
                    if (currentScale < 0.8) {
                        currentScale = 1;
                        container.style.transform = 'scale(1)';
                    } else if (currentScale > 2.5) {
                        currentScale = 2;
                        container.style.transform = 'scale(2)';
                    }
                }
            }, { passive: true });
        });
    }
    
    getDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    observeNewItems() {
        // Use MutationObserver to watch for new items
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if new expense items were added
                        const newExpenseItems = node.querySelectorAll('.expense-item, .transaction-item');
                        newExpenseItems.forEach(item => {
                            this.addSwipeToItem(item);
                        });
                        
                        // Check if new job items were added
                        const newJobItems = node.querySelectorAll('.job-item, .job-card');
                        newJobItems.forEach(item => {
                            this.addSwipeToItem(item);
                        });
                        
                        // Check if the node itself is an item
                        if (node.classList && (
                            node.classList.contains('expense-item') ||
                            node.classList.contains('transaction-item') ||
                            node.classList.contains('job-item') ||
                            node.classList.contains('job-card')
                        )) {
                            this.addSwipeToItem(node);
                        }
                    }
                });
            });
        });
        
        // Observe the document body for new items
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    showEditModal(item) {
        // Create edit modal
        const modal = document.createElement('div');
        modal.className = 'edit-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="mobileGestures.closeModal()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Edit Item</h3>
                    <button class="close-btn" onclick="mobileGestures.closeModal()">×</button>
                </div>
                <div class="modal-body">
                    <p>Edit functionality coming soon...</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Animate in
        setTimeout(() => {
            modal.classList.add('open');
        }, 10);
    }
    
    showDeleteConfirmation(item) {
        // Create delete confirmation
        const modal = document.createElement('div');
        modal.className = 'delete-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="mobileGestures.closeModal()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Delete Item</h3>
                    <button class="close-btn" onclick="mobileGestures.closeModal()">×</button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete this item?</p>
                    <div class="modal-actions">
                        <button class="btn-secondary" onclick="mobileGestures.closeModal()">Cancel</button>
                        <button class="btn-danger" onclick="mobileGestures.confirmDelete()">Delete</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Store reference to item being deleted
        modal.itemToDelete = item;
        
        // Animate in
        setTimeout(() => {
            modal.classList.add('open');
        }, 10);
    }
    
    showContextMenu(item, event) {
        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.innerHTML = `
            <div class="menu-item" onclick="mobileGestures.editItem()">
                <div class="menu-icon">✏️</div>
                <div class="menu-text">Edit</div>
            </div>
            <div class="menu-item" onclick="mobileGestures.duplicateItem()">
                <div class="menu-icon">📋</div>
                <div class="menu-text">Duplicate</div>
            </div>
            <div class="menu-item" onclick="mobileGestures.shareItem()">
                <div class="menu-icon">📤</div>
                <div class="menu-text">Share</div>
            </div>
            <div class="menu-item danger" onclick="mobileGestures.deleteItem()">
                <div class="menu-icon">🗑️</div>
                <div class="menu-text">Delete</div>
            </div>
        `;
        
        // Position menu near touch point
        const rect = item.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.left = `${event.touches[0].clientX}px`;
        menu.style.top = `${event.touches[0].clientY}px`;
        
        document.body.appendChild(menu);
        
        // Store reference
        menu.itemReference = item;
        
        // Close menu when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 100);
    }
    
    closeModal() {
        const modals = document.querySelectorAll('.edit-modal, .delete-modal');
        modals.forEach(modal => {
            modal.classList.remove('open');
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
        });
    }
    
    confirmDelete() {
        const modal = document.querySelector('.delete-modal');
        if (modal && modal.itemToDelete) {
            // Perform delete action
            // console.log('Deleting item:', modal.itemToDelete);
            
            // Remove item with animation
            modal.itemToDelete.style.transform = 'translateX(-100%)';
            modal.itemToDelete.style.opacity = '0';
            
            setTimeout(() => {
                if (modal.itemToDelete.parentNode) {
                    modal.itemToDelete.parentNode.removeChild(modal.itemToDelete);
                }
            }, 300);
            
            this.closeModal();
        }
    }
    
    editItem() {
        // console.log('Edit item from context menu');
        this.closeModal();
    }
    
    duplicateItem() {
        // console.log('Duplicate item');
        this.closeModal();
    }
    
    shareItem() {
        // console.log('Share item');
        this.closeModal();
    }
    
    deleteItem() {
        // console.log('Delete item from context menu');
        this.closeModal();
    }
    
    refreshExpenses() {
        // Trigger expenses refresh
        if (typeof loadTransactions === 'function') {
            loadTransactions();
        }
    }
    
    refreshJobs() {
        // Trigger jobs refresh
        if (typeof loadJobs === 'function') {
            loadJobs();
        }
    }
    
    refreshTransactions() {
        // Trigger transactions refresh
        if (typeof loadTransactions === 'function') {
            loadTransactions();
        }
    }
    
    triggerHapticFeedback(type) {
        if ('vibrate' in navigator) {
            switch (type) {
                case 'light':
                    navigator.vibrate(10);
                    break;
                case 'medium':
                    navigator.vibrate(50);
                    break;
                case 'heavy':
                    navigator.vibrate(100);
                    break;
                case 'success':
                    navigator.vibrate([50, 50, 50]);
                    break;
                case 'error':
                    navigator.vibrate([100, 50, 100]);
                    break;
            }
        }
    }
    
    addGestureStyles() {
        const styleId = 'mobile-gestures-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            /* Swipe Actions */
            .swipe-action {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1;
                pointer-events: none;
            }
            
            .swipe-action-right {
                background: linear-gradient(90deg, #9B6EC8, #7C3AED);
                justify-content: flex-start;
                padding-left: 20px;
            }
            
            .swipe-action-left {
                background: linear-gradient(270deg, #ef4444, #dc2626);
                justify-content: flex-end;
                padding-right: 20px;
            }
            
            .swipe-action-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
                color: white;
            }
            
            .swipe-icon {
                font-size: 20px;
            }
            
            .swipe-text {
                font-size: 12px;
                font-weight: 500;
            }
            
            /* Pull to Refresh */
            .pull-to-refresh-indicator {
                position: absolute;
                top: -60px;
                left: 0;
                right: 0;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: white;
                border-bottom: 1px solid #e5e7eb;
                z-index: 10;
                transition: transform 0.3s ease, opacity 0.3s ease;
            }
            
            .pull-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
            }
            
            .pull-icon {
                font-size: 20px;
                transition: transform 0.3s ease;
            }
            
            .pull-text {
                font-size: 14px;
                color: #6b7280;
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            /* Context Menu */
            .context-menu {
                position: fixed;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                padding: 8px;
                z-index: 10000;
                min-width: 150px;
                transform: translate(-50%, -100%);
                margin-top: -10px;
            }
            
            .menu-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: background 0.2s ease;
            }
            
            .menu-item:hover {
                background: #f3f4f6;
            }
            
            .menu-item.danger:hover {
                background: #fef2f2;
                color: #dc2626;
            }
            
            .menu-icon {
                font-size: 16px;
            }
            
            .menu-text {
                font-size: 14px;
                font-weight: 500;
            }
            
            /* Modals */
            .edit-modal, .delete-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
            }
            
            .edit-modal.open, .delete-modal.open {
                display: flex;
            }
            
            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            
            .modal-content {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 400px;
                animation: modalSlideIn 0.3s ease;
            }
            
            @keyframes modalSlideIn {
                from {
                    transform: translateY(-20px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .modal-header {
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #111827;
            }
            
            .close-btn {
                background: none;
                border: none;
                font-size: 24px;
                color: #6b7280;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            
            .close-btn:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .modal-body {
                padding: 24px;
            }
            
            .modal-actions {
                display: flex;
                gap: 12px;
                margin-top: 20px;
            }
            
            .btn-secondary, .btn-danger {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
                flex: 1;
            }
            
            .btn-secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            
            .btn-secondary:hover {
                background: #e5e7eb;
            }
            
            .btn-danger {
                background: #ef4444;
                color: white;
            }
            
            .btn-danger:hover {
                background: #dc2626;
            }
            
            /* Touch-friendly improvements */
            .expense-item, .job-item, .transaction-item {
                touch-action: pan-y;
                user-select: none;
                -webkit-user-select: none;
            }
            
            /* Prevent text selection during gestures */
            .gesture-active {
                user-select: none;
                -webkit-user-select: none;
            }
            
            @media (max-width: 768px) {
                .context-menu {
                    min-width: 120px;
                }
                
                .menu-item {
                    padding: 10px 12px;
                }
                
                .menu-text {
                    font-size: 13px;
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mobileGestures = new MobileGestures();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileGestures;
} 