# Research Paper Newsletter Generator

A Python application that fetches, summarizes, and emails daily ArXiv papers using various LLM backends. The application can run locally or as a Google Cloud Function triggered by Cloud Scheduler.

## Features

- Fetches latest papers from ArXiv
- Supports multiple LLM backends for paper summarization:
  - OpenAI (default)
  - Local LM Studio
  - Ollama
  - FuelIX
- Generates HTML email summaries
- Supports local PDF processing
- Debug mode for detailed logging

## Prerequisites

1. Gmail Account (Required for email sending)
   - Enable 2-Step Verification at https://myaccount.google.com/security
   - Generate an App Password:
     1. Go to Google Account settings
     2. Navigate to Security
     3. Under "2-Step Verification", click on "App passwords"
     4. Select "Mail" for app and your device type
     5. Click "Generate" and save the 16-character password

2. LLM Backend (Choose at least one)
   - OpenAI API key (default option)
   - Local LM Studio installation
   - Ollama installation
   - FuelIX API key

3. Local Development Setup
   - Python 3.12 or later
   - Git (for version control)
   - Google Cloud CLI (optional, for cloud deployment)

## Project Structure

```
Research-Paper-Newsletter/
├── main.py                # Main script and Cloud Function entry point
├── createEmailSummary.py  # HTML email template generator
├── createSummaries.py     # Paper summary generator with LLM support
├── getPapers.py          # ArXiv paper fetcher
├── requirements.txt      # Python dependencies
├── .env.template        # Environment variables template
└── README.md           # This file
```

## Command Line Arguments

```bash
python main.py [options]

Options:
  --pdfs PATH     Path to folder containing PDF files to process (if using local PDF's)
  --papers PATH   Override default papers directory for downloads (default: papers)
  --output PATH   Path for the output HTML summary (default: finalSummary.html)
  --llm BACKEND   Choose LLM backend: local, fuelix, openai, or ollama (default: openai)
  --debug         Enable debug logging
```

## Local Setup and Usage

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd Research-Paper-Newsletter
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
   # See .env.template for all available options
   ```

4. Run the script:
   ```bash
   # Basic usage (uses OpenAI by default)
   python main.py

   # Process local PDFs
   python main.py --pdfs /path/to/pdfs

   # Use different LLM backend
   python main.py --llm ollama

   # Enable debug logging
   python main.py --debug
   ```

## Cloud Deployment

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
   - In the Cloud Function configuration, add required variables from .env.template
   - At minimum, you need:
     ```
     SENDER_EMAIL=your-gmail@gmail.com
     SENDER_PASSWORD=your-gmail-app-password
     RECEIVER_EMAIL=recipient@example.com
     OPENAI_API_KEY=your-openai-api-key  # If using OpenAI (default)
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
     gcloud functions deploy research-paper-newsletter \
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

## Troubleshooting

1. **LLM Backend Issues**
   - OpenAI:
     * Verify API key is correct
     * Check API usage limits
   - Local LM Studio:
     * Ensure LM Studio is running
     * Verify API URL is correct
   - Ollama:
     * Ensure Ollama is running
     * Check if model is installed
   - FuelIX:
     * Verify API key is correct
     * Check API endpoint URL

2. **Email Issues**
   - Verify Gmail App Password is correct
   - Check if 2-Step Verification is enabled
   - Review logs for SMTP errors

3. **Cloud Function Errors**
   - Check function logs in Cloud Console
   - Verify environment variables are set
   - Ensure all dependencies are in requirements.txt

4. **Debug Mode**
   - Run with --debug flag for detailed logs:
     ```bash
     python main.py --debug
     ```
   - Check logs for API responses and error messages
   - Verify environment variables are set correctly

5. **Scheduler Issues**
   - Verify cron syntax
   - Check scheduler logs
   - Ensure function URL is correct

## Security Notes

- Never commit sensitive information (API keys, passwords) to version control
- Use .env file locally for environment variables
- For production:
  - Use Google Cloud Secret Manager for sensitive data
  - Regularly rotate credentials
  - Monitor logs for unauthorized access
  - Keep dependencies updated
  - Use HTTPS endpoints only
- Security best practices:
  - Don't share API keys or passwords
  - Use minimum required permissions
  - Implement rate limiting where possible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests if applicable
5. Create a Pull Request

## License

MIT License - See LICENSE file for details
