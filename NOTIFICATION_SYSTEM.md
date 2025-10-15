# Notification System Documentation

## Overview

The Fantasy Football Projections app now includes a comprehensive notification system that alerts users when new projections are added or updated. The system works automatically and provides multiple notification methods.

## Features

### 1. **Toast Notifications** (Always Active)
- Elegant slide-in notifications in the top-right corner
- Shows when new projections are detected
- Displays the number of new players added
- Auto-dismisses after 5 seconds
- Matches the Apple-themed dark mode design

### 2. **Browser Push Notifications** (Opt-in)
- Native browser notifications
- Works even when the tab is in the background
- Requires user permission
- Shows desktop notifications when projections update

### 3. **Update Badge** (Auto-shown)
- Red badge showing number of new projections
- Appears in top-right corner
- Animated pulse effect
- Click to dismiss

### 4. **Automatic Update Detection**
- Checks for updates every 5 minutes automatically
- Compares timestamps and player counts
- Uses localStorage to track last seen state
- Works across browser sessions

## How It Works

### For Users

1. **First Visit:**
   - Click "Enable Notifications" button in the header
   - Grant browser notification permission when prompted
   - You'll receive a test notification confirming it works

2. **Subsequent Visits:**
   - Notifications work automatically
   - When you update projections (via `update_projections.py`), users will be notified
   - No action needed from users

3. **Notification Types:**
   - **New Players Added:** Shows exact count of new projections
   - **Projections Updated:** General update notification if player count is the same

### For Developers

#### Files Added/Modified:

1. **`static/js/notifications.js`** (NEW)
   - Core notification manager class
   - Handles all notification logic
   - LocalStorage tracking
   - Permission management

2. **`static/css/style.css`** (MODIFIED)
   - Added notification styles
   - Toast animations
   - Badge styling
   - Mobile responsive design

3. **`app.py`** (MODIFIED)
   - New endpoint: `/api/projections/status`
   - Returns metadata for update checking
   - Includes timestamp and player counts

4. **`update_projections.py`** (MODIFIED)
   - Now includes `last_updated_timestamp` in cache
   - Unix timestamp for accurate comparison

5. **`templates/index.html`** (MODIFIED)
   - Added notification button
   - Loads notification.js script

6. **`templates/optimizer.html`** (MODIFIED)
   - Loads notification.js for consistency

7. **`static/js/app.js`** (MODIFIED)
   - Integrated notification initialization
   - Button state management

## API Endpoints

### GET `/api/projections/status`

Returns current projection status for notification system.

**Response:**
```json
{
  "success": true,
  "last_updated_timestamp": 1760470178.844,
  "last_updated_display": "October 14, 2025 at 02:29 PM",
  "total_players": 16,
  "projection_count": 48,
  "formats": ["PPR", "HALF_PPR", "STANDARD"]
}
```

## Testing the System

### Method 1: Simulate Update (Recommended for Testing)

1. Start the Flask app:
   ```bash
   python3 app.py
   ```

2. Open the website in your browser
3. Click "Enable Notifications" and grant permission
4. In another terminal, run:
   ```bash
   python3 update_projections.py
   ```

5. Wait up to 5 minutes (or refresh the page to check immediately)
6. You should see:
   - Toast notification slide in
   - Browser notification (if granted permission)
   - Badge showing new player count

### Method 2: Manual Test

To immediately test without waiting:

```javascript
// In browser console:
window.notificationManager.showToast('Test notification!', 'success');
window.notificationManager.showBrowserNotification('Test', 'This is a test');
window.notificationManager.showBadge(5);
```

### Method 3: Clear History and Reload

```javascript
// In browser console:
window.notificationManager.clearHistory();
// Then reload the page - it will treat current data as "new"
```

## Configuration

### Change Check Interval

Default is 5 minutes. To change, edit `static/js/app.js`:

```javascript
// Current (5 minutes):
window.notificationManager.startPeriodicCheck(5);

// Change to 10 minutes:
window.notificationManager.startPeriodicCheck(10);

// Change to 1 minute (for testing):
window.notificationManager.startPeriodicCheck(1);
```

### Disable Auto-Checks

If you want to disable automatic checking:

```javascript
// Comment out this line in app.js:
// window.notificationManager.startPeriodicCheck(5);
```

## Browser Compatibility

- **Chrome/Edge:** Full support ✓
- **Firefox:** Full support ✓
- **Safari:** Partial support (no browser notifications on macOS < 16)
- **Mobile Safari:** Toast notifications only (no push notifications)
- **Opera:** Full support ✓

## Privacy & Data Storage

- **LocalStorage:** Stores last seen timestamp and player count only
- **No Personal Data:** No user information is collected
- **Client-Side Only:** All notification logic runs in the browser
- **No External Services:** No third-party notification services used

## Deployment Notes

### Vercel / Production

The notification system works seamlessly in production because:

1. It uses the existing cache system (no API calls to external services)
2. All notification logic is client-side
3. No backend changes required beyond the new API endpoint
4. Works with the existing `update_projections.py` workflow

### When You Update Projections:

1. Run `python3 update_projections.py` (locally or via CI/CD)
2. The cache file is updated with new timestamp
3. Next time users visit (or within 5 minutes if already on site):
   - They'll automatically see notification
   - Badge shows new player count
   - Browser notification appears (if permitted)

## Troubleshooting

### Notifications Not Showing

1. **Check Browser Permission:**
   ```javascript
   console.log(Notification.permission); // Should be "granted"
   ```

2. **Check If Notification Manager Loaded:**
   ```javascript
   console.log(window.notificationManager); // Should be defined
   ```

3. **Clear History and Test:**
   ```javascript
   window.notificationManager.clearHistory();
   location.reload();
   ```

### Browser Notifications Blocked

- User must manually enable in browser settings
- Chrome: Settings → Privacy & Security → Site Settings → Notifications
- Firefox: Preferences → Privacy & Security → Permissions → Notifications

## Future Enhancements

Potential improvements for future versions:

1. **Email Notifications** - Send email alerts to subscribed users
2. **Discord/Slack Integration** - Post updates to Discord/Slack channels
3. **Webhook Support** - Allow users to configure custom webhooks
4. **Notification History** - Show log of past notifications
5. **Custom Notification Triggers** - Notify for specific players/positions
6. **Service Worker** - Background sync for offline support
7. **Notification Sound** - Optional sound alert
8. **Player-Specific Alerts** - Follow specific players

## Support

If you encounter issues:

1. Check browser console for errors
2. Verify API endpoint is accessible: `/api/projections/status`
3. Ensure cache file has `last_updated_timestamp` field
4. Check that notification.js loaded before app.js

---

**Built with:** Vanilla JavaScript, Flask, Apple Dark Mode Theme
**Version:** 1.0.0
**Last Updated:** October 14, 2025
