# Email Classification and Reply System

## Overview

This project is a Flask web application that integrates with Gmail and Google’s generative AI to classify and generate replies to emails. The application allows users to fetch emails from their Gmail account, classify them into categories, and generate automated replies using Google's AI model.

## Features

- **Authenticate with Gmail**: Securely authenticate and access Gmail using OAuth 2.0.
- **Fetch Emails**: Retrieve emails from the Gmail inbox.
- **Classify Emails**: Use Google's AI model to classify emails into categories (Interested, Not Interested, More Information).
- **Generate Replies**: Automatically generate email replies based on the classification.
- **Send Replies**: Send generated replies back through Gmail.

## Installation

### Prerequisites

- Python 3.8 or higher
- Pip (Python package installer)

### Clone the Repository

```bash
git clone https://github.com/bhumikabiyani/reachinbox_assignment.git
```

### Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Configuration

1. **Create a `.env` file** in the root directory of your project and add the following lines with your own values:

   ```plaintext
   API_KEY=your_google_api_key
   ```

2. **Google OAuth Credentials**: Obtain OAuth 2.0 credentials from the [Google Developer Console](https://console.developers.google.com/) and save them in `env/credentials.json`.

### Running the Application

1. **Start the Flask Development Server**:

   ```bash
   python app.py
   ```

2. **Access the Application**:

 

## Usage

1. **Fetch Emails**: The home page displays a list of emails fetched from your Gmail inbox.
2. **Classify Emails**: Submit an email snippet to classify it using the AI model.
3. **Generate and Send Replies**: Generate a reply based on the classification and send it back through Gmail.


## Troubleshooting

- **Authentication Issues**: Ensure that `credentials.json` is correctly configured and OAuth 2.0 credentials are valid.

