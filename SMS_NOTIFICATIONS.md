# SMS Notifications Documentation

## Overview

The Fantasy Football Projections app now includes SMS notifications powered by [Textbelt](https://textbelt.com), a free SMS API service. Users can subscribe to receive text messages when new projections are added.

## Features

### 1. **Phone Number Subscription**
- Users can subscribe with their phone number
- Support for US, Canada, and International numbers
- Phone number validation and formatting
- Confirmation SMS sent upon subscription

### 2. **Automatic Notifications**
- Sends SMS when you run `update_projections.py`
- Includes player count in message
- Formatted to fit within 160 characters

### 3. **Subscriber Management**
- Add/remove subscribers via web UI
- Stored in JSON file (`data/sms_subscribers.json`)
- Track subscription date and region
- Activate/deactivate without deletion

### 4. **Quota Management**
- Checks remaining quota before sending
- Warns if quota insufficient for all subscribers
- Supports both free and paid Textbelt tiers

## How It Works

### For Users

1. **Subscribe:**
   - Click "📱 Get SMS Notifications" button on homepage
   - Enter phone number (e.g., `555-123-4567`)
   - Select region (US/Canada/International)
   - Click "Subscribe"
   - Receive confirmation text

2. **Receive Updates:**
   - Get text when new projections added
   - Message format: "🏈 Fantasy Update: X new player projections added! Total: Y players. Check your app!"

3. **Unsubscribe:**
   - Click SMS button again
   - Click "Unsubscribe"
   - Or reply "STOP" to any message (carrier-handled)

### For Developers

#### Files Structure

```
src/notifications/
├── __init__.py
└── sms_service.py              # SMS service classes

static/js/
└── sms-notifications.js         # Frontend UI

data/
└── sms_subscribers.json         # Subscriber storage (auto-created)
```

#### API Endpoints

1. **POST `/api/sms/subscribe`**
   - Subscribe a phone number
   - Request: `{phone: "5551234567", region: "us"}`
   - Response: `{success: true, message: "...", subscriber_count: 1}`

2. **POST `/api/sms/unsubscribe`**
   - Unsubscribe a phone number
   - Request: `{phone: "5551234567"}`
   - Response: `{success: true, message: "...", subscriber_count: 0}`

3. **GET `/api/sms/status`**
   - Get system status
   - Response: `{success: true, subscriber_count: 5, quota_remaining: 98, is_free_tier: false}`

4. **POST `/api/sms/test`**
   - Test SMS sending (admin only)
   - Request: `{phone: "5551234567"}`
   - Response: `{success: true, message: "...", details: {...}}`

#### Python Classes

**`TextbeltSMSService`**
```python
from src.notifications.sms_service import TextbeltSMSService

# Initialize (uses free tier by default)
sms = TextbeltSMSService()

# Or with paid API key
sms = TextbeltSMSService(api_key="your_textbelt_key")

# Send SMS
result = sms.send_sms("5551234567", "Hello!")
# Returns: {"success": true, "textId": "12345"}

# Check quota
quota = sms.check_quota()
# Returns: 98 (messages remaining)

# Test connection
is_working = sms.test_connection()
# Returns: True/False
```

**`SMSSubscriberManager`**
```python
from src.notifications.sms_service import SMSSubscriberManager

# Initialize
manager = SMSSubscriberManager()

# Add subscriber
added = manager.add_subscriber("5551234567", region="us")

# Get subscribers
subscribers = manager.get_active_subscribers()
# Returns: [{"phone": "5551234567", "region": "us", ...}]

# Remove subscriber
removed = manager.remove_subscriber("5551234567")

# Get count
count = manager.get_subscriber_count()
```

## Usage

### Running Update Script

When you update projections, you'll be prompted to send SMS:

```bash
python3 update_projections.py

# Output:
# ✅ Successfully cached 48 projections
# 📁 Saved to: data/projections_cache.json
# 🕐 Last updated: October 14, 2025 at 02:29 PM
#
# ============================================================
# Send SMS notifications to subscribers? (y/n): y
#
# 📱 Sending SMS notifications...
# 📊 Found 3 active subscriber(s)
# 📝 Message: 🏈 Fantasy Update: Projections updated for 16 players. Check your app!
# ✓ SMS sent to 5551234567
# ✓ SMS sent to 5559876543
# ✓ SMS sent to 5555555555
#
# ✅ SMS notifications sent: 3 successful, 0 failed
```

### Configuration

#### Free Tier (Default)

No configuration needed! Uses Textbelt's free tier:
- 1 free text per day per IP address
- Key: `textbelt`

#### Paid Tier

For reliable, unlimited SMS:

1. Get API key from [textbelt.com](https://textbelt.com)
2. Set environment variable:
   ```bash
   export TEXTBELT_API_KEY="your_api_key_here"
   ```
3. Or add to `.env` file:
   ```
   TEXTBELT_API_KEY=your_api_key_here
   ```

## Textbelt Limits & Pricing

### Free Tier
- **1 text per day** per IP address
- Uses key: `textbelt`
- Good for testing
- Not suitable for multiple subscribers

### Paid Tier
- Purchase SMS credits
- Each key has specific quota
- Check quota: `GET https://textbelt.com/quota/{key}`
- More reliable delivery
- Recommended for production

### Pricing
Visit [textbelt.com](https://textbelt.com) for current pricing.

## Storage

Subscribers are stored in `data/sms_subscribers.json`:

```json
{
  "subscribers": [
    {
      "phone": "5551234567",
      "region": "us",
      "subscribed_at": "2025-10-14T14:30:00.000000",
      "active": true
    }
  ],
  "created": "2025-10-14T14:00:00.000000",
  "last_updated": "2025-10-14T14:30:00.000000"
}
```

**Security Notes:**
- Phone numbers stored in plain text (consider encryption for production)
- File has restricted permissions (only app can access)
- No PII besides phone numbers
- Users can request deletion via unsubscribe

## Testing

### Test SMS System

```bash
# Start the Flask app
python3 app.py

# In another terminal, test the API
curl -X POST http://localhost:5000/api/sms/test \
  -H "Content-Type: application/json" \
  -d '{"phone": "5551234567"}'
```

### Test Subscription Flow

1. Open http://localhost:5000
2. Click "📱 Get SMS Notifications"
3. Enter your phone number
4. Check your phone for confirmation text

### Test Update Notifications

```bash
python3 update_projections.py
# When prompted, enter 'y' to send SMS
# Check your phone for update text
```

## Frontend Integration

The SMS UI is built with vanilla JavaScript:

```javascript
// Show subscription modal
showSMSModal();

// Subscribe programmatically
await smsNotificationUI.subscribe("5551234567", "us");

// Unsubscribe
await smsNotificationUI.unsubscribe("5551234567");

// Check subscription status
const subscription = smsNotificationUI.getStoredSubscription();
// Returns: {phone: "5551234567", region: "us", subscribed_at: "..."}
```

## Troubleshooting

### SMS Not Sending

1. **Check Textbelt Status:**
   ```bash
   curl https://textbelt.com/text \
     -d number=5551234567 \
     -d "message=Test" \
     -d key=textbelt
   ```

2. **Verify Phone Format:**
   - Must be 10 digits (US)
   - No spaces or special characters in storage
   - UI handles formatting automatically

3. **Check Quota:**
   ```bash
   curl https://textbelt.com/quota/your_key
   ```

4. **Free Tier Limits:**
   - Only 1 text per day per IP
   - If you already sent a text today, wait 24 hours
   - Or use paid API key

### Subscription Not Working

1. **Check Console Errors:**
   - Open browser dev tools (F12)
   - Look for errors in Console tab

2. **Verify API Endpoint:**
   ```bash
   curl http://localhost:5000/api/sms/status
   ```

3. **Check Subscriber File:**
   ```bash
   cat data/sms_subscribers.json
   ```

### Messages Not Received

- Carrier delivery not guaranteed
- Some carriers filter automated messages
- Try different phone number/carrier
- Check phone spam/blocked messages
- Textbelt uses carrier-specific gateways (not always reliable)

## Production Deployment

### Recommendations

1. **Use Paid Tier**
   - Free tier insufficient for multiple users
   - More reliable delivery
   - Better support

2. **Add Authentication**
   - Protect `/api/sms/test` endpoint
   - Add rate limiting to prevent abuse
   - Consider CAPTCHA for subscription

3. **Encrypt Phone Numbers**
   - Store encrypted in database
   - Use environment variable for encryption key
   - Decrypt only when sending

4. **Add Rate Limiting**
   - Limit subscription attempts per IP
   - Prevent spam subscriptions
   - Use Flask-Limiter or similar

5. **Monitor Usage**
   - Log all SMS attempts
   - Track success/failure rates
   - Monitor quota consumption
   - Alert on quota running low

6. **Legal Compliance**
   - Add terms of service
   - Include privacy policy
   - Comply with TCPA regulations (US)
   - Provide easy unsubscribe method
   - Store consent timestamp

### Environment Variables

```bash
# .env file
TEXTBELT_API_KEY=your_api_key_here
SMS_ENCRYPTION_KEY=your_encryption_key  # For future use
```

### Example Production Setup

```python
# config/production.py
import os

SMS_CONFIG = {
    'api_key': os.getenv('TEXTBELT_API_KEY'),
    'rate_limit': 10,  # Max subscriptions per hour per IP
    'max_subscribers': 1000,
    'encrypt_storage': True,
    'require_verification': True  # Double opt-in
}
```

## Future Enhancements

Potential improvements:

1. **Double Opt-In** - Require confirmation code
2. **Verification Code** - SMS verification for security
3. **Unsubscribe Link** - Web-based unsubscribe
4. **Message Templates** - Customizable message formats
5. **Scheduling** - Choose notification times
6. **Player Filters** - Only notify for specific players
7. **Database Storage** - Move from JSON to PostgreSQL
8. **Analytics** - Track open rates, delivery rates
9. **Multiple Languages** - i18n support
10. **Webhook Integration** - Alternative to SMS

## Support

### Textbelt Issues
- Documentation: https://github.com/typpo/textbelt
- API Help: https://textbelt.com

### App Issues
- Check logs in terminal where Flask is running
- Verify all files are present
- Test with `curl` commands above

---

**Built with:** Textbelt API, Flask, Vanilla JavaScript
**Version:** 1.0.0
**Last Updated:** October 14, 2025
