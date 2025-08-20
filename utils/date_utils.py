from datetime import datetime
from dateutil.relativedelta import relativedelta

# Date formatting configuration
DATE_FORMAT = "{year}-{month}-{day}"
YEAR_MONTH_FORMAT = "{year}-{month}"


def format_date_for_filename(year, month, day):
	return DATE_FORMAT.format(year=year, month=month, day=day)


def format_year_month_for_filename(year, month):
	return YEAR_MONTH_FORMAT.format(year=year, month=month)


def subtract_one_month(year, month, day):
	dt = datetime(int(year), int(month), int(day))
	prev_month = dt - relativedelta(months=1)
	return prev_month.strftime('%Y'), prev_month.strftime('%m'), prev_month.strftime('%d') 