# 🔐 Private PyPI Repository - Management Guide

**Internal documentation for dev team credential provisioning and user management**

This guide provides step-by-step instructions for managing the private PyPI repository, including user provisioning, credential management, and beta participant onboarding.

---

## 🎯 **Overview**

The private PyPI repository is hosted at `https://pypi.briefcasebrain.com/` and requires authentication for package installation. This guide covers:
- Adding new beta participants
- Managing user credentials
- Monitoring access and usage
- Troubleshooting access issues

---

## 🔧 **Prerequisites**

**Required Access:**
- SSH access to the PyPI server: `ssh ubuntu@pypi.briefcasebrain.com`
- AWS console access for EC2 instance management
- GitHub repository admin access for secrets management

**SSH Key:**
```bash
# Use the deployment key (created during AWS setup)
ssh -i ~/.ssh/briefcase-pypi-key.pem ubuntu@pypi.briefcasebrain.com
```

---

## 👥 **Adding New Beta Participants**

### **Step 1: Receive Beta Application**

When a beta participant is approved (after signing the Beta Participation Agreement):

1. **📧 Collect Required Information:**
   - Organization name
   - Primary contact email
   - Technical contact email
   - Intended use case
   - Expected usage scale

2. **📋 Generate Credentials:**
   - Username: Use format `{company_name}_{contact_initials}` (e.g., `acme_jd`)
   - Password: Generate secure password using method below

### **Step 2: Generate Secure Credentials**

```bash
# SSH into the PyPI server
ssh -i ~/.ssh/briefcase-pypi-key.pem ubuntu@pypi.briefcasebrain.com

# Navigate to PyPI server directory
cd pypi-server

# Generate secure password
openssl rand -base64 32 | cut -c1-16

# Example output: K8mN2qR7vX9pL3wZ
```

### **Step 3: Add User to PyPI Server**

```bash
# Use the user management script
./scripts/manage-users.sh add {username}

# Example:
./scripts/manage-users.sh add acme_jd

# You'll be prompted to enter the password twice
# Enter the generated secure password from Step 2
```

### **Step 4: Test User Access**

```bash
# Verify user was added successfully
./scripts/manage-users.sh list

# Test authentication (replace with actual credentials)
curl -u acme_jd:K8mN2qR7vX9pL3wZ https://pypi.briefcasebrain.com/simple/

# Should return PyPI simple index without 401 error
```

### **Step 5: Send Credentials to Beta Participant**

**📧 Email Template:**

```
Subject: Briefcase AI Beta Access - PyPI Credentials

Dear [Contact Name],

Welcome to the Briefcase AI Telemetry SDK Beta Program!

Your private PyPI repository access is now configured:

🔗 Repository URL: https://pypi.briefcasebrain.com/simple/
👤 Username: acme_jd
🔑 Password: K8mN2qR7vX9pL3wZ

📦 Installation Command:
pip install --index-url https://acme_jd:K8mN2qR7vX9pL3wZ@pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry

📊 Dashboard Access: https://observe.briefcasebrain.io/
🔑 API Key: [Provided separately or via dashboard signup]

📚 Documentation:
- Getting Started: https://github.com/briefcasebrain/telemetry-sdk-examples/blob/main/GETTING_STARTED.md
- Examples: https://github.com/briefcasebrain/telemetry-sdk-examples

🆘 Support: support@briefcasebrain.com

Next Steps:
1. Install the SDK using the command above
2. Follow the getting started guide
3. Set up your dashboard access
4. Begin integration with your application

Best regards,
Briefcase AI Team
```

**🔒 Security Notes:**
- Send credentials via secure email or encrypted communication
- Consider using temporary credentials for initial setup
- Advise users to store credentials securely (environment variables, secret managers)

---

## 📊 **Managing Existing Users**

### **List All Users**

```bash
ssh -i ~/.ssh/briefcase-pypi-key.pem ubuntu@pypi.briefcasebrain.com
cd pypi-server
./scripts/manage-users.sh list
```

### **Change User Password**

```bash
# Reset password for existing user
./scripts/manage-users.sh change {username}

# Example:
./scripts/manage-users.sh change acme_jd

# Enter new secure password when prompted
```

### **Remove User Access**

```bash
# Remove user (use sparingly - only for terminated beta participation)
./scripts/manage-users.sh remove {username}

# Example:
./scripts/manage-users.sh remove acme_jd

# Confirm removal when prompted
```

### **View User Activity**

```bash
# Check PyPI server logs for user activity
docker-compose logs pypi-server | grep "{username}"

# View recent access logs
docker-compose logs pypi-server --tail 100 | grep "GET\|POST"
```

---

## 📈 **Monitoring & Analytics**

### **Server Health Monitoring**

```bash
# Check server status
ssh -i ~/.ssh/briefcase-pypi-key.pem ubuntu@pypi.briefcasebrain.com
cd pypi-server

# Check Docker containers
docker-compose ps

# Check system resources
df -h
free -h
top
```

### **Package Usage Analytics**

```bash
# View download statistics
docker-compose logs pypi-server | grep "GET.*briefcase-ai-telemetry" | wc -l

# Recent downloads (last 100 log entries)
docker-compose logs pypi-server --tail 1000 | grep "GET.*briefcase-ai-telemetry"

# Unique users downloading packages
docker-compose logs pypi-server | grep "GET.*briefcase-ai-telemetry" | awk '{print $1}' | sort | uniq -c
```

### **Security Monitoring**

