#!/bin/bash

# User Management Script for Briefcase AI Private PyPI
# Manages user accounts for the private PyPI repository

set -e

HTPASSWD_FILE="auth/.htpasswd"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if htpasswd is installed
if ! command -v htpasswd &> /dev/null; then
    echo "❌ htpasswd is not installed. Please install it:"
    echo "   - Ubuntu/Debian: sudo apt-get install apache2-utils"
    echo "   - macOS: brew install httpd"
    echo "   - CentOS/RHEL: sudo yum install httpd-tools"
    exit 1
fi

# Ensure auth directory exists
mkdir -p auth

show_help() {
    echo "🔐 Briefcase AI Private PyPI User Management"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  add <username>           Add a new user (will prompt for password)"
    echo "  add-beta <company> <initials> Add beta participant with auto-generated credentials"
    echo "  remove <username>        Remove a user"
    echo "  change <username>        Change user password"
    echo "  list                     List all users"
    echo "  test <username> <password> Test user authentication"
    echo "  generate-password        Generate a secure password"
    echo "  status                   Show server status and statistics"
    echo "  help                     Show this help"
    echo ""
    echo "Beta Participant Management:"
    echo "  $0 add-beta acme jd      # Add beta user 'acme_jd' with auto-generated password"
    echo "  $0 test acme_jd password # Test authentication for beta user"
    echo "  $0 status                # Check server health and usage stats"
    echo ""
    echo "Examples:"
    echo "  $0 add admin             # Add admin user"
    echo "  $0 add developer         # Add developer user"
    echo "  $0 list                  # List all users"
    echo "  $0 remove old-user       # Remove a user"
}

add_user() {
    local username="$1"
    if [ -z "$username" ]; then
        echo "❌ Username required"
        echo "Usage: $0 add <username>"
        exit 1
    fi

    if [ ! -f "$HTPASSWD_FILE" ]; then
        echo "📝 Creating new password file..."
        htpasswd -c "$HTPASSWD_FILE" "$username"
    else
        if grep -q "^$username:" "$HTPASSWD_FILE"; then
            echo "⚠️  User '$username' already exists. Use 'change' to update password."
            exit 1
        fi
        htpasswd "$HTPASSWD_FILE" "$username"
    fi

    echo "✅ User '$username' added successfully"
}

remove_user() {
    local username="$1"
    if [ -z "$username" ]; then
        echo "❌ Username required"
        echo "Usage: $0 remove <username>"
        exit 1
    fi

    if [ ! -f "$HTPASSWD_FILE" ]; then
        echo "❌ Password file does not exist"
        exit 1
    fi

    if ! grep -q "^$username:" "$HTPASSWD_FILE"; then
        echo "❌ User '$username' not found"
        exit 1
    fi

    # Create backup
    cp "$HTPASSWD_FILE" "$HTPASSWD_FILE.bak"

    # Remove user
    grep -v "^$username:" "$HTPASSWD_FILE" > "$HTPASSWD_FILE.tmp" && mv "$HTPASSWD_FILE.tmp" "$HTPASSWD_FILE"

    echo "✅ User '$username' removed successfully"
}

change_password() {
    local username="$1"
    if [ -z "$username" ]; then
        echo "❌ Username required"
        echo "Usage: $0 change <username>"
        exit 1
    fi

    if [ ! -f "$HTPASSWD_FILE" ]; then
        echo "❌ Password file does not exist"
        exit 1
    fi

    if ! grep -q "^$username:" "$HTPASSWD_FILE"; then
        echo "❌ User '$username' not found"
        exit 1
    fi

    # Create backup
    cp "$HTPASSWD_FILE" "$HTPASSWD_FILE.bak"

    # Remove old entry and add new one
    grep -v "^$username:" "$HTPASSWD_FILE" > "$HTPASSWD_FILE.tmp"
    mv "$HTPASSWD_FILE.tmp" "$HTPASSWD_FILE"
    htpasswd "$HTPASSWD_FILE" "$username"

    echo "✅ Password for user '$username' changed successfully"
}

list_users() {
    if [ ! -f "$HTPASSWD_FILE" ]; then
        echo "❌ No users found (password file does not exist)"
        exit 1
    fi

    echo "👥 Current users:"
    while IFS=: read -r username hash; do
        echo "  - $username"
    done < "$HTPASSWD_FILE"
}

