# Vercel Deployment Guide

## Step 1: Prepare Your Project

### Install Vercel CLI
```bash
npm install -g vercel
```

### Create `vercel.json` in project root
```json
{
  "builds": [
    {
      "src": "homeservices/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "homeservices/wsgi.py"
    }
  ],
  "env": {
    "DJANGO_SETTINGS_MODULE": "homeservices.settings"
  }
}
```

### Update `requirements.txt`
Ensure it includes:
```
Django
gunicorn
python-decouple
```

### Create `runtime.txt` in project root
```
python-3.11
```

## Step 2: Git Commit

```bash
# Add all changes
git add .

# Commit with message
git commit -m "Deploy to Vercel: Add Vercel configuration and runtime settings

- Added vercel.json for Vercel deployment configuration
- Added runtime.txt specifying Python 3.11
- Updated requirements.txt with necessary dependencies
- Configured WSGI entry point for Vercel hosting

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

# Push to GitHub (if connected)
git push origin main
```

## Step 3: Deploy to Vercel

### Option A: CLI Deployment
```bash
vercel
```
Follow the prompts:
1. Link to existing project or create new
2. Set framework to "Other"
3. Configure build command (if needed)
4. Deploy

### Option B: GitHub Integration (Recommended)

1. **Push to GitHub**
   - Ensure your project is on GitHub

2. **Visit Vercel Dashboard**
   - Go to https://vercel.com/dashboard
   - Click "Add New" → "Project"
   - Import your GitHub repository

3. **Configure Project**
   - Framework: Select "Other"
   - Root Directory: Leave blank or set to project root
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: Leave blank

4. **Environment Variables**
   - Add environment variables from `.env.example`:
     - Database URL
     - Secret Key
     - Debug: false
     - Allowed Hosts: your-vercel-domain.vercel.app

5. **Deploy**
   - Click "Deploy"

## Step 4: Post-Deployment

### Database Setup
```bash
# SSH into Vercel instance or use build script
python manage.py migrate
python manage.py collectstatic --noinput
```

### Environment Variables
Set in Vercel Dashboard:
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.vercel.app`
- `SECRET_KEY=your-secret-key`
- Database credentials

## Troubleshooting

**Issue: Static files not loading**
- Run: `python manage.py collectstatic`
- Ensure `STATIC_URL` and `STATIC_ROOT` are configured

**Issue: Database connection failed**
- Verify DATABASE_URL environment variable
- Check database is accessible from Vercel

**Issue: Module not found**
- Ensure all dependencies are in requirements.txt
- Run `pip freeze > requirements.txt` locally and recommit
