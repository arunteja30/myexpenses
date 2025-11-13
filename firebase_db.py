from datetime import datetime
import uuid
from firebase_config import database, get_admin_db
from werkzeug.security import generate_password_hash, check_password_hash

class FirebaseUser:
    def __init__(self, user_data=None, uid=None):
        if user_data:
            self.id = user_data.get('id', uid)
            self.uid = uid or user_data.get('uid')
            self.username = user_data.get('username', '')
            self.email = user_data.get('email', '')
            self.password_hash = user_data.get('password_hash', '')
            self.is_admin = user_data.get('is_admin', False)
            self.monthly_income = float(user_data.get('monthly_income', 0.0))
            self.created_at = user_data.get('created_at', datetime.utcnow().isoformat())
        else:
            self.id = None
            self.uid = uid
            self.username = ''
            self.email = ''
            self.password_hash = ''
            self.is_admin = False
            self.monthly_income = 0.0
            self.created_at = datetime.utcnow().isoformat()
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.uid) if self.uid else str(self.id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'monthly_income': self.monthly_income,
            'created_at': self.created_at
        }
    
    @staticmethod
    def create_user(username, email, password, monthly_income=0.0, is_admin=False):
        user_id = str(uuid.uuid4())
        user = FirebaseUser()
        user.id = user_id
        user.username = username
        user.email = email
        user.set_password(password)
        user.is_admin = is_admin
        user.monthly_income = monthly_income
        user.created_at = datetime.utcnow().isoformat()
        
        # Save to Firebase
        database.child("users").child(user_id).set(user.to_dict())
        return user
    
    @staticmethod
    def get_by_username(username):
        users = database.child("users").get()
        if users.val():
            for uid, user_data in users.val().items():
                if user_data.get('username') == username:
                    return FirebaseUser(user_data, uid)
        return None
    
    @staticmethod
    def get_by_email(email):
        users = database.child("users").get()
        if users.val():
            for uid, user_data in users.val().items():
                if user_data.get('email') == email:
                    return FirebaseUser(user_data, uid)
        return None
    
    @staticmethod
    def get_by_id(user_id):
        user_data = database.child("users").child(user_id).get()
        if user_data.val():
            return FirebaseUser(user_data.val(), user_id)
        return None
    
    @staticmethod
    def get_all_users():
        users = database.child("users").get()
        user_list = []
        if users.val():
            for uid, user_data in users.val().items():
                user_list.append(FirebaseUser(user_data, uid))
        return user_list
    
    @staticmethod
    def count():
        users = database.child("users").get()
        return len(users.val()) if users.val() else 0
    
    def save(self):
        database.child("users").child(self.get_id()).set(self.to_dict())
    
    def delete(self):
        database.child("users").child(self.get_id()).delete()

