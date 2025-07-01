# Google Gemini AI API Key Setup Guide

## To Enable Full AI-Powered Analysis

### Step 1: Get Your Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the new API key (starts with `AIza`)

### Step 2: Configure Your API Key

**Option A: Using Environment Variable (Recommended)**
1. Create a `.env` file in the project root directory
2. Add this line to the `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Replace `your_actual_api_key_here` with your actual Gemini API key

**Option B: Direct Code Update**
1. Open `agents.py`
2. Find the line: `GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")`
3. Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key

### Step 3: Restart the Application
1. Stop the current backend server (Ctrl+C)
2. Start the backend server again:
   ```bash
   cd debug-assignment/blood-test-analyser-debug
   python main_optimized.py
   ```

### Step 4: Test the Integration
1. Upload a blood test report
2. Try the analysis feature
3. You should now see full AI-powered analysis instead of fallback messages

## Benefits of Using Gemini AI

✅ **Free Tier Available** - Generous free usage limits  
✅ **High Quality Analysis** - Advanced medical knowledge  
✅ **Fast Processing** - Quick response times  
✅ **Reliable Service** - Google's infrastructure  

## Troubleshooting

**If you see fallback analysis:**
- Check that your API key is correctly set
- Verify the API key is valid in Google AI Studio
- Ensure the `.env` file is in the correct location
- Restart the backend server after making changes

**If you get API errors:**
- Check your usage limits in Google AI Studio
- Verify your account has access to Gemini API
- Try regenerating the API key if needed

## Alternative: OpenAI Setup (Previous Method)

If you prefer to use OpenAI instead:

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable: `OPENAI_API_KEY=your_openai_key_here`
3. Update `agents.py` to use OpenAI instead of Gemini

## Support

For issues with:
- **Gemini API**: Check [Google AI Studio Documentation](https://ai.google.dev/docs)
- **Application**: Check the console logs for error messages
- **Setup**: Ensure all environment variables are correctly configured 