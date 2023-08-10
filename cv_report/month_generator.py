# Standard library imports
from datetime import datetime


def generate_months(initial_date):
    """
    :param initial_date: date in yyyy.mm.dd format
    :return: A list of strings including the 12 months starting from the initial date in yyyy-mm format
    """
    # Convert the initial date string to a datetime object
    initial_date_obj = datetime.strptime(initial_date, "%Y.%m.%d")

    # Extract the year and month from the initial date
    start_year = initial_date_obj.year
    start_month = initial_date_obj.month

    # Initialize the list to store the result
    months = []

    for i in range(12):
        # Calculate the year and month for the current iteration
        current_year = start_year + (start_month + i - 1) // 12
        current_month = (start_month + i) % 12

        # Adjust the year for January
        if current_month == 0:
            current_month = 12

        # Format the current year and month into "yyyy-mm" string
        current_date_str = f"{current_year}-{current_month:02d}"

        # Append the formatted date string to the result list
        months.append(current_date_str)

    return months
