#!/bin/bash

# Expense Manager Startup Script

echo "🚀 Starting Expense Manager..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting the application..."
echo "   📱 Mobile-optimized interface"
echo "   💾 PWA capabilities enabled"
echo "   🔄 Auto-refresh for real-time updates"
echo ""
echo "🏠 Access your app at: http://localhost:5000"
echo "📱 On mobile: http://YOUR_IP:5000"
echo ""
echo "💡 Tip: Add to home screen for the best experience!"
echo ""

# Start the application
python3 app.py
