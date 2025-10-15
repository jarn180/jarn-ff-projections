/**
 * Notification System for Fantasy Football Projections
 * Handles browser notifications, toast messages, and update badges
 */

class NotificationManager {
    constructor() {
        this.storageKey = 'ff_projections_last_seen';
        this.notificationPermission = 'default';
        this.init();
    }

    init() {
        // Check if browser supports notifications
        if ('Notification' in window) {
            this.notificationPermission = Notification.permission;
        }

        // Check for updates on load
        this.checkForUpdates();
    }

    /**
     * Request permission for browser notifications
     */
    async requestPermission() {
        if (!('Notification' in window)) {
            console.warn('Browser does not support notifications');
            return false;
        }

        if (this.notificationPermission === 'granted') {
            return true;
        }

        try {
            const permission = await Notification.requestPermission();
            this.notificationPermission = permission;
            return permission === 'granted';
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return false;
        }
    }

    /**
     * Check for projection updates
     */
    async checkForUpdates() {
        try {
            const response = await fetch('/api/projections/status');
            const data = await response.json();

            if (!data.success) {
                return;
            }

            const lastSeen = this.getLastSeen();
            const currentUpdate = {
                timestamp: data.last_updated_timestamp,
                playerCount: data.total_players,
                lastUpdatedDisplay: data.last_updated_display
            };

            // Check if this is a new update
            if (lastSeen && this.isNewUpdate(lastSeen, currentUpdate)) {
                this.notifyUpdate(currentUpdate, lastSeen);
            }

            // Store current state for next check
            this.saveLastSeen(currentUpdate);

        } catch (error) {
            console.error('Error checking for updates:', error);
        }
    }

    /**
     * Determine if there's a new update
     */
    isNewUpdate(lastSeen, current) {
        // New if timestamp changed or player count increased
        return (
            current.timestamp !== lastSeen.timestamp ||
            current.playerCount > lastSeen.playerCount
        );
    }

    /**
     * Notify user of updates
     */
    notifyUpdate(current, lastSeen) {
        const playerDiff = current.playerCount - lastSeen.playerCount;
        const message = playerDiff > 0
            ? `${playerDiff} new player projection${playerDiff > 1 ? 's' : ''} added!`
            : 'Projections updated!';

        // Show toast notification (always)
        this.showToast(message, 'success');

        // Show browser notification (if permitted)
        if (this.notificationPermission === 'granted') {
            this.showBrowserNotification('Projections Updated', message);
        }

        // Update badge
        if (playerDiff > 0) {
            this.showBadge(playerDiff);
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Remove existing toasts
        const existing = document.querySelectorAll('.notification-toast');
        existing.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `notification-toast notification-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">${this.getToastIcon(type)}</div>
                <div class="toast-message">${message}</div>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    /**
     * Get icon for toast type
     */
    getToastIcon(type) {
        const icons = {
            success: '✓',
            info: 'i',
            warning: '⚠',
            error: '✕'
        };
        return icons[type] || icons.info;
    }

    /**
     * Show browser notification
     */
    showBrowserNotification(title, message) {
        if (this.notificationPermission !== 'granted') {
            return;
        }

        try {
            const notification = new Notification(title, {
                body: message,
                icon: '/static/images/favicon.svg',
                badge: '/static/images/favicon.svg',
                tag: 'projection-update',
                requireInteraction: false
            });

            notification.onclick = () => {
                window.focus();
                notification.close();
            };

            // Auto-close after 10 seconds
            setTimeout(() => notification.close(), 10000);
        } catch (error) {
            console.error('Error showing browser notification:', error);
        }
    }

    /**
     * Show update badge
     */
    showBadge(count) {
        let badge = document.querySelector('.notification-badge');

        if (!badge) {
            badge = document.createElement('div');
            badge.className = 'notification-badge';
            document.querySelector('header').appendChild(badge);
        }

        badge.textContent = count > 99 ? '99+' : count;
        badge.classList.add('show');

        // Remove badge when clicked
        badge.onclick = () => {
            badge.classList.remove('show');
            setTimeout(() => badge.remove(), 300);
        };
    }

    /**
     * Get last seen update info from localStorage
     */
    getLastSeen() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Error reading last seen data:', error);
            return null;
        }
    }

    /**
     * Save current update info to localStorage
     */
    saveLastSeen(updateInfo) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(updateInfo));
        } catch (error) {
            console.error('Error saving last seen data:', error);
        }
    }

    /**
     * Clear notification history
     */
    clearHistory() {
        try {
            localStorage.removeItem(this.storageKey);
            this.showToast('Notification history cleared', 'success');
        } catch (error) {
            console.error('Error clearing history:', error);
        }
    }

    /**
     * Start periodic update checks
     */
    startPeriodicCheck(intervalMinutes = 5) {
        // Check immediately
        this.checkForUpdates();

        // Set up periodic checks
        setInterval(() => {
            this.checkForUpdates();
        }, intervalMinutes * 60 * 1000);
    }
}

// Initialize notification manager
const notificationManager = new NotificationManager();

// Export for use in other scripts
window.notificationManager = notificationManager;
