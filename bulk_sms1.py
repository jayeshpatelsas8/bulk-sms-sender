#!/usr/bin/env python3
"""
Bulk SMS Sender for Google Messages via ADB

This script automates sending SMS messages to multiple recipients using the Google Messages
app on Android devices through ADB (Android Debug Bridge). It provides functionality to
send individual messages, save as drafts, and optionally delete conversations after sending.

Author: SMS Automation Tool
Version: 2.1
Requirements:
    - Android device with USB debugging enabled
    - Google Messages app installed and set as default SMS app
    - ADB tools available in PATH or in script directory
    - Python packages: click, phonenumbers, androidviewclient, tqdm

Usage:
    python bulk_sms1.py                    # Send to all numbers with default settings
    python bulk_sms1.py --draft            # Save messages as drafts only
    python bulk_sms1.py --delete --delay 5 # Send and delete conversations with 5s delay
    python bulk_sms1.py -s DEVICE_SERIAL   # Target specific device

Input Files:
    - numbers.txt: Phone numbers (one per line, any format)
    - content.txt: Message content (first line only)
"""

import sys
import os
from enum import IntEnum
from typing import List, Optional
import time

import click
import phonenumbers
from com.dtmilano.android.viewclient import ViewClient
from tqdm import tqdm

# Path to adb in same folder as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ADB_PATH = os.path.join(SCRIPT_DIR, "adb")

MESSAGES_PACKAGE = "com.google.android.apps.messaging"
CONFIRM_ID = "android:id/button1"
DELETE_CHAT_ID = f"{MESSAGES_PACKAGE}:id/action_delete"
LAST_CHAT_ID = f"{MESSAGES_PACKAGE}:id/swipeableContainer"

# Updated IDs based on the XML dumps
START_CHAT_ID = f"{MESSAGES_PACKAGE}:id/start_chat_fab"  # Start chat button
CONTACT_SEARCH_FIELD = "ContactSearchField"  # Text input field for recipient
COMPOSE_DRAFT_SEND_ID = "Compose:Draft:Send"  # Send button (voice record when no text)

# Alternative selectors for reliability
CONTACT_SUGGESTION_SELECTOR = "ContactSuggestionList"
MESSAGE_TEXT_ID = "message_text"


class Key(IntEnum):
    Back = 4
    Enter = 66
    Paste = 279


def get_phone_numbers(file_path="numbers.txt") -> List[str]:
    phone_numbers = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in map(str.strip, f):
                if not line:
                    continue
                try:
                    phone_numbers.add(
                        phonenumbers.format_number(
                            phonenumbers.parse(line, None),
                            phonenumbers.PhoneNumberFormat.E164,
                        )
                    )
                except phonenumbers.NumberParseException:
                    pass
    except FileNotFoundError:
        click.echo(f"Oops, file not found: {file_path}", err=True)
        sys.exit(1)

    if not phone_numbers:
        click.echo("Oops, no valid phone numbers!", err=True)
        sys.exit(2)

    return list(sorted(phone_numbers))


def get_message(file_path="content.txt") -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if not line:
                click.echo("Content file is empty!", err=True)
                sys.exit(3)
            return line
    except FileNotFoundError:
        click.echo(f"Oops, file not found: {file_path}", err=True)
        sys.exit(1)


def open_messages(view: ViewClient):
    """Open Messages app using activity manager"""
    view.device.shell(f"am start -n {MESSAGES_PACKAGE}/.ui.ConversationListActivity")
    time.sleep(3)  # Wait for app to load


def go_back_to_main_screen(view: ViewClient):
    """Navigate back to main Messages screen using the back button (requires 2 presses)"""
    try:
        print("Navigating back to main screen...")

        # First back button press - from conversation to conversation list
        view.dump()
        back_elements = view.findViewsWithContentDescriptionRe("Back")

        if back_elements:
            print("First back button press...")
            back_elements[0].touch()
            time.sleep(2)
        else:
            print("Using hardware back key (first press)...")
            view.device.shell("input keyevent KEYCODE_BACK")
            time.sleep(2)

        # Second back button press - from conversation list to main Messages screen
        view.dump()
        back_elements = view.findViewsWithContentDescriptionRe("Back")

        if back_elements:
            print("Second back button press...")
            back_elements[0].touch()
            time.sleep(2)
        else:
            print("Using hardware back key (second press)...")
            view.device.shell("input keyevent KEYCODE_BACK")
            time.sleep(2)

        # Verify we're back at main screen by checking for Start Chat button
        view.dump()
        start_chat = view.findViewById(START_CHAT_ID)
        if not start_chat:
            start_chat_elements = view.findViewsContainingText("Start chat")
            if start_chat_elements:
                start_chat = start_chat_elements[0]

        if start_chat:
            print("Successfully returned to main Messages screen")
            return True
        else:
            print("Warning: May not be at main screen yet")
            return False

    except Exception as e:
        print(f"Error navigating back: {str(e)}")
        # Final fallback - use hardware back keys
        print("Fallback: Using hardware back keys...")
        view.device.shell("input keyevent KEYCODE_BACK")
        time.sleep(2)
        view.device.shell("input keyevent KEYCODE_BACK")
        time.sleep(2)
        return False


