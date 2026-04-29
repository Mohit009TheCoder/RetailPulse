"""
Helper utility functions
"""


def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"


def format_number(value):
    """Format number with thousand separators"""
    return f"{value:,}"
