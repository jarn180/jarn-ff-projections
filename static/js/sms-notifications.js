/**
 * SMS Notification System - Frontend
 * Handles SMS subscription UI and interactions
 */

class SMSNotificationUI {
    constructor() {
        this.storageKey = 'ff_sms_subscription';
        this.init();
    }

    init() {
        // Check if user is already subscribed
        const subscription = this.getStoredSubscription();
        if (subscription) {
            this.updateUI(true, subscription.phone);
        }
    }

    /**
     * Show SMS subscription modal
     */
    showSubscriptionModal() {
        const existingModal = document.getElementById('smsModal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'smsModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <button class="modal-close" onclick="closeSMSModal()">×</button>
                <h2 style="margin-bottom: 8px;">📱 SMS Notifications</h2>
                <p style="color: var(--text-secondary); margin-bottom: 24px;">
                    Get text updates when new fantasy football projections are added
                </p>

                <div id="smsSubscribeForm">
                    <div class="control-group">
                        <label for="smsPhone">Phone Number:</label>
                        <input
                            type="tel"
                            id="smsPhone"
                            placeholder="(555) 123-4567"
                            style="font-size: 16px;"
                        />
                    </div>

                    <div class="control-group">
                        <label for="smsRegion">Region:</label>
                        <select id="smsRegion" style="font-size: 16px;">
                            <option value="us">United States</option>
                            <option value="canada">Canada</option>
                            <option value="intl">International</option>
                        </select>
                    </div>

                    <div style="background: var(--surface); padding: 12px; border-radius: 8px; margin: 20px 0; font-size: 13px; color: var(--text-secondary);">
                        <strong style="color: var(--warning-color);">⚠️ Free Tier Limits:</strong>
                        <ul style="margin: 8px 0 0 20px; line-height: 1.6;">
                            <li>Limited to 1 free text per day per IP</li>
                            <li>Carrier delivery not guaranteed</li>
                            <li>Standard SMS rates may apply from your carrier</li>
                        </ul>
                    </div>

                    <div style="font-size: 12px; color: var(--text-tertiary); margin-bottom: 20px;">
                        By subscribing, you agree to receive SMS notifications. Reply STOP to any message to unsubscribe.
                    </div>

                    <button id="smsSubscribeBtn" class="btn-primary" onclick="subscribeSMS()">
                        Subscribe to SMS Updates
                    </button>

                    <div id="smsMessage" style="margin-top: 16px; display: none;"></div>
                </div>

                <div id="smsUnsubscribeForm" style="display: none;">
                    <p style="color: var(--secondary-color); margin-bottom: 20px;">
                        ✓ You are subscribed to SMS notifications
                    </p>
                    <p style="color: var(--text-secondary); margin-bottom: 20px;">
                        Phone: <strong id="subscribedPhone"></strong>
                    </p>
                    <button class="btn-danger" onclick="unsubscribeSMS()">
                        Unsubscribe
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);

        // Format phone input
        const phoneInput = document.getElementById('smsPhone');
        if (phoneInput) {
            phoneInput.addEventListener('input', this.formatPhoneNumber);
        }
    }

    /**
     * Format phone number input
     */
    formatPhoneNumber(event) {
        let input = event.target.value.replace(/\D/g, '');
        if (input.length > 10) input = input.substring(0, 10);

        let formatted = '';
        if (input.length > 0) {
            formatted = '(' + input.substring(0, 3);
        }
        if (input.length >= 4) {
            formatted += ') ' + input.substring(3, 6);
        }
        if (input.length >= 7) {
            formatted += '-' + input.substring(6, 10);
        }

        event.target.value = formatted;
    }

