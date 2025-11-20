#!/bin/bash

# Briefcase AI Private PyPI Server Setup Script
# This script sets up a private PyPI repository with authentication

set -e

echo "🏗️ Setting up Briefcase AI Private PyPI Server..."

# Create necessary directories
mkdir -p packages auth config traefik ssl-certs

echo "📁 Created directory structure"

# Create initial auth file (you'll need to add users)
if [ ! -f auth/.htpasswd ]; then
    echo "🔐 Creating authentication file..."
    echo "# Add users with: htpasswd -c auth/.htpasswd username" > auth/.htpasswd
    echo "# For additional users: htpasswd auth/.htpasswd username" >> auth/.htpasswd
    echo "⚠️  Please add users to auth/.htpasswd before starting the server"
fi

# Create pypiserver configuration
cat > config/pypiserver.conf << 'EOF'
# PyPI Server Configuration for Briefcase AI
# This file contains additional configuration options

[server]
host = 0.0.0.0
port = 8080
server-name = Briefcase AI Private PyPI
welcome-file = /data/config/welcome.html

[security]
authenticate = upload
disable-fallback = true
hash-algo = sha256

[logging]
log-level = INFO
log-stream = stdout
EOF

# Create welcome page
cat > config/welcome.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Briefcase AI Private PyPI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { color: #2563eb; font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
        .tagline { color: #6b7280; font-size: 1.1em; }
        .section { margin: 20px 0; }
        .code { background: #f3f4f6; padding: 15px; border-radius: 6px; font-family: monospace; overflow-x: auto; }
        .warning { background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; margin: 15px 0; }
        .info { background: #dbeafe; border: 1px solid #3b82f6; padding: 15px; border-radius: 6px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">📦 Briefcase AI</div>
            <div class="tagline">Private PyPI Repository</div>
        </div>

        <div class="warning">
            <strong>🔒 Private Repository</strong><br>
            This is a private PyPI repository for Briefcase AI packages. Authentication is required for package installation and upload.
        </div>

        <div class="section">
            <h3>📋 Installation Instructions</h3>
            <p>To install packages from this repository, use:</p>
            <div class="code">pip install --index-url https://pypi.briefcasebrain.com/simple/ --trusted-host pypi.briefcasebrain.com briefcase-ai-telemetry</div>
        </div>

        <div class="section">
            <h3>🔐 Authentication</h3>
            <p>For authenticated access, create a <code>.pypirc</code> file in your home directory:</p>
            <div class="code">[distutils]
index-servers = briefcase-ai

[briefcase-ai]
repository = https://pypi.briefcasebrain.com/
username = your-username
password = your-password</div>
        </div>

        <div class="section">
            <h3>📚 Available Packages</h3>
            <ul>
                <li><strong>briefcase-ai-telemetry</strong> - High-performance telemetry SDK for AI applications</li>
                <li>More packages coming soon...</li>
            </ul>
        </div>

        <div class="info">
            <strong>📄 License</strong><br>
            All packages in this repository are licensed under the Business Source License 1.1.
            Commercial use restrictions apply. See individual package licenses for details.
        </div>

        <div class="section">
            <h3>🆘 Support</h3>
            <p>For support or access requests, contact: <strong>support@briefcasebrain.com</strong></p>
        </div>
    </div>
</body>
</html>
EOF

# Create Traefik configuration (optional, for SSL)
mkdir -p traefik
cat > traefik/traefik.yml << 'EOF'
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entrypoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: support@briefcasebrain.com
      storage: /ssl-certs/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false
EOF

# Create environment file template
cat > .env.template << 'EOF'
# Private PyPI Server Environment Variables
# Copy this to .env and customize

# Domain configuration
PYPI_DOMAIN=pypi.briefcasebrain.com
PYPI_PORT=8080

# SSL configuration (optional)
SSL_EMAIL=support@briefcasebrain.com

# Security
PYPI_ADMIN_USER=admin
PYPI_ADMIN_PASSWORD=change-this-password

# Backup configuration
BACKUP_LOCATION=/opt/briefcase-pypi-backup
BACKUP_RETENTION_DAYS=30
EOF

echo "✅ Private PyPI server setup complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Copy .env.template to .env and customize"
echo "2. Add users to auth/.htpasswd:"
echo "   htpasswd -c auth/.htpasswd admin"
echo "3. Start the server:"
echo "   docker-compose up -d"
echo ""
echo "🌐 Server will be available at: http://localhost:8080"
echo "📖 Admin interface: http://localhost:8080"
echo ""
echo "🔍 For production deployment:"
echo "- Set up proper domain (pypi.briefcasebrain.com)"
echo "- Enable SSL with: docker-compose --profile with-ssl up -d"
echo "- Configure firewall and security groups"