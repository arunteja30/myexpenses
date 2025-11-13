import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
from firebase_db import FirebaseUser, FirebaseExpense, FirebaseSavingsGoal
from collections import defaultdict
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Make datetime available in templates
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# Import and register template filters
from template_filters import format_date_for_input, format_date_display, format_datetime_display

app.jinja_env.filters['date_input'] = format_date_for_input
app.jinja_env.filters['date_display'] = format_date_display
app.jinja_env.filters['datetime_display'] = format_datetime_display

@login_manager.user_loader
def load_user(user_id):
    return FirebaseUser.get_by_id(user_id)

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
        user = FirebaseUser.get_by_username(username)
        
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
        
        if FirebaseUser.get_by_username(username):
            flash('Username already exists')
            return render_template('register.html')
        
        if FirebaseUser.get_by_email(email):
            flash('Email already exists')
            return render_template('register.html')
        
        # First user becomes admin
        is_admin = FirebaseUser.count() == 0
        
        user = FirebaseUser.create_user(username, email, password, monthly_income, is_admin)
        
        # Create default savings goal
        FirebaseSavingsGoal.create_goal(user.get_id())
        
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
    
    def calculate_monthly_expenses(expenses, current_month, current_year):
        total = 0
        for expense in expenses:
            expense_date = datetime.fromisoformat(expense.date.replace('Z', '+00:00'))
            if expense_date.month == current_month and expense_date.year == current_year:
                total += expense.amount
        return total
    
    def calculate_total_expenses(expenses):
        return sum(expense.amount for expense in expenses)
    
    if current_user.is_admin:
        all_expenses = FirebaseExpense.get_all_expenses()
        monthly_expenses = calculate_monthly_expenses(all_expenses, current_month, current_year)
        total_expenses = calculate_total_expenses(all_expenses)
        total_users = FirebaseUser.count()
        recent_expenses = FirebaseExpense.get_all_expenses(limit=5)
    else:
        user_expenses = FirebaseExpense.get_by_user_id(current_user.get_id())
        monthly_expenses = calculate_monthly_expenses(user_expenses, current_month, current_year)
        total_expenses = calculate_total_expenses(user_expenses)
        total_users = None
        recent_expenses = FirebaseExpense.get_by_user_id(current_user.get_id(), limit=5)
    
    # Get savings data
    savings_goal = FirebaseSavingsGoal.get_by_user_id(current_user.get_id())
    if not savings_goal:
        savings_goal = FirebaseSavingsGoal.create_goal(current_user.get_id())
    
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
        
        expense = FirebaseExpense.create_expense(
            user_id=current_user.get_id(),
            amount=amount,
            category=category,
            description=description,
            expense_type=expense_type,
            date=date
        )
        
        flash('Expense added successfully!')
        return redirect(url_for('expenses'))
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
    return render_template('add_expense.html', categories=categories)

@app.route('/expenses')
@login_required
def expenses():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Apply filters
    category = request.args.get('category')
    expense_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Convert string dates to date objects
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    
    # Get filtered expenses
    user_id = None if current_user.is_admin else current_user.get_id()
    all_expenses = FirebaseExpense.get_filtered_expenses(
        user_id=user_id,
        category=category,
        expense_type=expense_type,
        start_date=start_date_obj,
        end_date=end_date_obj,
        is_admin=current_user.is_admin
    )
    
    # Simple pagination
    total_expenses = len(all_expenses)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    expenses_page = all_expenses[start_idx:end_idx]
    
    # Create a simple pagination object
    class SimplePagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
    
    pagination = SimplePagination(page, per_page, total_expenses, expenses_page)
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
    
    return render_template('expenses.html', 
                         expenses=expenses_page,
                         pagination=pagination,
                         categories=categories)