class FirebaseExpense:
    def __init__(self, expense_data=None, expense_id=None):
        if expense_data:
            self.id = expense_data.get('id', expense_id)
            self.user_id = expense_data.get('user_id', '')
            self.amount = float(expense_data.get('amount', 0.0))
            self.category = expense_data.get('category', '')
            self.description = expense_data.get('description', '')
            self.expense_type = expense_data.get('expense_type', 'wanted')
            self.date = expense_data.get('date', datetime.utcnow().isoformat())
            self.created_at = expense_data.get('created_at', datetime.utcnow().isoformat())
        else:
            self.id = expense_id
            self.user_id = ''
            self.amount = 0.0
            self.category = ''
            self.description = ''
            self.expense_type = 'wanted'
            self.date = datetime.utcnow().isoformat()
            self.created_at = datetime.utcnow().isoformat()
    
    @property
    def user(self):
        """Get the user object for this expense"""
        if hasattr(self, '_user'):
            return self._user
        self._user = FirebaseUser.get_by_id(self.user_id)
        return self._user
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'expense_type': self.expense_type,
            'date': self.date,
            'created_at': self.created_at
        }
    
    @staticmethod
    def create_expense(user_id, amount, category, description='', expense_type='wanted', date=None):
        expense_id = str(uuid.uuid4())
        expense = FirebaseExpense()
        expense.id = expense_id
        expense.user_id = user_id
        expense.amount = amount
        expense.category = category
        expense.description = description
        expense.expense_type = expense_type
        expense.date = date.isoformat() if date else datetime.utcnow().isoformat()
        expense.created_at = datetime.utcnow().isoformat()
        
        # Save to Firebase
        database.child("expenses").child(expense_id).set(expense.to_dict())
        return expense
    
    @staticmethod
    def get_by_id(expense_id):
        expense_data = database.child("expenses").child(expense_id).get()
        if expense_data.val():
            return FirebaseExpense(expense_data.val(), expense_id)
        return None
    
    @staticmethod
    def get_by_user_id(user_id, limit=None, order_by='created_at'):
        expenses = database.child("expenses").get()
        expense_list = []
        if expenses.val():
            for expense_id, expense_data in expenses.val().items():
                if expense_data.get('user_id') == user_id:
                    expense_list.append(FirebaseExpense(expense_data, expense_id))
        
        # Sort by date (newest first)
        expense_list.sort(key=lambda x: x.date, reverse=True)
        
        if limit:
            expense_list = expense_list[:limit]
        
        return expense_list
    
    @staticmethod
    def get_all_expenses(limit=None):
        expenses = database.child("expenses").get()
        expense_list = []
        if expenses.val():
            for expense_id, expense_data in expenses.val().items():
                expense_list.append(FirebaseExpense(expense_data, expense_id))
        
        # Sort by date (newest first)
        expense_list.sort(key=lambda x: x.date, reverse=True)
        
        if limit:
            expense_list = expense_list[:limit]
        
        return expense_list
    
    @staticmethod
    def get_filtered_expenses(user_id=None, category=None, expense_type=None, start_date=None, end_date=None, is_admin=False):
        expenses = database.child("expenses").get()
        expense_list = []
        
        if expenses.val():
            for expense_id, expense_data in expenses.val().items():
                expense = FirebaseExpense(expense_data, expense_id)
                
                # Apply filters
                if not is_admin and user_id and expense.user_id != user_id:
                    continue
                
                if category and expense.category != category:
                    continue
                
                if expense_type and expense.expense_type != expense_type:
                    continue
                
                if start_date:
                    expense_date = datetime.fromisoformat(expense.date.replace('Z', '+00:00'))
                    if expense_date.date() < start_date:
                        continue
                
                if end_date:
                    expense_date = datetime.fromisoformat(expense.date.replace('Z', '+00:00'))
                    if expense_date.date() > end_date:
                        continue
                
                expense_list.append(expense)
        
        # Sort by date (newest first)
        expense_list.sort(key=lambda x: x.date, reverse=True)
        return expense_list
    
    def save(self):
        database.child("expenses").child(self.id).set(self.to_dict())
    
    def delete(self):
        database.child("expenses").child(self.id).delete()
    
    @staticmethod
    def delete_by_user_id(user_id):
        expenses = database.child("expenses").get()
        if expenses.val():
            for expense_id, expense_data in expenses.val().items():
                if expense_data.get('user_id') == user_id:
                    database.child("expenses").child(expense_id).delete()

class FirebaseSavingsGoal:
    def __init__(self, goal_data=None, goal_id=None):
        if goal_data:
            self.id = goal_data.get('id', goal_id)
            self.user_id = goal_data.get('user_id', '')
            self.target_amount = float(goal_data.get('target_amount', 100000.0))
            self.target_months = int(goal_data.get('target_months', 3))
            self.current_savings = float(goal_data.get('current_savings', 0.0))
            self.created_at = goal_data.get('created_at', datetime.utcnow().isoformat())
        else:
            self.id = goal_id
            self.user_id = ''
            self.target_amount = 100000.0
            self.target_months = 3
            self.current_savings = 0.0
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_amount': self.target_amount,
            'target_months': self.target_months,
            'current_savings': self.current_savings,
            'created_at': self.created_at
        }
    
    @staticmethod
    def create_goal(user_id, target_amount=100000.0, target_months=3, current_savings=0.0):
        goal_id = str(uuid.uuid4())
        goal = FirebaseSavingsGoal()
        goal.id = goal_id
        goal.user_id = user_id
        goal.target_amount = target_amount
        goal.target_months = target_months
        goal.current_savings = current_savings
        goal.created_at = datetime.utcnow().isoformat()
        
        # Save to Firebase
        database.child("savings_goals").child(goal_id).set(goal.to_dict())
        return goal
    
    @staticmethod
    def get_by_user_id(user_id):
        goals = database.child("savings_goals").get()
        if goals.val():
            for goal_id, goal_data in goals.val().items():
                if goal_data.get('user_id') == user_id:
                    return FirebaseSavingsGoal(goal_data, goal_id)
        return None
    
    @staticmethod
    def get_all_by_user_id(user_id):
        goals = database.child("savings_goals").get()
        goal_list = []
        if goals.val():
            for goal_id, goal_data in goals.val().items():
                if goal_data.get('user_id') == user_id:
                    goal_list.append(FirebaseSavingsGoal(goal_data, goal_id))
        return goal_list
    
    def save(self):
        database.child("savings_goals").child(self.id).set(self.to_dict())
    
    def delete(self):
        database.child("savings_goals").child(self.id).delete()
    
    @staticmethod
    def delete_by_user_id(user_id):
        goals = database.child("savings_goals").get()
        if goals.val():
            for goal_id, goal_data in goals.val().items():
                if goal_data.get('user_id') == user_id:
                    database.child("savings_goals").child(goal_id).delete()
