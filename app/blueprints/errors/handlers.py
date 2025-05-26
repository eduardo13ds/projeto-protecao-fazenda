"""
Error handlers for the application.
"""
from flask import Blueprint, render_template

# Create blueprint
errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors.
    
    Args:
        error: The error object.
        
    Returns:
        tuple: A tuple containing the rendered template and the HTTP status code.
    """
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error errors.
    
    Args:
        error: The error object.
        
    Returns:
        tuple: A tuple containing the rendered template and the HTTP status code.
    """
    return render_template('errors/500.html'), 500