    /**
     * Subscribe to SMS notifications
     */
    async subscribe(phone, region) {
        try {
            const response = await fetch('/api/sms/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ phone, region })
            });

            const data = await response.json();

            if (data.success) {
                // Store subscription locally
                this.saveSubscription(phone, region);
                this.showMessage('✓ ' + data.message, 'success');

                // Update UI after short delay
                setTimeout(() => {
                    this.showUnsubscribeForm(phone);
                }, 2000);

                return true;
            } else {
                this.showMessage('✗ ' + data.error, 'error');
                return false;
            }
        } catch (error) {
            this.showMessage('✗ Network error: ' + error.message, 'error');
            return false;
        }
    }

    /**
     * Unsubscribe from SMS notifications
     */
    async unsubscribe(phone) {
        try {
            const response = await fetch('/api/sms/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ phone })
            });

            const data = await response.json();

            if (data.success) {
                // Remove subscription from storage
                this.clearSubscription();
                this.showMessage('✓ ' + data.message, 'success');

                // Update UI after short delay
                setTimeout(() => {
                    this.showSubscribeForm();
                }, 2000);

                return true;
            } else {
                this.showMessage('✗ ' + data.error, 'error');
                return false;
            }
        } catch (error) {
            this.showMessage('✗ Network error: ' + error.message, 'error');
            return false;
        }
    }

    /**
     * Show subscription form
     */
    showSubscribeForm() {
        const subscribeForm = document.getElementById('smsSubscribeForm');
        const unsubscribeForm = document.getElementById('smsUnsubscribeForm');

        if (subscribeForm) subscribeForm.style.display = 'block';
        if (unsubscribeForm) unsubscribeForm.style.display = 'none';
    }

    /**
     * Show unsubscribe form
     */
    showUnsubscribeForm(phone) {
        const subscribeForm = document.getElementById('smsSubscribeForm');
        const unsubscribeForm = document.getElementById('smsUnsubscribeForm');
        const subscribedPhone = document.getElementById('subscribedPhone');

        if (subscribeForm) subscribeForm.style.display = 'none';
        if (unsubscribeForm) unsubscribeForm.style.display = 'block';
        if (subscribedPhone) subscribedPhone.textContent = phone;
    }

    /**
     * Show message in modal
     */
    showMessage(message, type = 'info') {
        const messageDiv = document.getElementById('smsMessage');
        if (!messageDiv) return;

        messageDiv.textContent = message;
        messageDiv.className = `notification-message notification-${type}`;
        messageDiv.style.display = 'block';
        messageDiv.style.padding = '12px';
        messageDiv.style.borderRadius = '8px';
        messageDiv.style.marginTop = '16px';

        if (type === 'success') {
            messageDiv.style.background = 'rgba(48, 209, 88, 0.1)';
            messageDiv.style.border = '1px solid rgba(48, 209, 88, 0.3)';
            messageDiv.style.color = 'var(--secondary-color)';
        } else if (type === 'error') {
            messageDiv.style.background = 'rgba(255, 69, 58, 0.1)';
            messageDiv.style.border = '1px solid rgba(255, 69, 58, 0.3)';
            messageDiv.style.color = 'var(--danger-color)';
        }
    }

    /**
     * Save subscription to localStorage
     */
    saveSubscription(phone, region) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify({
                phone,
                region,
                subscribed_at: new Date().toISOString()
            }));
        } catch (error) {
            console.error('Error saving subscription:', error);
        }
    }

    /**
     * Get stored subscription
     */
    getStoredSubscription() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Error reading subscription:', error);
            return null;
        }
    }

    /**
     * Clear subscription from localStorage
     */
    clearSubscription() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            console.error('Error clearing subscription:', error);
        }
    }

    /**
     * Update main page UI based on subscription status
     */
    updateUI(isSubscribed, phone) {
        const btn = document.getElementById('smsNotificationBtn');
        if (!btn) return;

        if (isSubscribed) {
            btn.innerHTML = '✓ SMS Notifications Active';
            btn.classList.add('btn-success');
        } else {
            btn.innerHTML = '📱 Get SMS Notifications';
        }
    }
}

// Initialize SMS UI
const smsNotificationUI = new SMSNotificationUI();
window.smsNotificationUI = smsNotificationUI;

// Global functions for modal
function showSMSModal() {
    const subscription = smsNotificationUI.getStoredSubscription();
    smsNotificationUI.showSubscriptionModal();

    if (subscription) {
        smsNotificationUI.showUnsubscribeForm(subscription.phone);
    }
}

function closeSMSModal() {
    const modal = document.getElementById('smsModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }
}

async function subscribeSMS() {
    const phoneInput = document.getElementById('smsPhone');
    const regionSelect = document.getElementById('smsRegion');
    const btn = document.getElementById('smsSubscribeBtn');

    const phone = phoneInput.value.replace(/\D/g, '');
    const region = regionSelect.value;

    if (!phone || phone.length < 10) {
        smsNotificationUI.showMessage('✗ Please enter a valid phone number', 'error');
        return;
    }

    // Disable button during request
    btn.disabled = true;
    btn.textContent = 'Subscribing...';

    await smsNotificationUI.subscribe(phone, region);

    // Re-enable button
    btn.disabled = false;
    btn.textContent = 'Subscribe to SMS Updates';
}

async function unsubscribeSMS() {
    const subscription = smsNotificationUI.getStoredSubscription();
    if (!subscription) return;

    const confirmed = confirm('Are you sure you want to unsubscribe from SMS notifications?');
    if (!confirmed) return;

    await smsNotificationUI.unsubscribe(subscription.phone);
}
