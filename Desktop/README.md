# WhatsApp Desktop Automator

A Windows desktop application for automating WhatsApp Desktop messaging built with C# and Windows Application Driver.

## Features

- **Bulk Messaging**: Send personalized messages to multiple contacts from Excel files
- **Message Templates**: Compose messages with line breaks and multiple paragraphs
- **Phone Number Validation**: Automatic phone number formatting and validation
- **Image Attachments**: Send images along with your messages (prepend or append)
- **Excel Import**: Load contact lists from Excel files (.xlsx, .xls)
- **Smart Phone Detection**: Auto-detect phone number columns in Excel
- **Real-time Logging**: Monitor sending progress with detailed logs
- **WhatsApp Detection**: Automatically finds WhatsApp installation (Store or standalone)

## Prerequisites

- Windows 10/11
- WhatsApp Desktop (Microsoft Store or standalone version)
- .NET Framework 4.7.2 or higher
- Windows Application Driver (WinAppDriver)

## Installation

### 1. Install Windows Application Driver

Download and install WinAppDriver from:
https://github.com/Microsoft/WinAppDriver/releases

Default installation path: `C:\Program Files (x86)\Windows Application Driver\`

### 2. Enable Developer Mode

1. Open Windows Settings
2. Go to Update & Security → For developers
3. Enable "Developer Mode"

### 3. Install WhatsApp Desktop

Install WhatsApp Desktop from either:
- Microsoft Store (recommended)
- Direct download from https://www.whatsapp.com/download

### 4. Run the Application

1. Download the latest release from the releases page
2. Extract the files
3. Run `WhatsAppAutomator.exe`

## Usage

### Loading Contacts

1. Click "Load Excel" button
2. Select your Excel file containing phone numbers
3. The application will auto-detect the phone number column

### Excel Format Requirements

Your Excel file should have a column containing phone numbers. The column can be named:
- phone
- mobile
- cell
- whatsapp
- number
- contact

Phone numbers should include country code (e.g., +1234567890)

### Composing Messages

**Single Paragraph Message:**
```
Hello! This is a test message.
```

**Multiple Line Message (single bubble):**
```
Hello!
This is line 1
This is line 2
```

**Multiple Separate Messages:**
Use double line breaks to send as separate message bubbles:
```
First message bubble


Second message bubble


Third message bubble
```

### Sending Messages

1. Load your contact list
2. Type your message in the message box
3. Optionally select an image to attach
4. Choose image position (prepend or append)
5. Click "Start" to begin sending

### Message Formatting Tips

- Single line break: Message appears in same bubble with line break
- Double line break: Creates separate message bubbles
- The application automatically handles special characters and emojis

## Technical Details

### Architecture

- **Language**: C# (.NET Framework 4.7.2)
- **UI Framework**: Windows Forms
- **Automation**: Selenium WebDriver with Appium
- **Driver**: Windows Application Driver (WinAppDriver)
- **Excel Reading**: ExcelDataReader library

### How It Works

1. **WhatsApp Detection**: Automatically locates WhatsApp installation
   - Checks `%LocalAppData%\WhatsApp\app-*\`
   - Checks Windows Store apps location
   - Falls back to manual selection if needed

2. **Automation Process**:
   - Launches WinAppDriver service
   - Connects to WhatsApp Desktop via UI Automation
   - Uses accessibility IDs to interact with UI elements
   - Sends messages through the native Windows app

3. **Phone Number Processing**:
   - Validates international format
   - Strips spaces and formatting
   - Adds country code if configured

## Project Structure

```
Desktop/
├── MainForm.cs              # Main application UI and logic
├── MainForm.Designer.cs     # Windows Forms designer code
├── WhatsAppHelper.cs        # WhatsApp detection and helper functions
├── Program.cs               # Application entry point
├── App.config              # Application configuration
└── WhatsAppAutomator.csproj # Project file
```

## Building from Source

### Requirements

- Visual Studio 2019 or later
- .NET Framework 4.7.2 SDK

### Build Steps

1. Clone the repository
2. Open `WhatsAppAutomator.sln` in Visual Studio
3. Restore NuGet packages
4. Build the solution (F6)
5. Run the application (F5)

### Dependencies (NuGet Packages)

- Appium.WebDriver (8.0.0)
- ExcelDataReader (3.7.0)
- ExcelDataReader.DataSet (3.7.0)
- Microsoft.WinAppDriver.Appium.WebDriver (1.0.1-Preview)
- Selenium.WebDriver (3.11.2)

## Troubleshooting

### WinAppDriver not starting
- Ensure Developer Mode is enabled
- Check if WinAppDriver is installed in the correct location
- Try running WinAppDriver.exe manually

### WhatsApp not found
- Make sure WhatsApp Desktop is installed
- Try selecting the WhatsApp.exe manually when prompted
- Check if WhatsApp is up to date

### Messages not sending
- Ensure WhatsApp is logged in
- Check phone number format (include country code)
- Verify the contact exists on WhatsApp
- Check the application logs for specific errors

### Excel file not loading
- Ensure the file is a valid .xlsx or .xls format
- Check that the file is not open in another program
- Verify phone numbers are in a recognizable column

## Limitations

- Requires WhatsApp Desktop to be installed (not WhatsApp Web)
- Windows only (uses Windows Application Driver)
- Cannot send messages if WhatsApp requires phone verification
- Rate limiting may apply for bulk messages

## Safety and Compliance

⚠️ **Important:**
- This tool automates the official WhatsApp Desktop application
- Use responsibly and in accordance with WhatsApp's Terms of Service
- Avoid sending spam or unsolicited messages
- Implement reasonable delays between messages
- Always obtain consent before sending automated messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is not affiliated with WhatsApp or Meta. Use at your own risk and responsibility. The developers are not responsible for any account restrictions or bans that may occur from using this tool.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.