# Deploy Dashboard to Netlify via Git

## ✅ What's Ready

- ✅ All Netlify Functions created
- ✅ Dashboard HTML migrated
- ✅ Git repository initialized
- ✅ All files committed

## 🚀 Deployment Steps

### Option 1: Deploy via GitHub (Recommended)

1. **Create GitHub Repository**
   ```bash
   cd dashboard_netlify
   
   # Create repo on GitHub (via web UI or GitHub CLI)
   gh repo create wheat-bot-dashboard --public --source=. --remote=origin --push
   ```
   
   Or manually:
   - Go to https://github.com/new
   - Create a new repository (e.g., `wheat-bot-dashboard`)
   - Don't initialize with README (we already have files)

2. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/wheat-bot-dashboard.git
   git branch -M main
   git push -u origin main
   ```

3. **Connect to Netlify**
   - Go to https://app.netlify.com
   - Click "Add new site" → "Import an existing project"
   - Choose "GitHub" and authorize
   - Select your `wheat-bot-dashboard` repository
   - Configure:
     - **Base directory**: `dashboard_netlify` (if repo is in parent folder)
     - **Build command**: (leave empty - no build needed)
     - **Publish directory**: `dashboard_netlify/public`
   - Click "Deploy site"

4. **Set Environment Variable**
   - In Netlify dashboard, go to: Site settings → Environment variables
   - Add: `NETLIFY_DATABASE_URL` = `your-neon-connection-string`
   - Redeploy: Deploys → Trigger deploy → Clear cache and deploy site

### Option 2: Deploy via Netlify CLI

1. **Login to Netlify**
   ```bash
   cd dashboard_netlify
   netlify login
   ```

2. **Initialize Site**
   ```bash
   netlify init
   ```
   - Choose "Create & configure a new site"
   - Select your team
   - Site name: `wheat-bot-dashboard` (or your choice)

3. **Set Environment Variable**
   ```bash
   netlify env:set NETLIFY_DATABASE_URL "your-neon-connection-string"
   ```

4. **Deploy**
   ```bash
   netlify deploy --prod
   ```

### Option 3: Deploy via GitLab/Bitbucket

Same process as GitHub, but choose GitLab or Bitbucket when connecting to Netlify.

## 📋 Before First Deploy

### 1. Set Up Neon Database Tables

Run this SQL in your Neon console:

```sql
-- Copy SQL from README_DEPLOY.md
-- Or run the table creation queries
```

### 2. Get Your Neon Connection String

From your Neon dashboard:
- Go to your project
- Click "Connection Details"
- Copy the connection string
- Format: `postgresql://user:password@host/database`

### 3. Set Environment Variable in Netlify

- **Name**: `NETLIFY_DATABASE_URL`
- **Value**: Your Neon connection string
- **Scopes**: All scopes (production, deploy previews, branch deploys)

## 🔄 Continuous Deployment

Once connected via Git:
- **Automatic**: Every push to `main` branch deploys automatically
- **Preview**: Pull requests get preview deployments
- **Manual**: Trigger deploys from Netlify dashboard

## 🧪 Test Your Deployment

1. Visit your site: `https://your-site-name.netlify.app`
2. Check Function logs: Netlify Dashboard → Functions → View logs
3. Test API endpoints:
   - `https://your-site-name.netlify.app/.netlify/functions/overview`
   - `https://your-site-name.netlify.app/.netlify/functions/positions`

## 🐛 Troubleshooting

**Functions not working?**
- Check Function logs in Netlify dashboard
- Verify `NETLIFY_DATABASE_URL` is set correctly
- Ensure Neon database tables are created

**Database connection errors?**
- Verify connection string format
- Check Neon database is running
- Test connection in Neon console

**CORS errors?**
- Functions already include CORS headers
- Check browser console for specific errors

**Build errors?**
- No build step needed for this project
- If Netlify tries to build, set build command to: `echo "No build"`

## 📝 Next Steps

1. ✅ Deploy to Netlify
2. ✅ Set environment variable
3. ✅ Create database tables
4. ✅ Test dashboard
5. ✅ Share your dashboard URL!

## 🔗 Your Dashboard URL

After deployment, your dashboard will be at:
`https://your-site-name.netlify.app`

You can also set a custom domain in Netlify settings.

