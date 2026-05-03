# Vercel Deployment Configuration for FastAPI

Vercel is primarily for **static sites and serverless functions**. While FastAPI can run on Vercel, there are **significant limitations** for your exam platform.

## ⚠️ Vercel Limitations for Your App

| Issue | Impact |
|-------|--------|
| **Function Timeout** | Hobby: 10s, Pro: 60s (exams run longer) |
| **Cold Starts** | 10-30 second delay on first request |
| **ML Libraries** | torch + sentence-transformers = 2GB (exceeds limit) |
| **Database** | Serverless functions can't persist state easily |
| **Concurrent Users** | Limited concurrent function executions |
| **Cost** | Hobby tier: very limited, Pro: expensive |

## ✅ RECOMMENDED: Use Google Cloud Run Instead

**Why it's better:**
- Designed for long-running containerized apps
- 2M requests/month FREE
- No function timeout limits
- Better for ML/database apps
- Easier scaling

**See:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for Google Cloud Run setup

---

## 🔧 If You Still Want Vercel (Not Recommended)

You'd need to:

1. **Rewrite FastAPI for serverless** (major changes - violates your "don't change code" requirement)
2. **Use lightweight alternatives** instead of torch
3. **Separate frontend and backend**
4. **Use external database service**

This would require significant code refactoring.

---

## 💡 Better Free/Cheap Alternatives

| Platform | Best For | Free Tier | Setup Time |
|----------|----------|-----------|-----------|
| **Google Cloud Run** ⭐ | Your app | 2M req/month | 5 min |
| **Railway** | Easy UI | $5/month credits | 3 min |
| **Render** | Simplicity | 512MB RAM | 5 min |
| **Heroku** | Simple deploy | Paid only | 10 min |
| **DigitalOcean** | Full control | $5/month | 15 min |

---

## Recommendation: Stay with Google Cloud Run

**See [GITHUB_DEPLOY.md](GITHUB_DEPLOY.md)** for:
- Automatic GitHub Actions deployment
- 99.95% uptime
- True serverless scaling
- Support for ML models
- Database compatibility

**Result:** Push code → Auto-deploy → Get live URL ✅

---

Would you like help with **Google Cloud Run** or **Railway** instead? Both work perfectly for your exam platform!
