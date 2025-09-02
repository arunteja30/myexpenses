# 💰 Smart Expense Manager

A modern, mobile-first expense tracking application built with Flask, featuring Progressive Web App (PWA) capabilities and comprehensive financial management tools.

## 🌟 Features

### Core Functionality
- **👥 Multi-User Support**: Admin and family member accounts
- **💸 Expense Tracking**: Add, edit, delete expenses with categories
- **📊 Analytics**: Beautiful charts and financial insights
- **🎯 Savings Goals**: Set and track ₹1,00,000 quarterly goals
- **🔍 Smart Categories**: Separate "wanted" vs "unwanted" expenses

### Mobile-First Design
- **📱 Responsive UI**: Bootstrap 5 with mobile-first approach
- **🔄 PWA Support**: Install on home screen, offline functionality
- **👆 Touch-Friendly**: Large buttons, swipe gestures
- **🌓 Dark/Light Mode**: Comfortable viewing in any lighting
- **⚡ Fast Loading**: Optimized for mobile networks

### Advanced Features
- **📈 Visual Reports**: Category breakdowns, monthly trends
- **💡 Smart Suggestions**: AI-powered savings recommendations
- **🏠 Admin Dashboard**: Family expense overview and management
- **📤 Data Export**: CSV/JSON export capabilities
- **🔒 Secure Authentication**: Password hashing and session management

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or download the project**
   ```bash
   cd expense-calculator
   ```

2. **Run the setup script**
   ```bash
   ./run.sh
   ```
   
   Or manually:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the application
   python3 app.py
   ```

3. **Access the application**
   - Desktop: http://localhost:5000
   - Mobile: http://YOUR_IP_ADDRESS:5000

### First Time Setup

1. **Register** the first user (automatically becomes admin)
2. **Set your monthly income** for accurate savings calculations
3. **Add family members** through the admin panel
4. **Start tracking expenses** immediately!

## 📱 Mobile Installation

### iOS (Safari)
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add"

### Android (Chrome)
1. Open the app in Chrome
2. Tap the menu (three dots)
3. Select "Add to Home screen"
4. Tap "Add"

## 🏗️ Project Structure

```
expense-calculator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── run.sh                # Startup script
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── dashboard.html    # Main dashboard
│   ├── add_expense.html  # Expense entry form
│   ├── expenses.html     # Expense listing
│   ├── reports.html      # Analytics and charts
│   ├── settings.html     # User preferences
│   └── admin.html        # Admin panel
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── app.js        # PWA and app logic
│   ├── icons/            # PWA icons
│   ├── manifest.json     # PWA manifest
│   └── sw.js             # Service worker
└── expenses.db           # SQLite database (created on first run)
```

## 💡 Usage Examples

### Adding Expenses
1. Click "Add Expense" from dashboard or bottom navigation
2. Enter amount, select category, add description
3. Mark as "Wanted" (necessary) or "Unwanted" (avoidable)
4. Use quick-add buttons for common expenses

### Viewing Analytics
1. Go to "Reports" section
2. Switch between category, monthly, and type views
3. View top spending categories and savings insights

### Setting Savings Goals
1. Go to Settings
2. Update your savings goal (default: ₹1,00,000 in 3 months)
3. Monitor progress on the dashboard

### Admin Functions
1. Access Admin panel (admin users only)
2. Add/manage family members
3. View system-wide statistics
4. Export data for all users

## 🎨 Customization

### Themes
- The app supports automatic dark/light mode switching
- Theme preference is saved locally
- Respects system dark mode settings

### Categories
Default categories include:
- Food & Dining
- Transportation
- Entertainment
- Shopping
- Bills & Utilities
- Healthcare
- Education
- Other

### Savings Goals
- Customizable target amounts
- Flexible time periods (1-12 months)
- Automatic progress tracking
- Smart recommendations

## 🔧 Technical Details

### Technology Stack
- **Backend**: Flask 2.3+ (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Chart.js
- **PWA**: Service Worker, Web App Manifest
- **Authentication**: Flask-Login with password hashing

### PWA Features
- **Offline Support**: Cache critical resources
- **Installation**: Add to home screen on mobile
- **Background Sync**: Sync data when connection returns
- **Push Notifications**: (Future enhancement)

### Performance
- Mobile-first responsive design
- Lazy loading for better performance
- Compressed assets and optimized images
- Fast SQLite database queries

## 📊 Database Schema

### Users Table
- id, username, email, password_hash
- is_admin, monthly_income, created_at

### Expenses Table
- id, user_id, amount, category, description
- expense_type (wanted/unwanted), date, created_at

### Savings Goals Table
- id, user_id, target_amount, target_months
- current_savings, created_at

## 🔐 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection (Flask-WTF)
- Input validation and sanitization
- Admin-only routes protection

## 🚀 Deployment

### Local Development
```bash
./run.sh
```

### Production Deployment
1. Set up a proper web server (nginx, Apache)
2. Use a WSGI server (Gunicorn, uWSGI)
3. Configure environment variables
4. Set up SSL/TLS certificates
5. Use a production database (PostgreSQL, MySQL)

### Environment Variables
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="your-database-url"
export FLASK_ENV="production"
```

## 🔮 Future Enhancements

### Planned Features
- **📸 Receipt Scanning**: Camera integration for receipt capture
- **🔔 Smart Notifications**: Spending alerts and reminders
- **📱 Mobile App**: Native iOS/Android applications
- **🌍 Multi-Currency**: Support for different currencies
- **📈 Advanced Analytics**: ML-powered spending predictions
- **🔄 Bank Integration**: Automatic transaction import
- **👫 Expense Sharing**: Split bills and shared expenses

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

### Common Issues

**Q: App won't start?**
A: Ensure Python 3.7+ is installed and run `./run.sh`

**Q: Can't add to home screen?**
A: Make sure you're using a modern browser and the app is served over HTTPS in production

**Q: Charts not loading?**
A: Check your internet connection for Chart.js CDN

**Q: Lost admin access?**
A: Delete `expenses.db` and restart - first user becomes admin

### Getting Help
- Check the console for error messages
- Ensure all dependencies are installed
- Verify Python version compatibility
- Test in different browsers

## 🏆 Key Benefits

✅ **Mobile-Optimized**: Perfect for on-the-go expense tracking  
✅ **Family-Friendly**: Multi-user support with admin controls  
✅ **Savings-Focused**: Built-in goal tracking and recommendations  
✅ **Privacy-First**: All data stored locally, no external services  
✅ **PWA-Ready**: Install like a native app on any device  
✅ **Beautiful UI**: Modern, clean interface with dark mode  
✅ **Fast & Responsive**: Optimized for performance on all devices  

---

**Start tracking your expenses smartly today! 🎯**
