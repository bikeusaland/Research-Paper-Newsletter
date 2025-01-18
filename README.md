# Quant Newsletter Generator

A Python application that fetches, summarizes, and emails daily ArXiv papers. The application is designed to run as a Google Cloud Function triggered by Cloud Scheduler, or run locally.

## Prerequisites

1. Google Cloud Platform Account
   - Create an account at https://console.cloud.google.com
   - Create a new project or select an existing one
   - Enable billing for your project

2. Required Google Cloud APIs
   - Cloud Functions API
   - Cloud Scheduler API
   - Cloud Build API

3. Gmail Account - REQUIRED FOR EMAIL SENDING VIA GMAIL
   - Enable 2-Step Verification at https://myaccount.google.com/security
   - Generate an App Password:
     1. Go to Google Account settings
     2. Navigate to Security
     3. Under "2-Step Verification", click on "App passwords"
     4. Select "Mail" for app and your device type
     5. Click "Generate" and save the 16-character password

4. Local Development Setup
   - Python 3.12 or later
   - Git (for version control)
   - Google Cloud CLI (optional, for command-line deployment)

## Project Structure

```
Research-Paper-Newsletter/
├── main.py                 # Cloud Function entry point
├── createEmailSummary.py   # HTML email template generator
├── createSummaries.py      # Paper summary generator
├── getPapers.py           # ArXiv paper fetcher
└── requirements.txt       # Python dependencies
```

## Local Testing

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd QuantNewsletter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the template env file
   cp .env.template .env
   
   # Edit .env with your credentials
   # NEVER commit the .env file to version control
   ```

4. Run the script:
   ```bash
   python main.py
   ```

## Google Cloud Deployment

1. **Create Cloud Function**
   - Go to Google Cloud Console > Cloud Functions
   - Click "Create Function"
   - Configure basic settings:
     * Name: `research-paper-newsletter`
     * Region: Choose nearest region
     * Runtime: Python 3.12
     * Entry point: `cloud_function`
     * Memory: 256 MB (adjust if needed)
     * Timeout: 60 seconds (adjust if needed)

2. **Set Environment Variables**
   - In the Cloud Function configuration, add these environment variables:
     ```
     SENDER_EMAIL=your-gmail@gmail.com
     SENDER_PASSWORD=your-gmail-app-password
     RECEIVER_EMAIL=recipient@example.com
     ARXIV_URL=https://arxiv.org/list/cs.AI/new
     ```

3. **Deploy Code**
   - Option 1: Console Upload
     * Zip all project files
     * Upload via Cloud Console
   - Option 2: Cloud Source Repository
     * Connect your git repository
     * Deploy directly from source
   - Option 3: Command Line (with Google Cloud CLI)
     ```bash
     gcloud functions deploy quant-newsletter \
       --runtime python312 \
       --trigger-http \
       --entry-point cloud_function \
       --region [your-region]
     ```

4. **Set Up Cloud Scheduler**
   - Go to Google Cloud Console > Cloud Scheduler
   - Click "Create Job"
   - Configure job:
     * Name: `trigger-paper-newsletter`
     * Frequency: `0 8 * * *` (runs at 8 AM daily)
     * Timezone: Your preferred timezone
     * Target type: HTTP
     * URL: [Your Cloud Function's trigger URL]
     * HTTP method: POST
     * Auth header: Add if you enabled authentication

## Troubleshooting

1. **Email Issues**
   - Verify Gmail App Password is correct
   - Check if 2-Step Verification is enabled
   - Review Cloud Function logs for SMTP errors

2. **Cloud Function Errors**
   - Check function logs in Cloud Console
   - Verify environment variables are set
   - Ensure all dependencies are in requirements.txt

3. **Scheduler Issues**
   - Verify cron syntax
   - Check scheduler logs
   - Ensure function URL is correct

## Security Notes

- Never commit sensitive information (passwords, API keys) to version control
- The .gitignore file is configured to prevent committing sensitive files
- Use .env file locally for environment variables (copy from .env.template)
- For production:
  - Use Google Cloud Secret Manager to store sensitive data
  - Regularly rotate credentials (Gmail App Password, API keys)
  - Monitor Cloud Function logs for unauthorized access attempts
  - Consider implementing rate limiting
  - Use minimum required permissions for service accounts
- Security best practices:
  - Don't share or expose your Gmail App Password
  - Don't share or expose your OpenAI API key
  - Keep your Python dependencies updated for security patches
  - Review Cloud Function security settings (e.g., HTTPS only)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