add_beta_user() {
    local company="$1"
    local initials="$2"

    if [ -z "$company" ] || [ -z "$initials" ]; then
        echo "❌ Company name and initials required"
        echo "Usage: $0 add-beta <company> <initials>"
        echo "Example: $0 add-beta acme jd  # Creates user 'acme_jd'"
        exit 1
    fi

    # Create username in format company_initials
    local username="${company}_${initials}"

    # Generate secure password
    local password=$(generate_secure_password)

    if [ ! -f "$HTPASSWD_FILE" ]; then
        echo "📝 Creating new password file..."
        echo "$password" | htpasswd -c -i "$HTPASSWD_FILE" "$username"
    else
        if grep -q "^$username:" "$HTPASSWD_FILE"; then
            echo "⚠️  User '$username' already exists. Use 'change' to update password."
            exit 1
        fi
        echo "$password" | htpasswd -i "$HTPASSWD_FILE" "$username"
    fi

    echo "✅ Beta participant '$username' added successfully"
    echo ""
    echo "📋 Beta Participant Credentials:"
    echo "   🏢 Company: $company"
    echo "   👤 Username: $username"
    echo "   🔑 Password: $password"
    echo ""
    echo "📦 Installation Command:"
    echo "pip install --index-url https://$username:$password@pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry"
    echo ""
    echo "🔍 Test authentication:"
    echo "$0 test $username $password"
    echo ""
    echo "⚠️  Store credentials securely and share via encrypted communication only!"
}

generate_secure_password() {
    # Generate a secure 16-character password with mixed case, numbers, and symbols
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-16
}

test_authentication() {
    local username="$1"
    local password="$2"

    if [ -z "$username" ] || [ -z "$password" ]; then
        echo "❌ Username and password required"
        echo "Usage: $0 test <username> <password>"
        exit 1
    fi

    echo "🔍 Testing authentication for user '$username'..."

    # Test local authentication file first
    if [ ! -f "$HTPASSWD_FILE" ]; then
        echo "❌ Password file does not exist"
        exit 1
    fi

    if ! grep -q "^$username:" "$HTPASSWD_FILE"; then
        echo "❌ User '$username' not found in password file"
        exit 1
    fi

    # Test HTTP authentication against the server
    if command -v curl &> /dev/null; then
        echo "📡 Testing HTTP authentication..."
        if curl -f -u "$username:$password" http://localhost:8080/simple/ >/dev/null 2>&1; then
            echo "✅ Local server authentication: SUCCESS"
        else
            echo "⚠️  Local server authentication: FAILED (server may not be running)"
        fi

        # Test against production domain if accessible
        if curl -f -u "$username:$password" https://pypi.briefcasebrain.com/simple/ >/dev/null 2>&1; then
            echo "✅ Production server authentication: SUCCESS"
        else
            echo "⚠️  Production server authentication: FAILED (check network/DNS)"
        fi
    else
        echo "⚠️  curl not available - cannot test HTTP authentication"
    fi

    echo "✅ User '$username' exists in password file"
}

show_status() {
    echo "📊 Briefcase AI Private PyPI Server Status"
    echo ""

    # Check if password file exists and show user count
    if [ -f "$HTPASSWD_FILE" ]; then
        local user_count=$(wc -l < "$HTPASSWD_FILE")
        echo "👥 Total Users: $user_count"
        echo "📁 Password File: $HTPASSWD_FILE"
    else
        echo "❌ No password file found"
    fi

    # Check server status
    echo ""
    echo "🐳 Docker Container Status:"
    if command -v docker &> /dev/null; then
        if docker ps --filter "name=briefcase-pypi-server" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -v NAMES; then
            echo "✅ PyPI server container is running"
        else
            echo "⚠️  PyPI server container is not running"
        fi
    else
        echo "⚠️  Docker not available"
    fi

    # Check local server accessibility
    echo ""
    echo "🔗 Server Accessibility:"
    if command -v curl &> /dev/null; then
        if curl -f http://localhost:8080 >/dev/null 2>&1; then
            echo "✅ Local server (port 8080): Accessible"
        else
            echo "❌ Local server (port 8080): Not accessible"
        fi

        if curl -f https://pypi.briefcasebrain.com >/dev/null 2>&1; then
            echo "✅ Production server: Accessible"
        else
            echo "❌ Production server: Not accessible"
        fi
    else
        echo "⚠️  curl not available for testing"
    fi

    # Show disk usage
    echo ""
    echo "💾 Storage Usage:"
    if [ -d "packages" ]; then
        local package_count=$(find packages -name "*.whl" -o -name "*.tar.gz" | wc -l)
        local package_size=$(du -sh packages 2>/dev/null | cut -f1)
        echo "📦 Packages: $package_count files ($package_size)"
    else
        echo "📦 No packages directory found"
    fi
}

# Main script logic
case "${1:-help}" in
    "add")
        add_user "$2"
        ;;
    "add-beta")
        add_beta_user "$2" "$3"
        ;;
    "remove")
        remove_user "$2"
        ;;
    "change")
        change_password "$2"
        ;;
    "list")
        list_users
        ;;
    "test")
        test_authentication "$2" "$3"
        ;;
    "generate-password")
        echo "🔑 Generated secure password: $(generate_secure_password)"
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac