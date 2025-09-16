#!/bin/bash

# AI-Powered Ecommerce Platform Setup Script

set -e  # Exit on any error

echo "🚀 Setting up AI-Powered Ecommerce Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p nginx/ssl
mkdir -p data/singlestore
mkdir -p logs

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Database Configuration
SINGLESTORE_HOST=singlestore
SINGLESTORE_PORT=3306
SINGLESTORE_USER=root
SINGLESTORE_PASSWORD=
SINGLESTORE_DATABASE=ecommerce_ai

# API Configuration
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration (Add your API key here)
OPENAI_API_KEY=

# External APIs (Optional)
STRIPE_SECRET_KEY=
SENDGRID_API_KEY=

# Agent Configuration
ENABLE_AUTO_PRICING=true
ENABLE_AUTO_INVENTORY=true
ENABLE_AUTO_RECOMMENDATIONS=true
PRICE_UPDATE_INTERVAL=3600
INVENTORY_CHECK_INTERVAL=1800

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
EOF
    echo "✅ Created .env file. Please add your OpenAI API key and other configuration."
else
    echo "✅ .env file already exists."
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service is not responding"
fi

if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
fi

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec backend python -c "
from backend.database.connection import init_database
try:
    init_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
"

# Create sample data
echo "📊 Creating sample data..."
docker-compose exec backend python scripts/create_sample_data.py

echo "🎉 Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   SingleStore Studio: http://localhost:8080"
echo ""
echo "🔑 Default admin credentials:"
echo "   Email: admin@example.com"
echo "   Password: admin123"
echo ""
echo "📝 Next steps:"
echo "   1. Add your OpenAI API key to the .env file"
echo "   2. Restart services: docker-compose restart"
echo "   3. Visit the admin panel to configure AI agents"
echo ""
echo "🛠️ Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose up -d --build"
