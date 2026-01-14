# Maileroo API Setup

## Configuration

Your code now uses Maileroo API instead of SMTP. This works on all platforms including PythonAnywhere, Render, and Deta!

## Environment Variables

Set these environment variables:

```bash
MAILEROO_API_KEY=your-maileroo-api-key
MAILEROO_FROM_EMAIL=your-verified-email@yourdomain.com
MAILEROO_FROM_NAME=Discord Bot  # Optional, defaults to "Discord Bot"
MAILEROO_TO_EMAIL=recipient@example.com
MAILEROO_API_URL=https://smtp.maileroo.com/api/v2/emails  # Optional, defaults to this
```

## Getting Your Maileroo API Key

1. **Sign up for Maileroo:**
   - Visit https://maileroo.com
   - Create an account

2. **Get API Key:**
   - Go to your Maileroo dashboard
   - Navigate to API settings
   - Generate a new API key
   - Copy the API key

3. **Verify Your Domain:**
   - Add and verify your domain in Maileroo dashboard
   - The `MAILEROO_FROM_EMAIL` must be from a verified domain (e.g., `bot@yourdomain.com`)

## Setting Environment Variables

### On PythonAnywhere:
1. Go to **Web** tab
2. Click on your web app
3. Scroll to **Environment variables**
4. Add:
   - `MAILEROO_API_KEY`
   - `MAILEROO_FROM_EMAIL` (must be from verified domain)
   - `MAILEROO_TO_EMAIL`
   - `MAILEROO_FROM_NAME` (optional)

### On Render:
1. Go to your service settings
2. Navigate to **Environment**
3. Add the variables

### On Deta:
```bash
deta update -e '{"MAILEROO_API_KEY":"your-key","MAILEROO_FROM_EMAIL":"bot@yourdomain.com","MAILEROO_TO_EMAIL":"recipient@example.com"}'
```

### Local Development (.env file):
```env
MAILEROO_API_KEY=your-api-key-here
MAILEROO_FROM_EMAIL=bot@yourdomain.com
MAILEROO_FROM_NAME=Discord Bot
MAILEROO_TO_EMAIL=recipient@example.com
```

## API Endpoint

The code uses the Maileroo API endpoint:
- Default: `https://smtp.maileroo.com/api/v2/emails`
- Custom: Set `MAILEROO_API_URL` environment variable if needed

## Testing

After setting up, test by sending a message in your Discord server. You should see:
- Console log: "Email sent successfully via Maileroo. Reference ID: [reference_id]"
- Email in your inbox

## Benefits Over SMTP

✅ Works on all platforms (no SMTP blocking)
✅ More reliable delivery
✅ Better error handling
✅ No port/firewall issues
✅ Works on free tiers

## Troubleshooting

**Error: "Maileroo API credentials not found"**
- Check that all required environment variables are set (`MAILEROO_API_KEY`, `MAILEROO_FROM_EMAIL`, `MAILEROO_TO_EMAIL`)
- Verify variable names are correct (case-sensitive)
- Ensure `MAILEROO_FROM_EMAIL` is from a verified domain in your Maileroo account

**Error: "401 Unauthorized"**
- Check your API key is correct
- Verify API key hasn't expired

**Error: "Network error"**
- Check internet connection
- Verify API URL is correct
- Check firewall settings

**Email not received:**
- Check spam folder
- Verify recipient email is correct
- Check Mailroo dashboard for delivery status