@app.route('/edit_expense/<expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = FirebaseExpense.get_by_id(expense_id)
    if not expense:
        flash('Expense not found')
        return redirect(url_for('expenses'))
    
    # Check permissions
    if not current_user.is_admin and expense.user_id != current_user.get_id():
        flash('You can only edit your own expenses')
        return redirect(url_for('expenses'))
    
    if request.method == 'POST':
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        expense.description = request.form['description']
        expense.expense_type = request.form['expense_type']
        date_str = request.form['date']
        expense.date = datetime.strptime(date_str, '%Y-%m-%d').isoformat()
        
        expense.save()
        flash('Expense updated successfully!')
        return redirect(url_for('expenses'))
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete_expense/<expense_id>')
@login_required
def delete_expense(expense_id):
    expense = FirebaseExpense.get_by_id(expense_id)
    if not expense:
        flash('Expense not found')
        return redirect(url_for('expenses'))
    
    # Check permissions
    if not current_user.is_admin and expense.user_id != current_user.get_id():
        flash('You can only delete your own expenses')
        return redirect(url_for('expenses'))
    
    expense.delete()
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
        if current_user.is_admin:
            expenses = FirebaseExpense.get_all_expenses()
        else:
            expenses = FirebaseExpense.get_by_user_id(current_user.get_id())
        
        if chart_type == 'category':
            # Category breakdown
            category_totals = defaultdict(float)
            for expense in expenses:
                category_totals[expense.category] += expense.amount
            
            if not category_totals:
                return jsonify({
                    'labels': ['No expenses yet'],
                    'data': [0]
                })
            
            return jsonify({
                'labels': list(category_totals.keys()),
                'data': list(category_totals.values())
            })
        
        elif chart_type == 'monthly':
            # Monthly expenses for current year
            current_year = datetime.now().year
            monthly_totals = defaultdict(float)
            
            for expense in expenses:
                expense_date = datetime.fromisoformat(expense.date.replace('Z', '+00:00'))
                if expense_date.year == current_year:
                    monthly_totals[expense_date.month] += expense.amount
            
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_amounts = [monthly_totals.get(i, 0) for i in range(1, 13)]
            
            return jsonify({
                'labels': months,
                'data': monthly_amounts
            })
        
        elif chart_type == 'expense_type':
            # Wanted vs Unwanted expenses
            type_totals = defaultdict(float)
            for expense in expenses:
                type_totals[expense.expense_type] += expense.amount
            
            if not type_totals:
                return jsonify({
                    'labels': ['No expenses yet'],
                    'data': [0]
                })
            
            return jsonify({
                'labels': [t.title() for t in type_totals.keys()],
                'data': list(type_totals.values())
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
    
    users = FirebaseUser.get_all_users()
    all_expenses = FirebaseExpense.get_all_expenses()
    total_expenses = sum(expense.amount for expense in all_expenses)
    total_users = FirebaseUser.count()
    
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
        
        if FirebaseUser.get_by_username(username):
            flash('Username already exists')
            return render_template('add_user.html')
        
        user = FirebaseUser.create_user(username, email, password, monthly_income)
        
        # Create default savings goal
        FirebaseSavingsGoal.create_goal(user.get_id())
        
        flash('User added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('add_user.html')

@app.route('/settings')
@login_required
def settings():
    savings_goal = FirebaseSavingsGoal.get_by_user_id(current_user.get_id())
    return render_template('settings.html', savings_goal=savings_goal)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_user.monthly_income = float(request.form['monthly_income'])
    current_user.save()
    flash('Profile updated successfully!')
    return redirect(url_for('settings'))

@app.route('/update_savings_goal', methods=['POST'])
@login_required
def update_savings_goal():
    savings_goal = FirebaseSavingsGoal.get_by_user_id(current_user.get_id())
    if not savings_goal:
        savings_goal = FirebaseSavingsGoal.create_goal(current_user.get_id())
    
    savings_goal.target_amount = float(request.form['target_amount'])
    savings_goal.target_months = int(request.form['target_months'])
    
    savings_goal.save()
    flash('Savings goal updated successfully!')
    return redirect(url_for('settings'))

@app.route('/api/savings_suggestions')
@login_required
def savings_suggestions():
    # Get current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    user_expenses = FirebaseExpense.get_by_user_id(current_user.get_id())
    
    monthly_expenses = 0
    unwanted_expenses = 0
    
    for expense in user_expenses:
        expense_date = datetime.fromisoformat(expense.date.replace('Z', '+00:00'))
        if expense_date.month == current_month and expense_date.year == current_year:
            monthly_expenses += expense.amount
            if expense.expense_type == 'unwanted':
                unwanted_expenses += expense.amount
    
    savings_goal = FirebaseSavingsGoal.get_by_user_id(current_user.get_id())
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

@app.route('/api/user_expenses/<user_id>')
@login_required
def user_expenses(user_id):
    # Only admin can access other users' data
    if not current_user.is_admin and user_id != current_user.get_id():
        return jsonify({'error': 'Unauthorized'}), 403
    
    user_expenses_list = FirebaseExpense.get_by_user_id(user_id)
    total_expenses = sum(expense.amount for expense in user_expenses_list)
    
    return jsonify({'total_expenses': total_expenses})

@app.route('/admin/delete_user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    if user_id == current_user.get_id():
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    try:
        user = FirebaseUser.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user's expenses first
        FirebaseExpense.delete_by_user_id(user_id)
        
        # Delete user's savings goals
        FirebaseSavingsGoal.delete_by_user_id(user_id)
        
        # Delete user
        user.delete()
        
        return jsonify({'success': True, 'message': f'User {user.username} deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user = FirebaseUser.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Update user fields
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'monthly_income' in data:
            user.monthly_income = float(data['monthly_income'])
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        
        user.save()
        return jsonify({'success': True, 'message': 'User updated successfully'})
    
    # GET request - return user data
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'monthly_income': user.monthly_income,
        'is_admin': user.is_admin
    })

@app.route('/admin/reset_password/<user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user = FirebaseUser.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    new_password = data.get('password', 'password123')  # Default password
    
    # Hash the new password
    user.password = generate_password_hash(new_password)
    user.save()
    
    return jsonify({'success': True, 'message': f'Password reset to: {new_password}'})

@app.route('/export_expenses')
@login_required
def export_expenses():
    """Export expenses based on current filters"""
    try:
        # Get filter parameters from URL
        category = request.args.get('category', '')
        expense_type = request.args.get('type', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Convert string dates to date objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        # Get filtered expenses
        user_id = None if current_user.is_admin else current_user.get_id()
        expenses = FirebaseExpense.get_filtered_expenses(
            user_id=user_id,
            category=category,
            expense_type=expense_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            is_admin=current_user.is_admin
        )
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        if current_user.is_admin:
            writer.writerow([
                'User ID', 'Expense ID', 'Amount', 'Category', 
                'Description', 'Type', 'Date', 'Created At'
            ])
        else:
            writer.writerow([
                'Expense ID', 'Amount', 'Category', 'Description', 
                'Type', 'Date', 'Created At'
            ])
        
        # Write expense data
        for expense in expenses:
            if current_user.is_admin:
                writer.writerow([
                    expense.user_id,
                    expense.id,
                    expense.amount,
                    expense.category,
                    expense.description or '',
                    expense.expense_type,
                    datetime.fromisoformat(expense.date.replace('Z', '+00:00')).strftime('%Y-%m-%d'),
                    datetime.fromisoformat(expense.created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                ])
            else:
                writer.writerow([
                    expense.id,
                    expense.amount,
                    expense.category,
                    expense.description or '',
                    expense.expense_type,
                    datetime.fromisoformat(expense.date.replace('Z', '+00:00')).strftime('%Y-%m-%d'),
                    datetime.fromisoformat(expense.created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # Create response
        output.seek(0)
        filename_prefix = 'all_expenses' if current_user.is_admin else 'my_expenses'
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        flash(f'Export failed: {str(e)}')
        return redirect(url_for('expenses'))

@app.route('/export_user_data_csv')
@login_required
def export_user_data_csv():
    """Export current user's data to CSV format"""
    try:
        # Get user's expenses and savings goals
        expenses = FirebaseExpense.get_by_user_id(current_user.get_id())
        savings_goals = FirebaseSavingsGoal.get_all_by_user_id(current_user.get_id())
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # User information section
        writer.writerow(['=== USER INFORMATION ==='])
        writer.writerow(['Username', 'Email', 'Monthly Income', 'Member Since'])
        writer.writerow([
            current_user.username,
            current_user.email,
            current_user.monthly_income,
            datetime.fromisoformat(current_user.created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
        ])
        writer.writerow([])  # Empty row
        
        # Savings goals section
        writer.writerow(['=== SAVINGS GOALS ==='])
        if savings_goals:
            writer.writerow(['Goal ID', 'Target Amount', 'Target Months', 'Created Date'])
            for goal in savings_goals:
                writer.writerow([
                    goal.id,
                    goal.target_amount,
                    goal.target_months,
                    datetime.fromisoformat(goal.created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                ])
        else:
            writer.writerow(['No savings goals found'])
        writer.writerow([])  # Empty row
        
        # Expenses section
        writer.writerow(['=== EXPENSES ==='])
        if expenses:
            writer.writerow(['Expense ID', 'Amount', 'Category', 'Description', 'Type', 'Date', 'Created At'])
            for expense in expenses:
                writer.writerow([
                    expense.id,
                    expense.amount,
                    expense.category,
                    expense.description or '',
                    expense.expense_type,
                    datetime.fromisoformat(expense.date.replace('Z', '+00:00')).strftime('%Y-%m-%d'),
                    datetime.fromisoformat(expense.created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                ])
        else:
            writer.writerow(['No expenses found'])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=my_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        flash(f'Export failed: {str(e)}')
        return redirect(url_for('settings'))

@app.route('/export_user_data_json')
@login_required
def export_user_data_json():
    """Export current user's data to JSON format"""
    try:
        # Get user's expenses and savings goals
        expenses = FirebaseExpense.get_by_user_id(current_user.get_id())
        savings_goals = FirebaseSavingsGoal.get_all_by_user_id(current_user.get_id())
        
        # Prepare data structure
        data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'export_version': '1.0',
                'app_name': 'Expense Manager'
            },
            'user_info': {
                'id': current_user.get_id(),
                'username': current_user.username,
                'email': current_user.email,
                'monthly_income': float(current_user.monthly_income),
                'is_admin': current_user.is_admin,
                'member_since': current_user.created_at
            },
            'savings_goals': [
                {
                    'id': goal.id,
                    'target_amount': float(goal.target_amount),
                    'target_months': goal.target_months,
                    'created_at': goal.created_at
                }
                for goal in savings_goals
            ],
            'expenses': [
                {
                    'id': expense.id,
                    'amount': float(expense.amount),
                    'category': expense.category,
                    'description': expense.description,
                    'expense_type': expense.expense_type,
                    'date': expense.date,
                    'created_at': expense.created_at
                }
                for expense in expenses
            ],
            'summary': {
                'total_expenses': len(expenses),
                'total_amount': sum(float(expense.amount) for expense in expenses),
                'total_savings_goals': len(savings_goals),
                'categories': list(set(expense.category for expense in expenses)) if expenses else [],
                'date_range': {
                    'earliest': min(expense.date for expense in expenses) if expenses else None,
                    'latest': max(expense.date for expense in expenses) if expenses else None
                }
            }
        }
        
        # Create JSON response
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        response = make_response(json_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=my_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return response
        
    except Exception as e:
        flash(f'Export failed: {str(e)}')
        return redirect(url_for('settings'))

@app.route('/clear_user_data', methods=['POST'])
@login_required
def clear_user_data():
    """Clear all user's expense data"""
    try:
        # Delete user's expenses
        FirebaseExpense.delete_by_user_id(current_user.get_id())
        
        # Delete user's savings goals
        FirebaseSavingsGoal.delete_by_user_id(current_user.get_id())
        
        flash('All your data has been successfully deleted.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Failed to clear data: {str(e)}', 'error')
        return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
