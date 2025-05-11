# Deployment Guide for re-arqui.pt

This guide outlines the steps to deploy the RE-ARQUI project to a cPanel environment.

## Prerequisites

- cPanel access with SSH enabled
- Python 3.8+ support on your hosting
- Ability to create SQLite databases
- Ability to configure Apache

## Deployment Steps

### 1. Set Up Environment

```bash
# SSH into your server
ssh username@re-arqui.pt

# Navigate to your home directory
cd ~

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Clone the repository directly into the correct location
git clone https://github.com/yourusername/re_arqui.git
cd re_arqui

# Install production dependencies
pip install -r requirements_prod.txt
```

### 2. Configure Production Settings

```bash
# Generate a secure secret key
python generate_secret_key.py

# Collect static files
python manage.py collectstatic --settings=re_arqui.settings_prod --no-input

# Run migrations
python manage.py migrate --settings=re_arqui.settings_prod
```

### 3. Fix File Permissions

This step is critical for Passenger to work correctly:

```bash
# Navigate to your project directory
cd ~/re_arqui

# Set directory permissions
find . -type d -exec chmod 755 {} \;

# Set file permissions
find . -type f -exec chmod 644 {} \;

# Make executable scripts actually executable
chmod 755 manage.py

# Make sure all Passenger-specific files are readable
chmod 644 Passengerfile.json
chmod 644 passenger_wsgi.py
```

See the `PERMISSIONS_FIX.md` file for more detailed instructions if you encounter permission errors.

### 4. Configure Passenger

Make sure your Passengerfile.json has the correct path to your Python interpreter:

```json
{
  "app_type": "wsgi",
  "startup_file": "passenger_wsgi.py",
  "python": "/home/username/venv/bin/python",
  "environment": "production"
}
```

Replace `/home/username/venv/bin/python` with the actual path to your virtual environment's Python.

### 5. Configure Apache/cPanel

1. In cPanel, go to "Python Application" and create a new app
2. Set the application path to your project directory (e.g., `/home/username/re_arqui`)
3. Set the application URL to your domain
4. Set the WSGI file to passenger_wsgi.py
5. Save and deploy

### 6. Troubleshooting

If you encounter errors after deployment:

1. Check the Apache error logs
2. Verify that all file permissions are set correctly (see step 3)
3. Make sure the virtual environment path in Passengerfile.json is correct
4. Restart the application through cPanel
5. If Passenger-specific errors appear, follow the instructions in PERMISSIONS_FIX.md

## Important Security Notes

1. Never store `secret_key.json` in version control
2. Keep your database file secure
3. Regularly update dependencies to patch security vulnerabilities
4. Consider setting up automatic backups for the database and media files 