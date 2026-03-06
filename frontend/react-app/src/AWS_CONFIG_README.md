# AWS Configuration

⚠️ **IMPORTANT**: You must configure this file before running the application!

## Steps:

1. Create a Cognito User Pool in AWS (see QUICKSTART.md)
2. Copy your User Pool ID and Client ID
3. Replace the placeholder values below
4. Save this file

## Configuration:

```javascript
const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'YOUR_USER_POOL_ID_HERE',      // Replace with your User Pool ID
      userPoolClientId: 'YOUR_CLIENT_ID_HERE',    // Replace with your Client ID
      loginWith: {
        email: true,
      },
    }
  }
};
```

## Example:

```javascript
const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'ap-south-1_abc123xyz',
      userPoolClientId: '1a2b3c4d5e6f7g8h9i0j1k2l3m',
      loginWith: {
        email: true,
      },
    }
  }
};
```

## Where to find these values:

**User Pool ID:**
- AWS Console → Cognito → Your User Pool
- Found at the top of the page

**Client ID:**
- AWS Console → Cognito → Your User Pool
- Click "App integration" tab
- Scroll to "App clients and analytics"
- Click on your app client
- Copy the "Client ID"

## Need Help?

See `QUICKSTART.md` for detailed instructions on creating a Cognito User Pool.
