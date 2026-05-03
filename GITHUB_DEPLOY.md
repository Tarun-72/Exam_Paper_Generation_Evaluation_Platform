# 🚀 Quick GitHub to Cloud Run Deployment

Your code is ready to deploy! Follow these 3 steps:

## Step 1: Push to GitHub

```powershell
cd "c:\Users\jagan\Desktop\Exam_Paper_Generation_Evaluation_Platform"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/Exam_Paper_Generation_Evaluation_Platform.git

# Push to main branch
git branch -M main
git push -u origin main
```

## Step 2: Create Google Cloud Project & Setup Deployment

Go to: **https://console.cloud.google.com/**

1. **Create a new project**
   - Name: `exam-platform`
   - Click Create

2. **Enable APIs**
   - Search for "Cloud Run API" → Enable
   - Search for "Cloud Build API" → Enable
   - Search for "Container Registry API" → Enable

3. **Create Service Account** (for CI/CD)
   - Go to: **IAM & Admin** → **Service Accounts**
   - Click **Create Service Account**
   - Name: `github-deployment`
   - Grant roles:
     - Cloud Run Admin
     - Cloud Build Service Account
     - Container Registry Service Account
   - Click **Create & Continue**
   - Skip optional steps
   - Click **Create Key** → JSON → Download file

## Step 3: Add GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**

2. Click **New repository secret** and add:

   **Secret 1:**
   - Name: `GCP_PROJECT_ID`
   - Value: Your GCP Project ID (from console)

   **Secret 2:**
   - Name: `GCP_SA_KEY`
   - Value: Paste entire contents of downloaded JSON file

   **Secret 3:**
   - Name: `GEMINI_API_KEY`
   - Value: Your Gemini API key

## Step 4: Trigger Deployment

Any push to `main` branch will auto-deploy!

```powershell
# Make a change to trigger deployment
echo "# Updated" >> README.md
git add README.md
git commit -m "Trigger deployment"
git push origin main
```

## Step 5: Monitor Deployment

1. Go to GitHub repo → **Actions** tab
2. Watch the deployment workflow run
3. After success (~10-15 min), your app is live!

## Step 6: Get Your Public URL

In **Google Cloud Console:**
- Go to **Cloud Run**
- Click on `exam-platform` service
- Copy the URL from **Service details**
- Example: `https://exam-platform-abc123.run.app`

## 🎯 Share This Link!

Once deployed, share: `https://exam-platform-abc123.run.app`

Others can:
✅ Create exams
✅ Generate questions  
✅ Submit answers
✅ View evaluations

---

## Troubleshooting

### Deployment Failed?
- Check GitHub Actions log → **Actions** tab
- Common issue: Missing secrets → verify all 3 secrets are added
- Missing API: Enable all 3 APIs mentioned above

### Service not responding?
- Wait 2-3 minutes after deployment
- Check Cloud Run logs: **Cloud Run** → **exam-platform** → **Logs**

### Need to update code?
- Just push to main: `git push origin main`
- GitHub Actions automatically redeployes!

---

## Alternative: Manual Deploy (if Actions fails)

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy exam-platform \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=YOUR_KEY_HERE"
```

---

**Ready? Let's go! 🚀**
