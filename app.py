import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Make datetime available in templates
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    monthly_income = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expenses = db.relationship('Expense', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    expense_type = db.Column(db.String(20), default='wanted')  # 'wanted' or 'unwanted'
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_amount = db.Column(db.Float, default=100000.0)  # Default ₹1,00,000
    target_months = db.Column(db.Integer, default=3)  # 3 months
    current_savings = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        monthly_income = float(request.form.get('monthly_income', 0))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        user = User(username=username, email=email, monthly_income=monthly_income)
        user.set_password(password)
        
        # First user becomes admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        # Create default savings goal
        savings_goal = SavingsGoal(user_id=user.id)
        db.session.add(savings_goal)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get current month expenses
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    if current_user.is_admin:
        monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
            extract('month', Expense.date) == current_month,
            extract('year', Expense.date) == current_year
        ).scalar() or 0
        
        total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
        total_users = User.query.count()
    else:
        monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            extract('month', Expense.date) == current_month,
            extract('year', Expense.date) == current_year
        ).scalar() or 0
        
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id
        ).scalar() or 0
        total_users = None
    
    # Get recent expenses
    if current_user.is_admin:
        recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    else:
        recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    
    # Get savings data
    savings_goal = SavingsGoal.query.filter_by(user_id=current_user.id).first()
    if not savings_goal:
        savings_goal = SavingsGoal(user_id=current_user.id)
        db.session.add(savings_goal)
        db.session.commit()
    
    monthly_income = current_user.monthly_income
    monthly_savings = monthly_income - monthly_expenses
    savings_percentage = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
    
    return render_template('dashboard.html', 
                         monthly_expenses=monthly_expenses,
                         total_expenses=total_expenses,
                         monthly_income=monthly_income,
                         monthly_savings=monthly_savings,
                         savings_percentage=savings_percentage,
                         recent_expenses=recent_expenses,
                         total_users=total_users,
                         savings_goal=savings_goal)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        expense_type = request.form['expense_type']
        date_str = request.form['date']
        
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
        
        expense = Expense(
            user_id=current_user.id,
            amount=amount,
            category=category,
            description=description,
            expense_type=expense_type,
            date=date
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!')
        return redirect(url_for('expenses'))
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
    return render_template('add_expense.html', categories=categories)

@app.route('/expenses')
@login_required
def expenses():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if current_user.is_admin:
        expenses_query = Expense.query
    else:
        expenses_query = Expense.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    category = request.args.get('category')
    expense_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if category:
        expenses_query = expenses_query.filter(Expense.category == category)
    if expense_type:
        expenses_query = expenses_query.filter(Expense.expense_type == expense_type)
    if start_date:
        expenses_query = expenses_query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        expenses_query = expenses_query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    expenses_pagination = expenses_query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
    
    return render_template('expenses.html', 
                         expenses=expenses_pagination.items,
                         pagination=expenses_pagination,
                         categories=categories)

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Check permissions
    if not current_user.is_admin and expense.user_id != current_user.id:
        flash('You can only edit your own expenses')
        return redirect(url_for('expenses'))
    
    if request.method == 'POST':
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        expense.description = request.form['description']
        expense.expense_type = request.form['expense_type']
        date_str = request.form['date']
        expense.date = datetime.strptime(date_str, '%Y-%m-%d')
        
        db.session.commit()
        flash('Expense updated successfully!')
        return redirect(url_for('expenses'))
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Check permissions
    if not current_user.is_admin and expense.user_id != current_user.id:
        flash('You can only delete your own expenses')
        return redirect(url_for('expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!')
    return redirect(url_for('expenses'))

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/api/chart_data')
@login_required
def chart_data():
    chart_type = request.args.get('type', 'category')
    
    try:
        if chart_type == 'category':
            # Category breakdown
            if current_user.is_admin:
                category_data = db.session.query(
                    Expense.category,
                    func.sum(Expense.amount)
                ).group_by(Expense.category).all()
            else:
                category_data = db.session.query(
                    Expense.category,
                    func.sum(Expense.amount)
                ).filter_by(user_id=current_user.id).group_by(Expense.category).all()
            
            if not category_data:
                return jsonify({
                    'labels': ['No expenses yet'],
                    'data': [0]
                })
            
            return jsonify({
                'labels': [item[0] for item in category_data],
                'data': [float(item[1]) for item in category_data]
            })
        
        elif chart_type == 'monthly':
            # Monthly expenses for current year
            current_year = datetime.now().year
            if current_user.is_admin:
                monthly_data = db.session.query(
                    extract('month', Expense.date),
                    func.sum(Expense.amount)
                ).filter(
                    extract('year', Expense.date) == current_year
                ).group_by(extract('month', Expense.date)).all()
            else:
                monthly_data = db.session.query(
                    extract('month', Expense.date),
                    func.sum(Expense.amount)
                ).filter(
                    Expense.user_id == current_user.id,
                    extract('year', Expense.date) == current_year
                ).group_by(extract('month', Expense.date)).all()
            
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_amounts = [0] * 12
            for month, amount in monthly_data:
                monthly_amounts[int(month) - 1] = float(amount)
            
            return jsonify({
                'labels': months,
                'data': monthly_amounts
            })
        
        elif chart_type == 'expense_type':
            # Wanted vs Unwanted expenses
            if current_user.is_admin:
                type_data = db.session.query(
                    Expense.expense_type,
                    func.sum(Expense.amount)
                ).group_by(Expense.expense_type).all()
            else:
                type_data = db.session.query(
                    Expense.expense_type,
                    func.sum(Expense.amount)
                ).filter_by(user_id=current_user.id).group_by(Expense.expense_type).all()
            
            if not type_data:
                return jsonify({
                    'labels': ['No expenses yet'],
                    'data': [0]
                })
            
            return jsonify({
                'labels': [item[0].title() for item in type_data],
                'data': [float(item[1]) for item in type_data]
            })
        
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
            
    except Exception as e:
        print(f"Chart data error: {str(e)}")
        return jsonify({
            'labels': ['Error loading data'],
            'data': [0],
            'error': str(e)
        }), 500

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin only.')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    total_users = User.query.count()
    
    return render_template('admin.html', users=users, total_expenses=total_expenses, total_users=total_users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Access denied. Admin only.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        monthly_income = float(request.form.get('monthly_income', 0))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('add_user.html')
        
        user = User(username=username, email=email, monthly_income=monthly_income)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default savings goal
        savings_goal = SavingsGoal(user_id=user.id)
        db.session.add(savings_goal)
        db.session.commit()
        
        flash('User added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('add_user.html')

@app.route('/settings')
@login_required
def settings():
    savings_goal = SavingsGoal.query.filter_by(user_id=current_user.id).first()
    return render_template('settings.html', savings_goal=savings_goal)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_user.monthly_income = float(request.form['monthly_income'])
    db.session.commit()
    flash('Profile updated successfully!')
    return redirect(url_for('settings'))

@app.route('/update_savings_goal', methods=['POST'])
@login_required
def update_savings_goal():
    savings_goal = SavingsGoal.query.filter_by(user_id=current_user.id).first()
    if not savings_goal:
        savings_goal = SavingsGoal(user_id=current_user.id)
    
    savings_goal.target_amount = float(request.form['target_amount'])
    savings_goal.target_months = int(request.form['target_months'])
    
    db.session.add(savings_goal)
    db.session.commit()
    flash('Savings goal updated successfully!')
    return redirect(url_for('settings'))

@app.route('/api/savings_suggestions')
@login_required
def savings_suggestions():
    # Get current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    unwanted_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_type == 'unwanted',
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    savings_goal = SavingsGoal.query.filter_by(user_id=current_user.id).first()
    monthly_income = current_user.monthly_income
    
    suggestions = []
    
    # Basic suggestions
    if unwanted_expenses > 0:
        suggestions.append(f"You spent ₹{unwanted_expenses:.2f} on unwanted items this month. Try to reduce this by 50% to save ₹{unwanted_expenses * 0.5:.2f}.")
    
    if savings_goal:
        monthly_savings_needed = savings_goal.target_amount / savings_goal.target_months
        current_savings = monthly_income - monthly_expenses
        
        if current_savings < monthly_savings_needed:
            shortfall = monthly_savings_needed - current_savings
            suggestions.append(f"To reach your savings goal of ₹{savings_goal.target_amount:.2f} in {savings_goal.target_months} months, you need to save ₹{monthly_savings_needed:.2f} monthly. You're short by ₹{shortfall:.2f}.")
        else:
            suggestions.append(f"Great! You're on track to meet your savings goal. Keep it up!")
    
    if monthly_expenses > monthly_income * 0.8:
        suggestions.append("Your expenses are quite high (>80% of income). Consider reviewing your spending habits.")
    
    return jsonify({'suggestions': suggestions})

@app.route('/api/user_expenses/<int:user_id>')
@login_required
def user_expenses(user_id):
    # Only admin can access other users' data
    if not current_user.is_admin and user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id
    ).scalar() or 0
    
    return jsonify({'total_expenses': total_expenses})

@app.route('/add_sample_data')
@login_required
def add_sample_data():
    """Add sample data for testing (only for demo purposes)"""
    from datetime import datetime, timedelta
    import random
    
    # Only allow if user has no expenses yet
    existing_expenses = Expense.query.filter_by(user_id=current_user.id).count()
    if existing_expenses > 0:
        flash('Sample data already exists or you have expenses.')
        return redirect(url_for('dashboard'))
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare']
    descriptions = {
        'Food': ['Lunch', 'Dinner', 'Groceries', 'Coffee', 'Snacks'],
        'Transportation': ['Bus fare', 'Auto', 'Fuel', 'Parking', 'Taxi'],
        'Entertainment': ['Movie', 'Concert', 'Games', 'Books', 'Streaming'],
        'Shopping': ['Clothes', 'Electronics', 'Groceries', 'Gifts', 'Household'],
        'Bills': ['Electricity', 'Water', 'Internet', 'Phone', 'Rent'],
        'Healthcare': ['Medicine', 'Doctor visit', 'Checkup', 'Dental', 'Pharmacy']
    }
    
    # Create sample expenses for the last 3 months
    base_date = datetime.now()
    sample_expenses = []
    
    for i in range(30):  # 30 sample expenses
        days_back = random.randint(0, 90)  # Last 3 months
        expense_date = base_date - timedelta(days=days_back)
        
        category = random.choice(categories)
        description = random.choice(descriptions[category])
        amount = random.uniform(50, 500)
        expense_type = 'unwanted' if random.random() < 0.3 else 'wanted'  # 30% unwanted
        
        expense = Expense(
            user_id=current_user.id,
            amount=round(amount, 2),
            category=category,
            description=description,
            expense_type=expense_type,
            date=expense_date
        )
        sample_expenses.append(expense)
    
    db.session.add_all(sample_expenses)
    db.session.commit()
    
    flash('Sample data added successfully! You can now see charts and analytics.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