```bash
# Check failed authentication attempts
docker-compose logs pypi-server | grep "401\|403\|Unauthorized"

# Monitor unusual activity patterns
docker-compose logs pypi-server | grep "POST\|PUT\|DELETE" | tail -20
```

---

## 🛠️ **Troubleshooting Common Issues**

### **User Cannot Install Package**

**1. Verify Credentials:**
```bash
# Test authentication
curl -u {username}:{password} https://pypi.briefcasebrain.com/simple/

# Should return HTML index, not 401 error
```

**2. Check User Exists:**
```bash
./scripts/manage-users.sh list | grep {username}
```

**3. Test Package Availability:**
```bash
# Check if package is uploaded
ls -la /data/packages/ | grep briefcase-ai-telemetry
```

### **Server Issues**

**1. PyPI Server Not Responding:**
```bash
# Check container status
docker-compose ps

# Restart if needed
docker-compose down && docker-compose up -d

# Check logs for errors
docker-compose logs pypi-server --tail 50
```

**2. SSL Certificate Issues:**
```bash
# Check certificate expiry
openssl s_client -connect pypi.briefcasebrain.com:443 -servername pypi.briefcasebrain.com </dev/null 2>/dev/null | openssl x509 -noout -dates

# Renew certificate if needed (automated via Let's Encrypt)
sudo certbot renew
```

**3. Disk Space Issues:**
```bash
# Check disk usage
df -h

# Clean up old logs if needed
docker system prune -f

# Archive old package versions if necessary
```

---

## 🔄 **Beta Program Lifecycle Management**

### **Onboarding New Cohorts**

**Monthly Beta Cohort Process:**
1. **Review Applications** - Validate beta agreement signatures
2. **Batch Credential Creation** - Create credentials for approved participants
3. **Send Welcome Package** - Email credentials and documentation
4. **Monitor Initial Usage** - Track first-week adoption metrics
5. **Follow-up Support** - Proactive check-in after 1 week

### **Offboarding Process**

**When beta participation ends:**
1. **Data Export** - Offer participants export of their telemetry data
2. **Credential Cleanup** - Remove PyPI access
3. **Migration Path** - Provide instructions for production upgrade
4. **Feedback Collection** - Exit survey for program improvement

### **Usage Monitoring & Limits**

**Current Beta Limits:**
- **Download limit**: No technical limit (monitor usage)
- **Storage**: 1M events/month in dashboard
- **Support**: Standard beta support channels

**Monitoring Commands:**
```bash
# Weekly usage report
echo "=== Weekly PyPI Usage Report ==="
echo "Total downloads this week:"
docker-compose logs pypi-server --since "7d" | grep "GET.*briefcase-ai-telemetry" | wc -l

echo "Active users this week:"
docker-compose logs pypi-server --since "7d" | grep "GET.*briefcase-ai-telemetry" | awk '{print $1}' | sort | uniq | wc -l
```

---

## 📚 **Quick Reference**

### **Common Commands**

```bash
# SSH into server
ssh -i ~/.ssh/briefcase-pypi-key.pem ubuntu@pypi.briefcasebrain.com

# User management
cd pypi-server
./scripts/manage-users.sh list                    # List all users
./scripts/manage-users.sh add {username}          # Add new user
./scripts/manage-users.sh change {username}       # Change password
./scripts/manage-users.sh remove {username}       # Remove user

# Server management
docker-compose ps                                 # Check status
docker-compose logs pypi-server --tail 50       # View recent logs
docker-compose restart pypi-server              # Restart server
docker-compose down && docker-compose up -d     # Full restart
```

### **Important Files & Directories**

```
pypi-server/
├── docker-compose.yml          # Main server configuration
├── scripts/manage-users.sh     # User management script
├── /data/auth/.htpasswd        # User credentials file
├── /data/packages/             # Stored packages
└── /data/logs/                 # Server logs
```

### **External Dependencies**

- **AWS EC2**: `i-08438c82c8cffe7ae` (briefcase-pypi-server)
- **Route53**: `pypi.briefcasebrain.com` → EC2 instance
- **SSL**: Let's Encrypt automatic renewal
- **GitHub Actions**: Package publishing workflow

---

## 🚨 **Emergency Procedures**

### **Server Outage**

1. **Check AWS Console** - Verify EC2 instance status
2. **SSH Access** - Attempt to connect to server
3. **Restart Services** - `docker-compose restart`
4. **Check DNS** - Verify Route53 routing
5. **SSL Issues** - Check certificate validity
6. **Escalation** - Contact AWS support if infrastructure issue

### **Security Incident**

1. **Immediate Response:**
   - Change admin passwords
   - Review access logs for suspicious activity
   - Temporarily disable affected users if needed

2. **Investigation:**
   - Check server logs for unauthorized access
   - Review user activity patterns
   - Validate credential integrity

3. **Communication:**
   - Notify affected beta participants if credentials compromised
   - Provide new credentials if necessary
   - Document incident for future prevention

---

## 📞 **Support Escalation**

**Internal Team Contacts:**
- **DevOps Lead**: [Primary contact for server issues]
- **Security Team**: [Contact for security incidents]
- **Beta Program Manager**: [Contact for participant issues]

**External Support:**
- **AWS Support**: [For infrastructure issues]
- **Let's Encrypt**: [For SSL certificate issues]

---

**📝 Document Maintained by:** DevOps Team
**🔄 Last Updated:** [Current Date]
**📋 Review Schedule:** Monthly or as needed for beta program updates

🔐 **This document contains sensitive operational information. Restrict access to authorized team members only.**