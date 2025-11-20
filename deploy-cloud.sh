#!/bin/bash

# Briefcase AI PyPI Server - Cloud Deployment Script
# This script deploys your private PyPI server to a cloud instance

set -e

# Configuration
SERVER_IP="${1:-}"
SSH_USER="${2:-root}"
DOMAIN="${3:-pypi.briefcasebrain.com}"
ADMIN_USER="${4:-admin}"

if [ -z "$SERVER_IP" ]; then
    echo "❌ Usage: $0 <server-ip> [ssh-user] [domain] [admin-user]"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.1.100"
    echo "  $0 192.168.1.100 ubuntu pypi.example.com admin"
    echo ""
    exit 1
fi

echo "🚀 Deploying Briefcase AI PyPI Server to Cloud"
echo "📍 Server: $SSH_USER@$SERVER_IP"
echo "🌐 Domain: $DOMAIN"
echo "👤 Admin User: $ADMIN_USER"
echo ""

# Check if we can connect to the server
echo "🔗 Testing SSH connection..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $SSH_USER@$SERVER_IP echo "Connected" 2>/dev/null; then
    echo "❌ Cannot connect to $SSH_USER@$SERVER_IP"
    echo "💡 Make sure:"
    echo "   - Server is running and accessible"
    echo "   - SSH key is properly configured"
    echo "   - Security groups allow SSH (port 22)"
    exit 1
fi
echo "✅ SSH connection successful"

# Copy files to server
echo "📦 Copying PyPI server files..."
scp -r pypi-server/ $SSH_USER@$SERVER_IP:~/
echo "✅ Files copied successfully"

# Create remote setup script
cat > remote-setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Installing dependencies..."
apt-get update
apt-get install -y docker.io docker-compose apache2-utils curl

echo "🐳 Starting Docker service..."
systemctl start docker
systemctl enable docker
usermod -aG docker $USER

echo "📁 Setting up PyPI server..."
cd pypi-server/
chmod +x setup-server.sh scripts/manage-users.sh

# Run setup
./setup-server.sh

echo "✅ Server setup complete"
EOF

# Copy and run setup script
echo "🛠️ Running server setup..."
scp remote-setup.sh $SSH_USER@$SERVER_IP:~/
ssh $SSH_USER@$SERVER_IP "bash remote-setup.sh"
echo "✅ Server setup complete"

# Create admin user
echo "🔐 Creating admin user..."
ssh $SSH_USER@$SERVER_IP "cd pypi-server && echo 'password123' | ./scripts/manage-users.sh add $ADMIN_USER" || true

# Update configuration for domain
echo "🌐 Configuring domain..."
cat > update-config.sh << EOF
#!/bin/bash
cd pypi-server/

# Update environment file
cat > .env << ENVEOF
PYPI_DOMAIN=$DOMAIN
PYPI_PORT=8080
SSL_EMAIL=support@briefcasebrain.com
PYPI_ADMIN_USER=$ADMIN_USER
PYPI_ADMIN_PASSWORD=password123
BACKUP_LOCATION=/opt/briefcase-pypi-backup
BACKUP_RETENTION_DAYS=30
ENVEOF

# Update docker-compose for domain
sed -i "s/pypi\\.briefcasebrain\\.com/$DOMAIN/g" docker-compose.yml

echo "✅ Configuration updated for domain: $DOMAIN"
EOF

scp update-config.sh $SSH_USER@$SERVER_IP:~/
ssh $SSH_USER@$SERVER_IP "bash update-config.sh"

# Start services
echo "🚀 Starting PyPI server..."
ssh $SSH_USER@$SERVER_IP "cd pypi-server && docker-compose up -d"

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Test the deployment
echo "🔍 Testing deployment..."
if curl -f http://$SERVER_IP:8080 >/dev/null 2>&1; then
    echo "✅ PyPI server is running successfully!"
else
    echo "⚠️ Server might still be starting. Check status with:"
    echo "   ssh $SSH_USER@$SERVER_IP 'cd pypi-server && docker-compose ps'"
fi

# Show next steps
echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. 🌐 Point $DOMAIN DNS to $SERVER_IP"
echo "2. 🔐 Update GitHub secrets:"
echo "   gh secret set PRIVATE_PYPI_URL --body 'https://$DOMAIN/'"
echo "   gh secret set PRIVATE_PYPI_USERNAME --body '$ADMIN_USER'"
echo "   gh secret set PRIVATE_PYPI_PASSWORD --body 'password123'"
echo ""
echo "3. 🔒 Enable SSL (after DNS propagation):"
echo "   ssh $SSH_USER@$SERVER_IP 'cd pypi-server && docker-compose --profile with-ssl up -d'"
echo ""
echo "4. 🔑 Change default password:"
echo "   ssh $SSH_USER@$SERVER_IP 'cd pypi-server && ./scripts/manage-users.sh change $ADMIN_USER'"
echo ""
echo "🌐 Server URLs:"
echo "   HTTP: http://$SERVER_IP:8080"
echo "   Domain (after DNS): https://$DOMAIN"
echo ""
echo "🔧 Server Management:"
echo "   SSH: ssh $SSH_USER@$SERVER_IP"
echo "   Logs: docker-compose logs pypi-server"
echo "   Restart: docker-compose restart"
echo ""

# Cleanup
rm -f remote-setup.sh update-config.sh

echo "✅ Cloud deployment script completed successfully!"