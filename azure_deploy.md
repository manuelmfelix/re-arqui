# Azure Deployment Guide for RE-ARQUI Project

This guide outlines the steps to deploy the RE-ARQUI project to an Azure Linux B1 Web App.

## Prerequisites

- Azure account
- Azure CLI installed (optional, for command-line deployment)
- Git repository with your code

## Deployment Steps

### 1. Prepare Your Project

1. Make sure your `requirements.txt` file is properly configured (no circular references)
2. Create a `startup.sh` script to run on startup 
3. Create a `.deployment` file in the project root
4. Ensure your SQLite database is included in your project files
5. Make startup.sh executable with `chmod +x startup.sh` before deploying

### 2. Create Azure Web App

#### Through Azure Portal:

1. Go to the [Azure Portal](https://portal.azure.com)
2. Create a new "Web App" resource
3. Configure the following settings:
   - Publish: Code
   - Runtime stack: Python 3.9 or higher
   - Operating System: Linux
   - Region: (Choose the one closest to your users)
   - App Service Plan: B1 (as requested)

### 3. Configure Web App Settings

1. In the Azure Portal, navigate to your newly created web app
2. Go to "Configuration" → "Application settings" and add:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT`: true
   - `DJANGO_SETTINGS_MODULE`: re_arqui.settings_prod

3. Go to "Configuration" → "General settings":
   - Set "Startup Command" to: `sh startup.sh`

### 4. Deploy Your Code

#### Using Git:

1. In the Azure Portal, go to your web app → "Deployment Center"
2. Choose your source (GitHub, Azure DevOps, Local Git, etc.)
3. Follow the prompts to connect your repository
4. For local Git, you'll get a Git URL to add as a remote

```bash
git remote add azure <your-azure-git-url>
git push azure main
```

#### Using Azure CLI:

```bash
az webapp up --name <your-app-name> --resource-group <your-resource-group> --location <location> --sku B1 --os-type Linux
```

#### Using ZIP Deployment (Includes SQLite Database):

1. Create a ZIP file of your entire project, including the db.sqlite3 file
   ```bash
   zip -r deployment.zip . -x "venv/*" ".git/*"
   ```

2. Deploy using Azure CLI:
   ```bash
   az webapp deployment source config-zip --resource-group <resource-group> --name <app-name> --src deployment.zip
   ```

### 5. Verify Deployment

1. Access your app at `https://<your-app-name>.azurewebsites.net`
2. Check logs in the Azure Portal under "App Service Logs"

## Required Files

### .deployment
Create this file in your project root:

```
[config]
command = bash startup.sh
```

### startup.sh
Create this file in your project root:

```bash
#!/bin/bash

# Make migrations
python manage.py migrate --settings=re_arqui.settings_prod --no-input

# Collect static files
python manage.py collectstatic --settings=re_arqui.settings_prod --no-input

# Start Gunicorn
gunicorn --bind=0.0.0.0:8000 --workers=2 re_arqui.wsgi:application
```

## Including the SQLite Database

1. Make sure your SQLite database file (db.sqlite3) is included in your deployment package
2. The easiest way to include your database is to use ZIP deployment as described above
3. If deploying through Git, you'll need to ensure db.sqlite3 is not in your .gitignore file

## Azure-specific Settings Update

The settings_prod.py file has been updated to work with Azure's environment:

```python
# Add 'azurewebsites.net' to ALLOWED_HOSTS
ALLOWED_HOSTS = ['re-arqui.pt', 'www.re-arqui.pt', '*.azurewebsites.net', 'localhost', '127.0.0.1']

# Configure static files with WhiteNoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Web Server Configuration

Azure App Service provides its own web server configuration, so you don't need to include:
- nginx configuration files
- supervisor configuration files

The Gunicorn web server specified in startup.sh is sufficient, and Azure will automatically route HTTP requests to your application.

## Troubleshooting

- Check application logs in the Azure Portal:
  1. Go to your Web App → "App Service Logs"
  2. Enable "Application Logging" and set the level to "Verbose"
  3. View logs under "Log stream" or "Log files"

- SSH into your web app for direct troubleshooting:
  1. Enable SSH in the Azure Portal under "SSH" 
  2. Connect using the Azure Portal's web console or SSH client

- Common issues:
  - If you see "Application Error" or the app doesn't start, check the logs
  - Database write permissions: Make sure the app has permissions to write to db.sqlite3
  - Startup script not executed: Make sure startup.sh is executable (chmod +x) 