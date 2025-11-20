#!/bin/bash

# Briefcase AI PyPI Server - AWS Deployment Script
# Deploys to AWS EC2 with Route53 DNS integration

set -e

# Configuration
DOMAIN="pypi.briefcasebrain.com"
HOSTED_ZONE_ID="${1:-}"
AWS_REGION="${2:-us-east-1}"
INSTANCE_TYPE="${3:-t3.small}"
KEY_NAME="${4:-briefcase-pypi-key}"

echo "🚀 Briefcase AI PyPI - AWS Deployment"
echo "🌐 Domain: $DOMAIN"
echo "🗺️  Region: $AWS_REGION"
echo "💻 Instance: $INSTANCE_TYPE"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install it with:"
    echo "   pip install awscli"
    echo "   aws configure"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run:"
    echo "   aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"

# Get hosted zone ID if not provided
if [ -z "$HOSTED_ZONE_ID" ]; then
    echo "🔍 Looking up hosted zone for briefcasebrain.com..."
    HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name \
        --dns-name briefcasebrain.com \
        --query 'HostedZones[0].Id' \
        --output text 2>/dev/null | sed 's|/hostedzone/||')

    if [ "$HOSTED_ZONE_ID" = "None" ] || [ -z "$HOSTED_ZONE_ID" ]; then
        echo "❌ Could not find hosted zone for briefcasebrain.com"
        echo "💡 Please provide the hosted zone ID:"
        echo "   $0 Z1234567890ABC"
        exit 1
    fi
fi

echo "✅ Using hosted zone: $HOSTED_ZONE_ID"

# Create key pair if it doesn't exist
echo "🔑 Setting up SSH key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME >/dev/null 2>&1; then
    echo "📝 Creating new key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ~/.ssh/${KEY_NAME}.pem
    chmod 600 ~/.ssh/${KEY_NAME}.pem
    echo "✅ Key pair created: ~/.ssh/${KEY_NAME}.pem"
else
    echo "✅ Using existing key pair: $KEY_NAME"
fi

# Create security group
echo "🔒 Setting up security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name briefcase-pypi-sg \
    --description "Security group for Briefcase AI PyPI server" \
    --query 'GroupId' \
    --output text 2>/dev/null || aws ec2 describe-security-groups \
    --group-names briefcase-pypi-sg \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

# Add security group rules
echo "🚪 Configuring firewall rules..."
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 22 --cidr 0.0.0.0/0 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 443 --cidr 0.0.0.0/0 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 8080 --cidr 0.0.0.0/0 2>/dev/null || true

echo "✅ Security group configured: $SECURITY_GROUP_ID"

# Get latest Ubuntu AMI
echo "🐧 Finding latest Ubuntu 22.04 AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images|sort_by(@, &CreationDate)[-1].ImageId' \
    --output text)

echo "✅ Using AMI: $AMI_ID"

# Launch EC2 instance
echo "🚀 Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=briefcase-pypi-server}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "🎉 Instance launched: $INSTANCE_ID"
echo "⏳ Waiting for instance to be running..."

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Instance is running at: $PUBLIC_IP"

# Create Route53 DNS record
echo "🌐 Creating DNS record for $DOMAIN..."
cat > dns-record.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "$DOMAIN",
            "Type": "A",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "$PUBLIC_IP"
            }]
        }
    }]
}
EOF

CHANGE_ID=$(aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file://dns-record.json \
    --query 'ChangeInfo.Id' \
    --output text)

echo "✅ DNS record created. Change ID: $CHANGE_ID"

# Wait for DNS propagation (optional)
echo "⏳ Waiting for DNS to propagate..."
sleep 30

# Wait for SSH to be available
echo "⏳ Waiting for SSH to be available..."
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP echo "Connected" 2>/dev/null; do
    echo "   Still waiting for SSH..."
    sleep 10
done

echo "✅ SSH connection established"

# Deploy PyPI server
echo "📦 Deploying PyPI server..."
./deploy-cloud.sh $PUBLIC_IP ubuntu $DOMAIN admin

# Clean up temporary files
rm -f dns-record.json

echo ""
echo "🎉 AWS Deployment Complete!"
echo ""
echo "📋 Server Details:"
echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   Domain: $DOMAIN"
echo "   SSH Key: ~/.ssh/${KEY_NAME}.pem"
echo ""
echo "🔧 Management Commands:"
echo "   SSH: ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo "   Logs: ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'cd pypi-server && docker-compose logs'"
echo ""
echo "🔒 Security:"
echo "   - Change default password: ssh ubuntu@$PUBLIC_IP 'cd pypi-server && ./scripts/manage-users.sh change admin'"
echo "   - SSL will be auto-configured via Let's Encrypt"
echo ""
echo "🌐 URLs:"
echo "   Testing: http://$PUBLIC_IP:8080"
echo "   Production: https://$DOMAIN (after SSL setup)"
echo ""
echo "📝 Next: Update GitHub secrets with these values:"
echo "   gh secret set PRIVATE_PYPI_URL --body 'https://$DOMAIN/'"
echo "   gh secret set PRIVATE_PYPI_USERNAME --body 'admin'"
echo "   gh secret set PRIVATE_PYPI_PASSWORD --body 'password123'"
echo ""

# Save deployment info
cat > deployment-info.txt << EOF
Briefcase AI PyPI Server - AWS Deployment Info
Generated: $(date)

Instance Details:
- Instance ID: $INSTANCE_ID
- Public IP: $PUBLIC_IP
- Domain: $DOMAIN
- Region: $AWS_REGION
- Instance Type: $INSTANCE_TYPE

DNS:
- Hosted Zone ID: $HOSTED_ZONE_ID
- DNS Change ID: $CHANGE_ID

SSH Access:
- Key: ~/.ssh/${KEY_NAME}.pem
- Command: ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP

Management:
- Start: docker-compose up -d
- Stop: docker-compose down
- Logs: docker-compose logs pypi-server
- Users: ./scripts/manage-users.sh list

GitHub Secrets:
PRIVATE_PYPI_URL=https://$DOMAIN/
PRIVATE_PYPI_USERNAME=admin
PRIVATE_PYPI_PASSWORD=password123

Costs (estimated):
- EC2 $INSTANCE_TYPE: ~\$15-30/month
- Route53 Hosted Zone: \$0.50/month
- Data Transfer: ~\$1-5/month
Total: ~\$16-35/month
EOF

echo "💾 Deployment info saved to: deployment-info.txt"
echo "✅ AWS deployment script completed successfully!"