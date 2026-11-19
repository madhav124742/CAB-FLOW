import glob

files = glob.glob(r'c:\Users\madha\OneDrive\Desktop\cab_prediction_system\*.py') + \
        glob.glob(r'c:\Users\madha\OneDrive\Desktop\cab_prediction_system\*.md') + \
        glob.glob(r'c:\Users\madha\OneDrive\Desktop\cab_prediction_system\*.bat')

replacements = [
    ('data_analysis_and_exploration', 'data_analysis_and_exploration'),
    ('data_cleaning_and_price_prediction', 'data_cleaning_and_price_prediction'),
    ('ride_cancellation_prediction', 'ride_cancellation_prediction'),
    ('ride_grouping_and_patterns', 'ride_grouping_and_patterns'),
    ('data analysis & exploration', 'data analysis & exploration'),
    ('Data Analysis & Exploration', 'Data Analysis & Exploration'),
    ('DATA ANALYSIS & EXPLORATION', 'DATA ANALYSIS & EXPLORATION'),
    ('data cleaning & price prediction', 'data cleaning & price prediction'),
    ('Data Cleaning & Price Prediction', 'Data Cleaning & Price Prediction'),
    ('DATA CLEANING & PRICE PREDICTION', 'DATA CLEANING & PRICE PREDICTION'),
    ('ride cancellation prediction', 'ride cancellation prediction'),
    ('Ride Cancellation Prediction', 'Ride Cancellation Prediction'),
    ('RIDE CANCELLATION PREDICTION', 'RIDE CANCELLATION PREDICTION'),
    ('ride grouping & patterns', 'ride grouping & patterns'),
    ('Ride Grouping & Patterns', 'Ride Grouping & Patterns'),
    ('RIDE GROUPING & PATTERNS', 'RIDE GROUPING & PATTERNS'),
    ('PART 1:', 'PART 1:'),
    ('PART 2:', 'PART 2:'),
    ('PART 3:', 'PART 3:'),
    ('PART 4:', 'PART 4:')
]

for fpath in files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        orig = content
        for old, new in replacements:
            content = content.replace(old, new)
        if content != orig:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print('Updated:', fpath)
    except Exception as e:
        print('Error with', fpath, e)
