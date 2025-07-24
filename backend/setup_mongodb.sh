#!/bin/bash

# MongoDB Setup Script for Model Myself
# This script sets up MongoDB locally for document storage

set -e

echo "🚀 Setting up MongoDB for Model Myself..."

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "MongoDB not found. Installing MongoDB..."
    
    # macOS installation
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing MongoDB on macOS..."
        if ! command -v brew &> /dev/null; then
            echo "Error: Homebrew is required to install MongoDB on macOS"
            echo "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
        
        # Install MongoDB
        brew tap mongodb/brew
        brew install mongodb-community
        
        # Start MongoDB service
        brew services start mongodb/brew/mongodb-community
        
    # Linux installation
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing MongoDB on Linux..."
        
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            # Import MongoDB public key
            curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
                sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
                --dearmor
            
            # Add MongoDB repository
            echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
                sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
            
            # Update package list and install
            sudo apt-get update
            sudo apt-get install -y mongodb-org
            
            # Start MongoDB service
            sudo systemctl start mongod
            sudo systemctl enable mongod
            
        # Red Hat/CentOS/Fedora
        elif command -v yum &> /dev/null; then
            # Create MongoDB repository file
            cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc
EOF
            
            # Install MongoDB
            sudo yum install -y mongodb-org
            
            # Start MongoDB service
            sudo systemctl start mongod
            sudo systemctl enable mongod
        fi
        
    else
        echo "Unsupported operating system: $OSTYPE"
        echo "Please install MongoDB manually: https://docs.mongodb.com/manual/installation/"
        exit 1
    fi
    
else
    echo "✅ MongoDB is already installed"
fi

# Wait for MongoDB to start
echo "⏳ Waiting for MongoDB to start..."
sleep 5

# Test MongoDB connection
echo "🔍 Testing MongoDB connection..."
if mongosh --eval "db.runCommand('ping').ok" > /dev/null 2>&1; then
    echo "✅ MongoDB is running successfully!"
else
    echo "❌ MongoDB connection failed"
    echo "Please check MongoDB installation and try again"
    exit 1
fi

# Create database and collection
echo "🗃️ Setting up Model Myself database..."
mongosh model_myself --eval "
    // Create the documents collection
    db.createCollection('documents');
    
    // Create indexes for better performance
    db.documents.createIndex({ 'filename': 1 });
    db.documents.createIndex({ 'upload_date': -1 });
    db.documents.createIndex({ 'file_type': 1 });
    db.documents.createIndex({ 'searchable_content': 'text' });
    
    print('✅ Database setup complete!');
"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd "$(dirname "$0")"
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete! MongoDB is ready for Model Myself."
echo ""
echo "Next steps:"
echo "1. Start the backend: python main.py"
echo "2. Start the frontend: npm start (from the main directory)"
echo "3. Open http://localhost:3001 in your browser"
echo "4. Backend API will be available at http://localhost:8088"
echo ""
echo "MongoDB connection details:"
echo "- URL: mongodb://localhost:27017"
echo "- Database: model_myself"
echo "- Collection: documents"
echo ""
echo "To check MongoDB status: mongosh model_myself --eval 'db.stats()'"
echo "To view MongoDB logs: tail -f /usr/local/var/log/mongodb/mongo.log (macOS)" 