def send_sms(view: ViewClient, phone_number: str, message: str, draft: bool = False):
    """Send SMS to a phone number"""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Ensure we're on the main Messages screen first
            view.dump()

            # Find and click Start Chat button
            start_chat = view.findViewById(START_CHAT_ID)
            if not start_chat:
                # Try alternative method - look for "Start chat" text
                start_chat_elements = view.findViewsContainingText("Start chat")
                if start_chat_elements:
                    start_chat = start_chat_elements[0]
                else:
                    print(f"Could not find Start Chat button (attempt {attempt + 1}/{max_retries}). Retrying...")
                    time.sleep(2)
                    continue

            print(f"Starting new chat...")
            start_chat.touch()
            time.sleep(3)  # Wait for new chat screen to load

            # Wait for new chat screen to load and find contact search field
            view.dump()
            contact_field = view.findViewById(CONTACT_SEARCH_FIELD)
            if not contact_field:
                print(f"Could not find contact search field (attempt {attempt + 1}/{max_retries}). Retrying...")
                time.sleep(2)
                continue

            # Enter phone number
            print(f"Entering phone number: {phone_number}")
            contact_field.touch()
            time.sleep(1)

            # Clear any existing text and enter phone number
            view.device.shell("input keyevent KEYCODE_CTRL_A")  # Select all
            time.sleep(0.5)
            view.device.shell(f"input text '{phone_number.replace('+', '')}'")  # Remove + for input
            time.sleep(3)  # Wait for suggestions to appear

            # Press Enter to proceed to conversation after typing number
            print("Pressing Enter to proceed to conversation...")
            view.device.shell("input keyevent KEYCODE_ENTER")
            time.sleep(3)  # Wait for conversation screen to load

            # Look for contact suggestion and tap it if it appears
            view.dump()
            suggestion_list = view.findViewById(CONTACT_SUGGESTION_SELECTOR)
            if suggestion_list:
                # Find clickable contact suggestion
                suggestions = view.findViewsWithAttribute('clickable', True)
                for suggestion in suggestions:
                    if suggestion.getText() and (
                        phone_number[-10:] in suggestion.getText() or "Send to" in suggestion.getText()):
                        print(f"Found contact suggestion, selecting...")
                        suggestion.touch()
                        time.sleep(3)
                        break
                else:
                    # If no matching suggestion found, press Enter again
                    view.device.shell("input keyevent KEYCODE_ENTER")
                    time.sleep(3)

            # Now we should be in the conversation screen
            # Wait for the conversation interface to fully load
            time.sleep(2)
            view.dump()

            # Type the message - the text field should now be active
            print(f"Typing message: {message}")
            view.device.shell(f"input text '{message}'")
            time.sleep(2)

            if not draft:
                # After typing text, the send button should appear
                print("Looking for send button...")
                view.dump()
                send_button = view.findViewById(COMPOSE_DRAFT_SEND_ID)

                if send_button:
                    print("Sending message via button...")
                    send_button.touch()
                else:
                    # Fallback: press Enter to send
                    print("Fallback: pressing Enter to send...")
                    view.device.shell("input keyevent KEYCODE_ENTER")

                time.sleep(3)  # Wait for message to send
                print("Message sent successfully")
            else:
                print("Message saved as draft")

            return True

        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print("Retrying after error...")
                time.sleep(2)
                # Try to get back to main screen for retry
                for _ in range(3):
                    view.device.shell("input keyevent KEYCODE_BACK")
                    time.sleep(1)
                time.sleep(2)
            continue

    raise RuntimeError(f"Failed to send SMS to {phone_number} after {max_retries} attempts")


