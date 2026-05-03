# Deployment Guide - Free Hosting Options

## Option 1: Google Cloud Run (RECOMMENDED - Most Free Resources)
**Free Tier: 2M requests/month, 360,000 GB-seconds/month**

### Prerequisites
- GitHub account (already have your code there)
- Google Cloud account (free)
- Google Cloud SDK or just use Cloud Console

### Steps

1. **Push code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Add deployment files"
   git push origin main
   ```

2. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create new project
   - Enable Cloud Run API and Cloud Build API

3. **Deploy from GitHub**
   - Go to Cloud Run: https://console.cloud.google.com/run
   - Click "Create Service"
   - Select "Continuously deploy from GitHub"
   - Connect GitHub repo
   - Select repository and branch (main)
   - Service name: `exam-platform`
   - Region: `us-central1`
   - Memory: 512 MB (sufficient for free tier)
   - CPU: 1 vCPU
   - Allow unauthenticated invocations: YES
   - Click "Deploy"

4. **Get Shareable Link**
   - After deployment, you'll get: `https://exam-platform-xxxxx.run.app`
   - Share this link!

5. **Set Environment Variables**
   - In Cloud Run service settings → Environment variables
   - Add: `GEMINI_API_KEY=YOUR_KEY_HERE`
   - Add: `DATABASE_URL=sqlite:///./test.db` (or your DB connection)
   - Redeploy

**Deployment Time:** ~5-10 minutes
**Auto-scaling:** Yes (handles traffic spikes)
**Cost:** FREE for first 2M requests/month

---

## Option 2: Railway (Simple Alternative)
**Free Tier: $5/month free credits**

### Steps
1. Go to https://railway.app/
2. Sign in with GitHub
3. Create new project → Deploy from GitHub
4. Select this repository
5. Add environment variables in Railway dashboard
6. Click Deploy
7. Get public URL from deployment

---

## Option 3: Render (Another Alternative)
**Free Tier: 0.5 CPU, 512MB RAM, sleeps after 15 min inactivity**

### Steps
1. Go to https://render.com/
2. Sign up with GitHub
3. Create new Web Service
4. Connect GitHub repository
5. Build command: (leave auto)
6. Start command: `gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app`
7. Add environment variables
8. Deploy

---

## Database Setup for Free Deployment

Since your app uses SQLAlchemy, options:

### Option A: SQLite (Simplest)
- Default in most FastAPI apps
- File-based, works with free hosting
- Limited scalability (only for demo/testing)

### Option B: PostgreSQL (Better for Production)
**Free options:**
- **Render Database:** https://render.com/docs/databases
- **Railway PostgreSQL:** ~$7/month
- **Neon (Postgres):** Free tier available at https://neon.tech/
  
Add to environment variables:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## Important Notes for Free Tier

1. **Torch/ML Libraries (Heavy)**
   - Torch is ~1GB, sentence-transformers adds size
   - May exceed free tier memory limits
   - First deployment might take 10-15 min due to package installation

2. **Cold Start**
   - Free services go to sleep after inactivity
   - First request after inactivity takes 10-30 seconds
   - This is normal for free tier

3. **Limitations**
   - Free tier has CPU/memory constraints
   - May not handle real-time evaluation smoothly
   - Good for demo/testing, not production

4. **Monitoring**
   - Check Cloud Run Logs: `https://console.cloud.google.com/run`
   - Look for errors during deployment

---

## Quick Deployment Checklist

- [ ] Git repository initialized: `git status`
- [ ] Dockerfile present: `ls Dockerfile`
- [ ] Procfile present: `ls Procfile`
- [ ] requirements.txt updated with gunicorn: `grep gunicorn requirements.txt`
- [ ] Code committed: `git log --oneline | head -5`
- [ ] Environment variables planned: GEMINI_API_KEY, DATABASE_URL

---

## Testing Locally (Before Deploy)

```bash
# Test with Docker locally
docker build -t exam-platform .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_key" \
  exam-platform

# Visit http://localhost:8000
```

---

## Sharing Your Link

Once deployed, share: **`https://exam-platform-xxxxx.run.app`**

Others can:
- Visit the homepage
- Generate questions
- Create exams
- Submit answers
- View evaluations

---

## Cost Summary (First Month)

| Platform | Cost | Requests | Memory |
|----------|------|----------|--------|
| **Google Cloud Run** | FREE | 2M/month | 512MB |
| **Railway** | FREE | Unlimited* | Shared* |
| **Render** | FREE | Unlimited* | 512MB* |

*Limited by fair-use policy and CPU allocation

---

## Next Steps After Deployment

1. Share the deployed link with your team
2. Test exam submission workflow
3. Collect feedback
4. If successful, upgrade to paid tier for production
5. Implement monitoring/logging

---

## Support

- **Google Cloud Run Docs:** https://cloud.google.com/run/docs
- **Railway Docs:** https://docs.railway.app/
- **Render Docs:** https://render.com/docs/

Choose Google Cloud Run for best free features!
