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
    echo "  remove <username>        Remove a user"
    echo "  change <username>        Change user password"
    echo "  list                     List all users"
    echo "  generate-token <username> Generate API token for user"
    echo "  help                     Show this help"
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

generate_token() {
    local username="$1"
    if [ -z "$username" ]; then
        echo "❌ Username required"
        echo "Usage: $0 generate-token <username>"
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

    # Generate a simple token (in production, use proper token generation)
    local token=$(openssl rand -hex 32)
    local token_file="auth/tokens/${username}.token"

    mkdir -p auth/tokens
    echo "$token" > "$token_file"

    echo "🔑 API Token generated for '$username':"
    echo "   Token: $token"
    echo "   Saved to: $token_file"
    echo ""
    echo "📝 Add to ~/.pypirc:"
    echo "[distutils]"
    echo "index-servers = briefcase-ai"
    echo ""
    echo "[briefcase-ai]"
    echo "repository = https://pypi.briefcasebrain.com/"
    echo "username = __token__"
    echo "password = $token"
}

# Main script logic
case "${1:-help}" in
    "add")
        add_user "$2"
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
    "generate-token")
        generate_token "$2"
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