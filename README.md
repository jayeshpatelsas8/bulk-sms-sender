# bulk-sms-sender
a small python utility to send bulk sms by controlling google sms app
# Bulk SMS Sender v2.1

originally inspired from : https://github.com/malokhvii-eduard/bulk-sms/blob/master/bulk_sms.py 

**Disclaimer**: This tool is intended for legitimate use cases only. Users are solely responsible for ensuring compliance with local laws, carrier policies, and recipient consent requirements. this tool does not come with any kind of warranty whatsoever , user takes complete responsiblity

Automated SMS sending tool for Google Messages via ADB (Android Debug Bridge). Send messages to multiple recipients efficiently using your Android device.

## Features

- **Bulk SMS Sending**: Send messages to multiple phone numbers automatically
- **Draft Mode**: Save messages as drafts without sending
- **Smart Navigation**: Automatically handles UI navigation with proper back button presses
- **Progress Tracking**: Real-time progress bar with detailed status updates
- **Error Recovery**: Robust error handling with automatic retry mechanisms
- **Conversation Management**: Optional conversation deletion after sending
- **Phone Number Validation**: Automatic formatting and validation of phone numbers
- **Customizable Delays**: Configurable delays between messages to avoid rate limiting

## Requirements

### Hardware & Software
- Android device with USB debugging enabled
- USB cable for device connection
- Computer with Python 3.7+ installed
- Google Messages app installed and set as default SMS app

### Python Dependencies
```
click
phonenumbers
androidviewclient
tqdm
```

### ADB Tools
- ADB (Android Debug Bridge) executable
- Place `adb.exe` in the same directory as the script, or ensure ADB is in your system PATH

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd bulk-sms-sender
   ```

2. **Install Python dependencies**
   ```bash
   pip install click phonenumbers androidviewclient tqdm
   ```

3. **Setup ADB**
   - Download ADB tools from Android SDK
   - Place `adb.exe` in the script directory
   - Or install ADB globally and add to PATH

4. **Enable USB Debugging on Android**
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times to enable Developer Options
   - Go to Settings > Developer Options
   - Enable "USB Debugging"
   - Enable "Stay Awake" (recommended)

5. **Setup Google Messages**
   - Install Google Messages from Play Store
   - Set it as default SMS app
   - Ensure you have sufficient SMS credit/plan

## Usage

### Input Files
Create two text files in the script directory:

**numbers.txt** - Phone numbers (one per line)
```
+1234567890
+9876543210
+15551234567
```

**content.txt** - Message content (first line only)
```
Hello! This is a test message from bulk SMS sender.
```

### Command Line Options

**Basic usage:**
```bash
python bulk_sms1.py
```

**Send as drafts only:**
```bash
python bulk_sms1.py --draft
```

**Send with custom delay and delete conversations:**
```bash
python bulk_sms1.py --delete --delay 10
```

**Target specific device:**
```bash
python bulk_sms1.py --serialno DEVICE_SERIAL_NUMBER
```

### Command Line Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--serialno` | `-s` | Target device serial number | Auto-detect |
| `--draft` | `-d` | Save messages as drafts only | False |
| `--delete` | `-x` | Delete conversations after sending | False |
| `--delay` | `-t` | Delay between messages (seconds) | 5 |

## How It Works

1. **Connect**: Establishes ADB connection to Android device
2. **Launch**: Opens Google Messages app
3. **Process Each Number**:
   - Click "Start chat" button
   - Enter phone number in search field
   - Press Enter to proceed to conversation
   - Select contact suggestion if available
   - Type the message text
   - Send message or save as draft
   - Navigate back to main screen (2 back button presses)
   - Optional: Delete conversation
   - Wait specified delay before next number

## Sample Output

```
============================================================
           BULK SMS SENDER v2.1
      Google Messages Automation via ADB
============================================================

📊 Configuration:
   • Phone numbers found: 5
   • Message: Hello! This is a test message from bulk...
   • Mode: Send messages
   • Delete after: No
   • Delay between messages: 5s
   • Target device: Auto-detect

🔌 Connecting to Android device...
✅ Device connected successfully
📱 Opening Google Messages app...
✅ Messages app launched

🚀 Starting bulk SMS sending process...
------------------------------------------------------------
Processing +1234567890: 100%|██████████| 5/5 [04:23<00:00, 52.8s/it]
------------------------------------------------------------
📈 BULK SMS PROCESS COMPLETED
   • Successfully processed: 5/5 messages
   • Success rate: 100.0%

✅ All done! Check your Messages app for results.
============================================================
```

## Troubleshooting

### Common Issues

**Device not found:**
- Ensure USB debugging is enabled
- Check USB cable connection
- Try different USB port
- Accept ADB debugging prompt on device

**Messages app not opening:**
- Verify Google Messages is installed
- Set Google Messages as default SMS app
- Close other messaging apps

**Script can't find UI elements:**
- Ensure device screen is on and unlocked
- Check if Google Messages UI has changed
- Try updating the script to latest version

**Messages not sending:**
- Verify sufficient SMS credit/plan
- Check network connectivity
- Ensure phone numbers are valid
- Try sending manually first

### Error Recovery

The script includes robust error handling:
- Automatic retries for failed operations
- Navigation recovery on UI errors
- Detailed error logging
- Graceful fallback to hardware keys

## Limitations

- Requires physical device connection via USB
- Works specifically with Google Messages app
- Depends on UI element stability (may break with app updates)
- No support for multimedia messages (MMS)
- Rate limited by carrier SMS restrictions

## Legal Considerations

- Ensure compliance with local SMS/messaging laws
- Respect recipient consent and privacy
- Follow carrier terms of service
- Consider anti-spam regulations
- Use responsibly for legitimate purposes only

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on your device
5. Submit a pull request

## tested on below system on android 12 
OnePlus9:/ $ dumpsys package com.google.android.apps.messaging | grep version
    versionCode=289151063 minSdk=26 targetSdk=36
    versionName=messages.android_20250907_01_RC00.phone_dynamic
    signatures=PackageSignatures{735bbed version:3, signatures:[658fb6d4], past signatures:[]}
    versionCode=118032063 minSdk=21 targetSdk=31
    versionName=messages.android_20220214_00_RC02.phone_dynamic
    signatures=PackageSignatures{8bd1270 version:0, signatures:[], past signatures:[]}


## commands to know UI 

adb shell uiautomator dump
adb pull /sdcard/window_dump.xml

launch app 

adb shell am start -n com.google.android.apps.messaging/.ui.ConversationListActivity

simulate tap 

adb shell input tap 700 300



## Version History

- **v2.1**: Fixed ViewClient method calls, improved navigation reliability
- **v2.0**: Added professional UI, enhanced error handling, progress tracking
- **v1.0**: Initial release with basic bulk SMS functionality

## License

This project is provided as-is for educational and legitimate use cases. Users are responsible for compliance with all applicable laws and regulations.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review the requirements and setup steps
3. Test with a small number of recipients first
4. Open an issue with detailed error logs if needed

---

**Disclaimer**: This tool is intended for legitimate use cases only. Users are solely responsible for ensuring compliance with local laws, carrier policies, and recipient consent requirements.
