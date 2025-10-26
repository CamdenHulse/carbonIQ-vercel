# 🔗 Step-by-Step: Connect Vercel Frontend to Railway Backend

This guide shows you **exactly** how to connect your deployed Vercel frontend to your Railway backend.

---

## 🎯 Overview

Right now:
- ❌ Vercel frontend → tries to call `http://localhost:8000` → fails
- ✅ Railway backend → running at `https://your-app.up.railway.app` → works

We need to:
1. Get your Railway backend URL
2. Add it to Vercel as an environment variable
3. Redeploy Vercel so it uses the Railway URL

**Time needed:** 3 minutes

---

## Step 1: Get Your Railway Backend URL

### 1.1 Go to Railway Dashboard
- Visit: [railway.app](https://railway.app)
- Click on your CarbonIQ project

### 1.2 Find Your Backend Service
- You should see your backend service listed
- Click on it

### 1.3 Copy the Public URL
Look for the **Deployments** section or **Settings** tab:

**Option A - From Settings:**
- Click **Settings** tab
- Scroll to **Networking** section
- Look for **Public Networking**
- Click **Generate Domain** if you don't have one yet
- Copy the URL (looks like: `carboniq-production-xxxx.up.railway.app`)

**Option B - From Deployments:**
- Click on the **Deployments** tab
- Find your latest successful deployment (green checkmark)
- Copy the domain shown

### 1.4 Test the Backend URL
Open a new browser tab and visit:
```
https://your-railway-url.up.railway.app/
```

You should see:
```json
{
  "status": "healthy",
  "service": "CO₂UNT API",
  "app_name": "CO₂UNT - NYC Climate Impact Simulator",
  "version": "1.0.0"
}
```

✅ If you see this JSON, your backend is working!
❌ If you see an error, check the troubleshooting section below.

**Write down your Railway URL - you'll need it for Step 2!**

Example: `https://carboniq-production-a1b2c3.up.railway.app`

---

## Step 2: Add Environment Variable to Vercel

### 2.1 Go to Vercel Dashboard
- Visit: [vercel.com](https://vercel.com)
- Click on your CarbonIQ project

### 2.2 Navigate to Settings
- Click **Settings** (top menu)
- In the left sidebar, click **Environment Variables**

### 2.3 Add the API URL Variable

You'll see a form with three fields:

**Field 1: Key (Name)**
```
VITE_API_URL
```
Type exactly: `VITE_API_URL` (all caps, with underscore)

**Field 2: Value**
```
https://your-railway-url.up.railway.app
```
Paste your Railway URL from Step 1.4

⚠️ **IMPORTANT:**
- ✅ Use `https://` (secure)
- ❌ Do NOT add trailing slash: `https://example.com/` ← WRONG
- ✅ Should be: `https://example.com` ← CORRECT

**Field 3: Environments**
Check all three:
- ☑️ Production
- ☑️ Preview
- ☑️ Development

### 2.4 Save the Variable
- Click **Save** or **Add**
- You should see your new variable in the list:

```
VITE_API_URL = https://carboniq-production-xxxx.up.railway.app
```

---

## Step 3: Redeploy Vercel (Critical!)

Adding the environment variable **does NOT automatically update your live site**. You must redeploy.

### 3.1 Go to Deployments Tab
- Click **Deployments** in the top menu
- You'll see a list of your deployments

### 3.2 Find Latest Deployment
- Look for the most recent deployment (top of the list)
- It should say "Production" or have a ✓ checkmark

### 3.3 Redeploy
Click the **⋯** (three dots) button on the right side of that deployment

Select: **Redeploy**

A popup appears - click **Redeploy** again to confirm

### 3.4 Wait for Build to Complete
- The build typically takes 30-60 seconds
- You'll see a progress indicator
- Wait for the green checkmark ✅

---

## Step 4: Verify Connection

### 4.1 Open Your Vercel Site
Click **Visit** or open your Vercel URL:
```
https://your-project-name.vercel.app
```

### 4.2 Check the Map
- The page should load
- You should see the NYC map
- Red dots (baseline emissions) should appear
- No error message about "Backend connection failed"

### 4.3 Test a Simulation
Type a prompt in the text box:
```
Reduce emissions in Manhattan by 20%
```

Click **Simulate**

You should see:
- Green dots appear (simulation results)
- A difference view showing the impact
- No errors in the interface

### 4.4 Verify in Browser Console (Optional)

Press **F12** (or Cmd+Option+I on Mac) → **Console** tab

You should see logs like:
```
[CARBONIQ] Intervention received: {...}
```

Go to **Network** tab → reload page → look for `/api/baseline`:
- **Request URL**: Should be your Railway URL (not localhost!)
- **Status**: 200 OK
- **Response**: JSON data with grid points

---

## ✅ Success Checklist

- [ ] Railway backend shows healthy status at `/`
- [ ] Copied Railway URL (no trailing slash)
- [ ] Added `VITE_API_URL` to Vercel environment variables
- [ ] Selected all environments (Production, Preview, Development)
- [ ] Redeployed Vercel from Deployments tab
- [ ] Waited for build to complete (green checkmark)
- [ ] Visited Vercel site - map loads with data
- [ ] Tested a simulation - it works
- [ ] No "Backend connection failed" error

---

## 🔍 Troubleshooting

### Issue: Map still doesn't load after redeploying

**Check 1: Did you actually redeploy?**
- Adding env var doesn't auto-deploy
- You MUST click "Redeploy" in the Deployments tab

**Check 2: Is the environment variable correct?**
- Go back to Settings → Environment Variables
- Verify `VITE_API_URL` is spelled exactly right (case-sensitive!)
- Verify the Railway URL has no typos
- Verify no trailing slash

**Check 3: Check browser console**
```javascript
// In browser console, check what URL it's using:
// Look at Network tab → find /api/baseline request → check Request URL
```

If it still shows `http://localhost:8000`, the rebuild didn't pick up the env var.

**Fix:** Try these in order:
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Clear browser cache
3. Open in incognito/private window
4. Redeploy again from Vercel

### Issue: CORS Error in Console

Error message:
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Fix:** Update Railway environment variables:
1. Go to Railway project
2. Click on your backend service
3. **Variables** tab
4. Add or update:
   ```
   ALLOWED_ORIGINS=*
   ```
   Or specifically:
   ```
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-*.vercel.app
   ```
5. Railway will auto-redeploy

### Issue: Railway backend returns 404 or error

**Check:** Visit these URLs directly:
```
https://your-railway-url.up.railway.app/
https://your-railway-url.up.railway.app/api/baseline
```

If you see errors:
1. Go to Railway → Deployments → View Logs
2. Look for Python errors
3. Common issues:
   - Missing `ANTHROPIC_API_KEY` environment variable
   - Wrong root directory (should be `backend`)
   - Missing dependencies in `requirements.txt`

### Issue: Railway build failed

**Check Railway Logs:**
1. Railway dashboard → your service
2. **Deployments** tab
3. Click on failed deployment
4. **View Logs**

**Common fixes:**
- Root directory not set to `backend` (Settings → Build & Deploy)
- Missing `Procfile` in backend directory
- Python version incompatibility (check `runtime.txt`)

### Issue: Environment variable not showing in Vercel

**After adding the variable:**
- It only applies to NEW builds
- Existing deployments don't automatically get it
- You MUST redeploy

**To verify it's set:**
1. Settings → Environment Variables
2. Look for `VITE_API_URL` in the list
3. Should show all three checkmarks (Production, Preview, Development)

---

## 🎨 Visual Debugging: Network Tab

Here's how to see EXACTLY what's happening:

### 1. Open DevTools
Press **F12** or right-click → Inspect

### 2. Go to Network Tab
Click **Network** at the top

### 3. Reload Page
Press Ctrl+R or Cmd+R

### 4. Find the API Call
Look for `/api/baseline` in the list

### 5. Click on it
You'll see:

**Request URL:**
- ❌ Bad: `http://localhost:8000/api/baseline`
- ✅ Good: `https://your-railway-url.up.railway.app/api/baseline`

**Status:**
- ✅ `200 OK` - Working!
- ❌ `(failed)` - Not connecting
- ❌ `404` - Wrong URL or backend not running
- ❌ `500` - Backend error, check Railway logs
- ❌ `CORS error` - Update Railway `ALLOWED_ORIGINS`

**Response:**
- ✅ Should see JSON with `grid`, `metadata` fields
- ❌ If empty or error HTML, backend has issues

---

## 📋 Quick Reference

### Railway Backend Requirements

**Environment Variables:**
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
PORT=8000
ALLOWED_ORIGINS=*
```

**Settings:**
```
Root Directory: backend
Watch Paths: backend/**
```

**Files Required:**
- `backend/Procfile` → tells Railway how to run the app
- `backend/requirements.txt` → Python dependencies
- `backend/runtime.txt` → Python version

### Vercel Frontend Requirements

**Environment Variables:**
```bash
VITE_API_URL=https://your-railway-url.up.railway.app
```

**Important:**
- Variable name must be `VITE_API_URL` (not `API_URL`)
- Must start with `VITE_` for Vite to expose it
- Must redeploy after adding/changing variables
- No trailing slash on URL

---

## 🆘 Still Stuck?

### Check These URLs Directly:

1. **Railway backend health:**
   ```
   https://your-railway-url.up.railway.app/
   ```
   Should return: `{"status": "healthy", ...}`

2. **Railway baseline API:**
   ```
   https://your-railway-url.up.railway.app/api/baseline
   ```
   Should return: JSON with `grid` and `metadata`

3. **Vercel frontend:**
   ```
   https://your-vercel-app.vercel.app/
   ```
   Should show map with data

If any of these don't work, that's where the problem is.

### Get Help

- **Railway Logs:** Railway dashboard → Deployments → View Logs
- **Vercel Logs:** Vercel dashboard → Deployments → Function Logs
- **Browser Console:** F12 → Console tab (for frontend errors)
- **Network Tab:** F12 → Network tab (to see API calls)

---

## 💡 Understanding Environment Variables

**Why `VITE_API_URL`?**
- Vite (your build tool) only exposes env vars that start with `VITE_`
- At build time, Vite replaces `import.meta.env.VITE_API_URL` with the actual value
- This gets baked into the JavaScript file
- The browser then uses that hardcoded URL

**Why redeploy?**
- Environment variables are read at BUILD time, not runtime
- Changing an env var doesn't change already-built code
- You must rebuild to pick up the new value

**Test it:**
After redeploying, view your site's source code:
1. Right-click on page → View Page Source
2. Find the `.js` file in `<script>` tags
3. Open it (might be minified)
4. Search for your Railway URL - it should be in there!

---

**That's it!** Your frontend and backend should now be connected. The map should load with NYC emissions data, and you can run simulations! 🎉
