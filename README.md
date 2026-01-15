# GitHub Commit Email Notifier
A Dockerized Python application that listens for GitHub webhooks and sends an email notification every time a push is committed to your repositories.

## Prerequisites
- A VPS with Docker and Docker Compose installed.
- An Nginx web server configured with SSL (HTTPS).
- An SMTP email account (e.g., PrivateEmail, Gmail, SendGrid).

## Configuration and deployment
### 1. Clone the repository
```bash
git clone https://github.com/pelazas/gh-commit-notification.git
```

### 2. Env setup
Create a .env file and fill these:
```bash
EMAIL_PASSWORD="XXXXXXXXXX"
TARGET_EMAIL="xxxxxxxx@gmail.com"
GITHUB_SECRET="XXXXXXXXXX"
EMAIL_HOST="XXXXXXXXXX"
EMAIL_PORT=999
EMAIL_USER="xxxxxxxx@gmail.com"
```

### 3. Deploy container
```bash
docker compose up -d --build
```

### 4. Nginx configuration
Add this block to your Nginx server config (inside the SSL server block). This proxies the public /notifier/ URL to the internal /webhook endpoint.

```nginx
location /notifier/ {
    proxy_pass http://127.0.0.1:8003/webhook;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
After updating the configuration, reload Nginx

### 5. GitHub App Setup
- Create App: Go to Settings > Developer Settings > GitHub Apps > New GitHub App.
- Webhook URL: Set to https://yourdomain.com/notifier/
    - Important: Ensure it ends with a slash /.
    - Important: Do NOT add webhook to the end (Nginx handles that).
- Webhook Secret: Paste the GITHUB_SECRET from your .env file.
- Permissions: Set Repository contents to Read-only.
- Subscribe to Events: Check Push.
- Click Create App.
- Install App: Go to Install App on the left sidebar.
- Click Install next to your account.
- Select All repositories.


## Troubleshooting
To check if the container is running on the correct port:

```bash
docker ps
```
Expected output example:
```bash
563c489cf033 gh-commit-notification-github-notifier "gunicorn --bind 0.0…" 50 minutes ago Up 50 minutes 0.0.0.0:8003->8003/tcp, [::]:8003->8003/tcp github_notifier
```
To view application logs:

```bash
docker logs github_notifier
````
