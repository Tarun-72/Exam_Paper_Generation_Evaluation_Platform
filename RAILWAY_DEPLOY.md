# 🚀 Deploy to Railway (Easiest Free Option)

**Railway is perfect for FastAPI apps - easier than Vercel!**

## Why Railway?

✅ Simple one-click deployment  
✅ PostgreSQL included  
✅ Free $5/month credits  
✅ Auto-deploys from GitHub  
✅ Works with ML libraries  
✅ No function timeouts  

---

## Step 1: Push Code to GitHub (If Not Done)

```powershell
cd "c:\Users\jagan\Desktop\Exam_Paper_Generation_Evaluation_Platform"

# Create GitHub repo first at github.com/new
git remote add origin https://github.com/YOUR_USERNAME/Exam_Paper_Generation_Evaluation_Platform.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Railway (2 Minutes)

### Go to: **https://railway.app**

1. **Sign up** → Click "Sign in with GitHub"
2. Click **"New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select your repository
5. Click **Deploy**

**That's it!** 🎉 Railway auto-detects FastAPI and deploys!

---

## Step 3: Add Environment Variables

1. Go to your Railway project
2. Click **Variables** tab
3. Add:
   - `GEMINI_API_KEY` = your API key
   - `DATABASE_URL` = (Railway generates this automatically)

4. Click **Deploy**

---

## Step 4: Get Your Live URL

1. Go to **Deployments** tab
2. Click on the active deployment
3. See your public URL at the top
4. Example: `exam-platform-production.up.railway.app`

---

## Step 5: Share & Done!

Share your URL with anyone: `https://exam-platform-production.up.railway.app`

---

## How It Works

- **GitHub Push** → Railway auto-detects changes
- **Auto-rebuild** → New deployment automatically
- **Database** → PostgreSQL included for free
- **Logs** → Real-time debugging

---

## Cost

- **Free tier:** $5 monthly credits (usually enough)
- **After credits:** $0.50/GB-hour (very cheap)
- **Best for:** Demo, testing, small production

---

## Troubleshooting

### Deployment failed?
- Check **Build Logs** tab
- Usually missing environment variables
- Add `GEMINI_API_KEY` in Variables

### App not responding?
- Check **Deployment Logs**
- Look for Python errors
- Railway shows exact error

### Want to update code?
- Just `git push` to GitHub
- Railway auto-redeploys in ~2 minutes

---

## Comparison: Vercel vs Railway vs Google Cloud Run

| Feature | Vercel | Railway | Google Cloud |
|---------|--------|---------|--------------|
| **Timeout** | 10-60s ❌ | Unlimited ✅ | Unlimited ✅ |
| **Cold Start** | 10-30s ⚠️ | Fast ✅ | Fast ✅ |
| **ML Libraries** | No ❌ | Yes ✅ | Yes ✅ |
| **Database** | External | Included ✅ | External |
| **Free Tier** | Limited ⚠️ | $5/mo ✅ | 2M req/mo ✅ |
| **Setup Time** | 15 min | 2 min | 5 min |

**Winner for your app: Railway** 🏆

---

## Quick Deployment Summary

1. ✅ Code in GitHub
2. ✅ Go to railway.app
3. ✅ Connect GitHub repo
4. ✅ Add env variables
5. ✅ Deploy
6. ✅ Get live URL

**Total time: ~5 minutes**

---

## Alternative: If You Prefer Google Cloud Run

See [GITHUB_DEPLOY.md](GITHUB_DEPLOY.md) for auto-deployment with GitHub Actions

---

**Ready to deploy? Pick Railway - it's the fastest! 🚀**
