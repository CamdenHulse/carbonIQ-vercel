# CarbonIQ Deployment Guide

This guide will help you deploy your CarbonIQ application with the frontend on Vercel and backend on Railway.

## Architecture Overview

- **Frontend**: React + Vite → Deployed on Vercel
- **Backend**: FastAPI (Python) → Deployed on Railway
- **Why this setup?**: Your backend uses AI processing (Anthropic API) and loads large datasets, which work better on dedicated hosting like Railway rather than Vercel's serverless functions with strict timeout limits.

---

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **GitHub Account**: Your code should be in a GitHub repository
4. **Anthropic API Key**: Get one from [console.anthropic.com](https://console.anthropic.com)

---

## Part 1: Deploy Backend to Railway

### Step 1: Create a New Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account if not already connected
5. Select your `carbonIQ-vercel` repository
6. Railway will auto-detect it's a Python project

### Step 2: Configure Backend Directory

Railway needs to know where your backend code is:

1. In your Railway project, click on your service
2. Go to **Settings** tab
3. Under **Build & Deploy**, set:
   - **Root Directory**: `backend`
   - **Watch Paths**: `backend/**`

### Step 3: Set Environment Variables

In the **Variables** tab, add:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
PORT=8000
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

**Note**: You'll update `ALLOWED_ORIGINS` after deploying the frontend.

### Step 4: Deploy

1. Click **Deploy** or push a commit to trigger deployment
2. Railway will:
   - Install dependencies from `requirements.txt`
   - Run the command from `Procfile`
3. Once deployed, copy your backend URL (e.g., `https://your-app.up.railway.app`)

### Step 5: Verify Backend

Visit `https://your-app.up.railway.app/` - you should see:
```json
{
  "status": "healthy",
  "service": "CO₂UNT API",
  "app_name": "CO₂UNT - NYC Climate Impact Simulator",
  "version": "1.0.0"
}
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create a New Vercel Project

1. Go to [vercel.com](https://vercel.com) and log in
2. Click **"Add New"** → **"Project"**
3. Import your `carbonIQ-vercel` repository from GitHub
4. Vercel will auto-detect the configuration from `vercel.json`

### Step 2: Configure Environment Variables

In the **Environment Variables** section, add:

```
VITE_API_URL=https://your-app.up.railway.app
```

Replace with your actual Railway backend URL (from Part 1, Step 4).

### Step 3: Deploy

1. Click **Deploy**
2. Vercel will:
   - Run `npm install` in the `frontend` directory
   - Run `npm run build`
   - Deploy the `dist` folder
3. Once deployed, you'll get a URL like `https://your-app.vercel.app`

### Step 4: Update Backend CORS

Go back to Railway and update the `ALLOWED_ORIGINS` variable:

```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

This allows your Vercel frontend (including preview deployments) to access the backend.

---

## Part 3: Verify Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. The map should load with NYC emissions data
3. Try entering a prompt like "Reduce emissions in Manhattan by 20%"
4. Verify the simulation runs successfully

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
ANTHROPIC_API_KEY=your_api_key
ALLOWED_ORIGINS=http://localhost:5173
```

Run:
```bash
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

Run:
```bash
npm run dev
```

Frontend runs on `http://localhost:5173`

---

## Troubleshooting

### Backend Issues

**Problem**: Backend shows "Application failed to respond"
- Check Railway logs in the **Deployments** tab
- Verify `Procfile` exists and is correct
- Ensure `requirements.txt` has all dependencies
- Check that `PORT` environment variable is set

**Problem**: CORS errors in browser console
- Update `ALLOWED_ORIGINS` in Railway to include your Vercel domain
- Make sure there are no trailing slashes in the URLs

### Frontend Issues

**Problem**: "Backend connection failed" error
- Verify `VITE_API_URL` is set correctly in Vercel
- Check that Railway backend is running (visit the URL directly)
- Open browser DevTools → Network tab to see the failed request

**Problem**: Environment variable not working
- Remember: Vite env vars must start with `VITE_`
- Redeploy after adding environment variables
- Clear browser cache

### Data Loading Issues

**Problem**: Map shows no data
- Check Railway logs for errors in data loading
- Verify all data files are included in the repository
- Check that the `data/` directory is accessible to the backend

---

## Cost Estimates

### Vercel
- **Hobby (Free)**: 100 GB bandwidth/month, suitable for demos
- **Pro ($20/month)**: More bandwidth, commercial projects

### Railway
- **Free Trial**: $5 credit, no credit card needed
- **Developer Plan**: $5/month for 500 hours (enough for 24/7)
- **Usage-based**: ~$5-10/month for a small app

### Anthropic API
- Claude API costs per token usage
- Check [anthropic.com/pricing](https://www.anthropic.com/pricing)

---

## Alternative: Deploy Everything on Vercel (Not Recommended)

If you want to deploy the backend as Vercel serverless functions:

**Limitations**:
- 10 second timeout (Hobby), 60 seconds (Pro)
- Your AI processing may hit timeouts
- Cold starts on every request

**If you still want to try**:
1. Create `api/` directory at project root
2. Move backend code to serverless functions
3. This requires significant restructuring

**We recommend the Railway + Vercel approach** for better performance and reliability.

---

## Custom Domain (Optional)

### Vercel
1. Go to your project **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed

### Railway
1. Go to **Settings** → **Domains**
2. Add custom domain
3. Update DNS records

After adding custom domains, update environment variables:
- Vercel: `VITE_API_URL=https://api.yourdomain.com`
- Railway: `ALLOWED_ORIGINS=https://yourdomain.com`

---

## Monitoring

### Railway
- View logs in **Deployments** tab
- Monitor resource usage in **Metrics**
- Set up alerts for downtime

### Vercel
- View deployment logs in **Deployments**
- Monitor analytics in **Analytics** tab
- Check function logs for errors

---

## Security Best Practices

1. **Never commit `.env` files** - they're in `.gitignore`
2. **Rotate API keys** periodically
3. **Use HTTPS only** in production
4. **Limit CORS origins** - don't use `*` in production (we configured this already)
5. **Monitor API usage** - set up billing alerts on Anthropic console

---

## Need Help?

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Vite Docs**: [vitejs.dev](https://vitejs.dev)

---

## Summary Checklist

- [ ] Backend deployed to Railway
- [ ] Railway environment variables set (ANTHROPIC_API_KEY, PORT, ALLOWED_ORIGINS)
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] Vercel environment variable set (VITE_API_URL)
- [ ] CORS updated with Vercel URL
- [ ] Frontend loads and connects to backend
- [ ] Test simulation with a prompt
- [ ] Set up monitoring/alerts (optional)
- [ ] Configure custom domain (optional)

**Congratulations! Your CarbonIQ app is now live!** 🎉
