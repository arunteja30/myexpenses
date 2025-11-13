from datetime import datetime

def format_date_for_input(date_string):
    """Convert ISO date string to YYYY-MM-DD format for HTML date input"""
    if not date_string:
        return ""
    try:
        # Handle both ISO format with and without timezone
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d')
    except:
        return ""

def format_date_display(date_string):
    """Convert ISO date string to readable format for display"""
    if not date_string:
        return ""
    try:
        # Handle both ISO format with and without timezone
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
            
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_string

def format_datetime_display(date_string):
    """Convert ISO datetime string to readable format for display"""
    if not date_string:
        return ""
    try:
        # Handle both ISO format with and without timezone
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
            
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_string
