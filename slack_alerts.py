import requests
import os
from datetime import datetime

# Get Slack webhook URL from environment variable
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

def send_slack_alert(message, channel="#aws-cost-alerts"):
    """
    Send a message to Slack using webhook.
    
    Args:
        message (str): The message to send
        channel (str): The Slack channel to send to (default: #aws-cost-alerts)
    """
    if not SLACK_WEBHOOK_URL:
        print("Warning: SLACK_WEBHOOK_URL environment variable not set. Skipping Slack notification.")
        return False
    
    try:
        # Format the message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"*AWS Cost Analysis Report*\nTime: {timestamp}\n\n{message}"
        
        # Prepare the payload
        payload = {
            "channel": channel,
            "text": formatted_message,
            "username": "AWS Cost Analyzer",
            "icon_emoji": ":money_with_wings:",
            "parse": "full"
        }
        
        # Send the message
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        print("Successfully sent notification to Slack")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack notification: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the Slack integration
    test_message = "This is a test message from AWS Cost Analyzer"
    send_slack_alert(test_message)