def delete_last_sms(view: ViewClient):
    """Delete the most recent SMS conversation"""
    try:
        view.dump()

        # Find the first conversation in the list
        last_chat = view.findViewById(LAST_CHAT_ID)
        if not last_chat:
            print("⚠️ Could not find conversation to delete")
            return

        # Long press on the conversation
        coords = last_chat.getXY()
        view.device.drag(coords, coords, duration=1000, steps=1)
        time.sleep(2)

        # Look for delete action
        view.dump()
        delete_button = view.findViewById(DELETE_CHAT_ID)
        if delete_button:
            delete_button.touch()
            time.sleep(1)

            # Confirm deletion
            view.dump()
            confirm_button = view.findViewById(CONFIRM_ID)
            if confirm_button:
                confirm_button.touch()
                time.sleep(2)
                print("🗑️ Conversation deleted")
            else:
                print("⚠️ Could not find delete confirmation")
        else:
            print("⚠️ Could not find delete button")

    except Exception as e:
        print(f"❌ Error deleting conversation: {str(e)}")


@click.command()
@click.option("--serialno", "-s", help="The device or emulator serial number.")
@click.option("--draft", "-d", is_flag=True, help="Save SMS as Draft.")
@click.option("--delete", "-x", is_flag=True, help="Delete SMS after sending.")
@click.option("--delay", "-t", default=5, help="Delay between messages in seconds.")
def main(serialno: Optional[str], draft: bool, delete: bool, delay: int):
    """
    A tool to send bulk SMS messages using Google Messages app via ADB.

    Requirements:
    - Android device with USB debugging enabled
    - Google Messages app installed and set as default SMS app
    - numbers.txt file with phone numbers (one per line)
    - content.txt file with message content (first line only)

    The script will:
    1. Open Google Messages app
    2. For each number, create new conversation
    3. Send the message (or save as draft)
    4. Navigate back to main screen
    5. Optionally delete the conversation
    6. Repeat for next number
    """

    # Display header
    print("=" * 60)
    print("           BULK SMS SENDER v2.1")
    print("      Google Messages Automation via ADB")
    print("=" * 60)
    print()

    phone_numbers = get_phone_numbers()
    message = get_message()

    print(f"📊 Configuration:")
    print(f"   • Phone numbers found: {len(phone_numbers)}")
    print(f"   • Message: {message[:50]}{'...' if len(message) > 50 else ''}")
    print(f"   • Mode: {'Draft only' if draft else 'Send messages'}")
    print(f"   • Delete after: {'Yes' if delete else 'No'}")
    print(f"   • Delay between messages: {delay}s")
    print(f"   • Target device: {serialno if serialno else 'Auto-detect'}")
    print()

    # Force ViewClient to use adb in same directory
    os.environ["ANDROID_VIEW_CLIENT_ADB"] = ADB_PATH

    try:
        # Connect to device
        print("🔌 Connecting to Android device...")
        view = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serialno))
        print("✅ Device connected successfully")

        # Open Messages app
        print("📱 Opening Google Messages app...")
        open_messages(view)
        print("✅ Messages app launched")

        print()
        print("🚀 Starting bulk SMS sending process...")
        print("-" * 60)

        # Process each phone number with progress bar
        phone_numbers = tqdm(phone_numbers, desc="Sending SMS")
        success_count = 0

        for i, phone_number in enumerate(phone_numbers):
            phone_numbers.set_description(f"Processing {phone_number}")

            try:
                send_sms(view, phone_number, message, draft)
                success_count += 1

                # Always go back to main screen after sending/drafting message
                print("Returning to main Messages screen...")
                go_back_to_main_screen(view)

                if delete:
                    print("Deleting conversation...")
                    delete_last_sms(view)

                # Add delay between messages (except for last one)
                if i < len(phone_numbers) - 1:
                    print(f"Waiting {delay} seconds before next message...")
                    time.sleep(delay)

            except Exception as e:
                print(f"Failed to send to {phone_number}: {str(e)}")
                # Try to recover by going back to main screen
                print("Attempting to recover to main screen...")
                go_back_to_main_screen(view)
                time.sleep(1)

        print("-" * 60)
        print(f"📈 BULK SMS PROCESS COMPLETED")
        print(f"   • Successfully processed: {success_count}/{len(phone_numbers)} messages")
        print(f"   • Success rate: {(success_count / len(phone_numbers) * 100):.1f}%")
        if success_count < len(phone_numbers):
            print(f"   • Failed messages: {len(phone_numbers) - success_count}")
        print()
        print("✅ All done! Check your Messages app for results.")
        print("=" * 60)

    except Exception as e:
        print(f"💥 Critical error: {str(e)}")
        print("❌ Bulk SMS process terminated unexpectedly")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
