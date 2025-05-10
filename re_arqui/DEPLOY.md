# Deployment Guide for re-arqui.pt

This guide outlines the steps to deploy the RE-ARQUI project to a cPanel environment.

## Prerequisites

- cPanel access with SSH enabled
- Python 3.8+ support on your hosting
- Ability to create MySQL databases
- Ability to configure Nginx
- Domain (re-arqui.pt) pointed to your hosting

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

# Clone the repository
git clone https://github.com/yourusername/re_arqui.git
cd re_arqui

# Install production dependencies
pip install -r requirements_prod.txt
```

### 2. Database Setup

1. Create a MySQL database in cPanel (e.g., `rearqui_db`)
2. Create a database user (e.g., `rearqui_dbuser`) with all privileges on this database
3. Update the database credentials in `re_arqui/settings_prod.py` or use environment variables

### 3. Configure Production Settings

```bash
# Generate a secure secret key
python generate_secret_key.py

# Collect static files
python manage.py collectstatic --settings=re_arqui.settings_prod --no-input

# Run migrations
python manage.py migrate --settings=re_arqui.settings_prod
```

### 4. Set Up Supervisor

1. Install Supervisor if not already available:
   ```bash
   pip install supervisor
   ```

2. Copy the supervisor configuration:
   ```bash
   cp supervisord.conf ~/supervisord.conf
   ```

3. Start Supervisor:
   ```bash
   supervisord -c ~/supervisord.conf
   ```

4. Verify that it's running:
   ```bash
   supervisorctl status
   ```

### 5. Nginx Configuration

1. If you have access to Nginx configuration (VPS/dedicated hosting):
   - Copy `nginx.conf` to `/etc/nginx/sites-available/re-arqui.pt`
   - Create a symbolic link: `ln -s /etc/nginx/sites-available/re-arqui.pt /etc/nginx/sites-enabled/`
   - Test and reload Nginx: `nginx -t && systemctl reload nginx`

2. If using cPanel with Apache:
   - Set up a proxy in `.htaccess`:
   ```
   RewriteEngine On
   
   # Serve static files directly
   RewriteCond %{REQUEST_URI} ^/static/
   RewriteRule ^static/(.*)$ /home/rearquipt/re_arqui/staticfiles/$1 [L]
   
   RewriteCond %{REQUEST_URI} ^/media/
   RewriteRule ^media/(.*)$ /home/rearquipt/re_arqui/media/$1 [L]
   
   # Forward API requests to FastAPI
   RewriteCond %{REQUEST_URI} ^/api/
   RewriteRule ^api/(.*)$ http://127.0.0.1:8001/$1 [P,L]
   
   # Forward all other requests to Django
   RewriteCond %{REQUEST_URI} !^/static/
   RewriteCond %{REQUEST_URI} !^/media/
   RewriteCond %{REQUEST_URI} !^/api/
   RewriteRule ^(.*)$ http://127.0.0.1:8000/$1 [P,L]
   ```

### 6. SSL Certificate

1. Use Let's Encrypt through cPanel or run certbot manually:
   ```bash
   certbot --nginx -d re-arqui.pt -d www.re-arqui.pt
   ```

### 7. Test Your Deployment

1. Visit your website at https://re-arqui.pt
2. Test the front-end functionality
3. Test the API at https://re-arqui.pt/api/projects/list/

### 8. Maintenance Commands

```bash
# Restart the application
supervisorctl restart rearqui

# View logs
tail -f ~/re_arqui/django_prod.log
tail -f ~/re_arqui/uvicorn.log

# Update the application
cd ~/re_arqui
git pull
source ~/venv/bin/activate
pip install -r requirements_prod.txt
python manage.py migrate --settings=re_arqui.settings_prod
python manage.py collectstatic --settings=re_arqui.settings_prod --no-input
supervisorctl restart rearqui
```

## Troubleshooting

- **500 Server Error**: Check the Django and Uvicorn logs for errors
- **Static Files Not Loading**: Verify the paths in Nginx/Apache configuration
- **Database Connection Issues**: Verify credentials and database connectivity
- **Permission Issues**: Ensure the application directory has proper permissions
- **Supervisor Not Starting**: Check supervisor logs and ensure paths are correct

## Important Security Notes

1. Never store `secret_key.json` in version control
2. Keep your database credentials secure
3. Regularly update dependencies to patch security vulnerabilities
4. Consider setting up automatic backups for the database and media files 