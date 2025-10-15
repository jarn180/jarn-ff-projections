"""
SMS Notification Service using Textbelt
Free SMS notifications for projection updates
"""

import requests
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class TextbeltSMSService:
    """Service for sending SMS notifications via Textbelt API."""

    # Textbelt endpoints
    BASE_URL = "https://textbelt.com"
    US_ENDPOINT = f"{BASE_URL}/text"
    CANADA_ENDPOINT = f"{BASE_URL}/canada"
    INTL_ENDPOINT = f"{BASE_URL}/intl"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize SMS service.

        Args:
            api_key: Textbelt API key. If None, uses free tier (1 text/day).
                    Set TEXTBELT_API_KEY env var for paid tier.
        """
        self.api_key = api_key or os.getenv("TEXTBELT_API_KEY", "textbelt")
        self.is_free_tier = self.api_key == "textbelt"

    def send_sms(self, phone_number: str, message: str,
                 region: str = "us") -> Dict:
        """Send SMS to a phone number.

        Args:
            phone_number: Phone number (e.g., "5551234567" or "+15551234567")
            message: Message text (max 160 chars recommended)
            region: Region code ("us", "canada", "intl")

        Returns:
            Dictionary with success status and details
        """
        # Select endpoint based on region
        endpoint = self._get_endpoint(region)

        # Prepare request
        payload = {
            "phone": phone_number,
            "message": message,
            "key": self.api_key
        }

        try:
            response = requests.post(endpoint, data=payload, timeout=10)
            result = response.json()

            # Log the result
            if result.get("success"):
                print(f"✓ SMS sent to {phone_number}")
                if "textId" in result:
                    print(f"  Text ID: {result['textId']}")
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"✗ Failed to send SMS to {phone_number}: {error_msg}")

            return result

        except requests.RequestException as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            print(f"✗ Network error sending SMS: {e}")
            return error_result

    def send_bulk_sms(self, phone_numbers: List[str], message: str,
                     region: str = "us") -> Dict[str, Dict]:
        """Send SMS to multiple phone numbers.

        Args:
            phone_numbers: List of phone numbers
            message: Message text
            region: Region code

        Returns:
            Dictionary mapping phone numbers to their send results
        """
        results = {}

        for phone in phone_numbers:
            result = self.send_sms(phone, message, region)
            results[phone] = result

        return results

    def check_quota(self) -> Optional[int]:
        """Check remaining SMS quota for current API key.

        Returns:
            Number of messages remaining, or None if check failed
        """
        if self.is_free_tier:
            print("ℹ Using free tier (1 text per day per IP)")
            return None

        try:
            url = f"{self.BASE_URL}/quota/{self.api_key}"
            response = requests.get(url, timeout=5)
            data = response.json()

            quota = data.get("quotaRemaining")
            if quota is not None:
                print(f"📊 Quota remaining: {quota} messages")
            return quota

        except Exception as e:
            print(f"✗ Error checking quota: {e}")
            return None

    def test_connection(self) -> bool:
        """Test API connection without using quota.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Use test key to avoid using quota
            test_key = f"{self.api_key}_test" if not self.is_free_tier else "textbelt_test"

            payload = {
                "phone": "5555555555",
                "message": "Test",
                "key": test_key
            }

            response = requests.post(self.US_ENDPOINT, data=payload, timeout=5)
            # Test mode should return success or specific test response
            return response.status_code == 200

        except Exception as e:
            print(f"✗ Connection test failed: {e}")
            return False

    def _get_endpoint(self, region: str) -> str:
        """Get appropriate endpoint for region.

        Args:
            region: Region code

        Returns:
            API endpoint URL
        """
        endpoints = {
            "us": self.US_ENDPOINT,
            "canada": self.CANADA_ENDPOINT,
            "intl": self.INTL_ENDPOINT
        }
        return endpoints.get(region.lower(), self.US_ENDPOINT)

    def format_projection_update_message(self, total_players: int,
                                        new_players: int = 0) -> str:
        """Format a message for projection updates.

        Args:
            total_players: Total number of players with projections
            new_players: Number of new players added

        Returns:
            Formatted SMS message
        """
        if new_players > 0:
            msg = f"🏈 Fantasy Update: {new_players} new player projection"
            msg += "s" if new_players > 1 else ""
            msg += f" added! Total: {total_players} players. Check your app!"
        else:
            msg = f"🏈 Fantasy Update: Projections updated for {total_players} players. Check your app!"

        # Keep under 160 chars for best compatibility
        return msg[:160]


class SMSSubscriberManager:
    """Manage SMS notification subscribers."""

    def __init__(self, storage_file: str = "data/sms_subscribers.json"):
        """Initialize subscriber manager.

        Args:
            storage_file: Path to JSON file storing subscribers
        """
        self.storage_file = storage_file
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)

        if not os.path.exists(self.storage_file):
            self._save_data({
                "subscribers": [],
                "created": datetime.now().isoformat()
            })

    def _load_data(self) -> Dict:
        """Load subscriber data from file."""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading subscribers: {e}")
            return {"subscribers": []}

    def _save_data(self, data: Dict):
        """Save subscriber data to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving subscribers: {e}")

    def add_subscriber(self, phone_number: str, region: str = "us") -> bool:
        """Add a new SMS subscriber.

        Args:
            phone_number: Phone number to add
            region: Region code

        Returns:
            True if added successfully, False if already exists
        """
        data = self._load_data()
        subscribers = data.get("subscribers", [])

        # Check if already subscribed
        if any(sub["phone"] == phone_number for sub in subscribers):
            return False

        # Add new subscriber
        subscribers.append({
            "phone": phone_number,
            "region": region,
            "subscribed_at": datetime.now().isoformat(),
            "active": True
        })

        data["subscribers"] = subscribers
        data["last_updated"] = datetime.now().isoformat()
        self._save_data(data)

        print(f"✓ Added subscriber: {phone_number}")
        return True

    def remove_subscriber(self, phone_number: str) -> bool:
        """Remove a subscriber.

        Args:
            phone_number: Phone number to remove

        Returns:
            True if removed, False if not found
        """
        data = self._load_data()
        subscribers = data.get("subscribers", [])

        initial_count = len(subscribers)
        subscribers = [sub for sub in subscribers if sub["phone"] != phone_number]

        if len(subscribers) < initial_count:
            data["subscribers"] = subscribers
            data["last_updated"] = datetime.now().isoformat()
            self._save_data(data)
            print(f"✓ Removed subscriber: {phone_number}")
            return True

        return False

    def get_active_subscribers(self) -> List[Dict]:
        """Get list of active subscribers.

        Returns:
            List of active subscriber dictionaries
        """
        data = self._load_data()
        subscribers = data.get("subscribers", [])
        return [sub for sub in subscribers if sub.get("active", True)]

    def get_subscriber_count(self) -> int:
        """Get count of active subscribers.

        Returns:
            Number of active subscribers
        """
        return len(self.get_active_subscribers())

    def deactivate_subscriber(self, phone_number: str) -> bool:
        """Deactivate a subscriber without removing them.

        Args:
            phone_number: Phone number to deactivate

        Returns:
            True if deactivated, False if not found
        """
        data = self._load_data()
        subscribers = data.get("subscribers", [])

        for sub in subscribers:
            if sub["phone"] == phone_number:
                sub["active"] = False
                sub["deactivated_at"] = datetime.now().isoformat()
                data["last_updated"] = datetime.now().isoformat()
                self._save_data(data)
                return True

        return False
