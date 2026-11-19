import sys

filepath = r'c:\Users\madha\OneDrive\Desktop\cab_prediction_system\app.py'
content = open(filepath, encoding='utf-8').read()

replacements = [
    # Header area - remove the "Delhi NCR Cab Price Guide" line entirely
    ('<div style="font-size:0.73rem;color:{text_dim};border-left:1px solid {border_hex};padding-left:12px;">Delhi NCR Cab Price Guide</div>',
     ''),

    # Role selector
    ('Pick your portal \u2014 Customers can predict and book rides; Drivers can see incoming requests and high-demand zones.',
     'Are you a rider or a driver? Pick one below.'),
    ('Customer Portal', 'I Want a Ride'),
    ('Check prices for any time slot, compare costs, and book your ride across all Delhi NCR.',
     'See prices, compare times, and book a cab anywhere in Delhi NCR.'),
    ('Driver Partner Hub', 'I Am a Driver'),
    ('Accept live ride requests and see which Delhi NCR zones need drivers right now.',
     'Get ride requests and see where riders need cabs right now.'),

    # Customer section
    ('Pick where you want to go and when \u2014 we will show you the expected price.',
     'Tell us where you want to go and when \u2014 we will show you the price.'),
    ('Pickup \u2014 Where should the cab come?', 'Pickup Place'),
    ('Drop \u2014 Where are you going?', 'Where To?'),
    ('When do you want to travel? (See price now, book later)',
     'What time do you want to go?'),
    ('Morning Rush', 'Morning'),
    ('1.30x Busy', 'Slightly Busy'),
    ('1.05x Normal', 'Normal'),
    ('1.45x Very Busy', 'Very Busy'),
    ('1.25x Night Rate', 'Night Rates'),
    ('Choose Vehicle Type:', 'Pick Your Cab:'),
    ('Auto rickshaw, fastest in traffic', 'Auto, quick in traffic'),
    ('Affordable AC sedan', 'AC car, good price'),
    ('Top-rated drivers, comfortable', 'Comfy car, best drivers'),
    ('Spacious SUV for families', 'Big car for groups'),
    ('RIDE BOOKED!', 'YOUR RIDE IS BOOKED!'),
    ('ARRIVING SHORTLY', 'DRIVER IS COMING'),
    ('RIDE START PIN', 'YOUR PIN'),

    # Forecast section
    ('Price Forecast \u2014 See prices for all times of day', 'Compare Prices for Each Time'),
    ('Check what the price will be at <strong>any time of day</strong> \u2014 even before you travel. Pick the cheapest time!',
     'See how much the ride costs at different times. Travel when it is cheapest!'),
    ('8 AM \u2013 11 AM &bull; 1.30x surge', '8 AM \u2013 11 AM \u2022 Slightly busy'),
    ('11 AM \u2013 5 PM &bull; 1.05x normal', '11 AM \u2013 5 PM \u2022 Normal'),
    ('5 PM \u2013 9 PM &bull; 1.45x high surge', '5 PM \u2013 9 PM \u2022 Very busy'),
    ('11 PM \u2013 5 AM &bull; 1.25x night rate', '11 PM \u2013 5 AM \u2022 Night rates'),
    ('Calculating best time to travel...', 'Finding the cheapest time for you...'),
    ('How reliable is this ride?', 'Will my driver come?'),
    ('Very reliable \u2014 Driver unlikely to cancel', 'Yes! Drivers almost never cancel this ride'),
    ('Notify Nearby Drivers', 'Call More Drivers'),

    # Surge banner messages in JS
    ("prices are high right now, consider off-peak hours.", "prices are high now. Try a different time to save money."),
    ("moderate price increase.", "prices are a bit higher than normal."),
    ("normal pricing, great time to travel!", "prices are normal. Good time to book!"),

    # Driver section
    ("Today's Earnings", "Money Earned Today"),
    ("Trips Done", "Rides Done"),
    ("Online &amp; Ready", "I Am Ready"),
    ("Online & Ready", "I Am Ready"),
    ("Offline (Paused)", "Taking a Break"),
    ("NEW RIDE FOR YOU", "NEW RIDE!"),
    ("Payment via Cash / UPI &bull; 4.8 Rider Rating", "Pays by Cash or UPI \u2022 Good rider"),
    ("YOUR FARE", "YOU WILL EARN"),
    ("TRIP IS RUNNING", "RIDE IN PROGRESS"),
    ("TRIP FARE", "YOU EARN"),
    ("RIDER START PIN", "RIDER PIN"),
    ("Complete &amp; Collect", "Finish Ride & Get Paid"),
    ("Cancel Ride", "Cancel This Ride"),
    ("Pass / Next", "Skip / Next"),
    ("Auto-skip in:", "Skipping in:"),

    # Driver hour plan
    ('When Should I Drive Today?', 'Best Times to Drive Today'),
    ('Based on ride data from across Delhi NCR \u2014 here is when and where you will get the most rides today.',
     'Here is when and where you will get the most rides today.'),

    # Demand radar
    ('Live NCR Demand Radar (Right Now)', 'Where Are Riders Right Now?'),
    ('Real-time rider demand across Delhi NCR. Move to <strong style="color:#EF4444;">High Demand</strong> zones for maximum earnings.',
     'Go to <strong style="color:#EF4444;">busy areas</strong> to earn more money.'),
    ('Refresh Radar', 'Refresh'),
    ('Loading demand data from Delhi NCR roads...', 'Finding busy areas...'),
    ('Loading live Delhi NCR demand...', 'Finding busy areas...'),

    # Toast messages in JS
    ("You are now Online! Listening for new ride requests.", "You are online! You will get ride requests now."),
    ("You are Offline. No rides will be sent.", "You are taking a break. No rides for now."),
    ("Alerting 3 nearby cabs to your pickup point!", "Calling more drivers near you!"),
    ("Ride Accepted! Go pick up ", "Ride accepted! Go pick up "),
    ("Passed. Finding next rider...", "Skipped. Getting next ride..."),
    ("Trip done! Rs. ", "Ride done! Rs. "),
    (" added to your wallet.", " earned!"),
    ("Trip cancelled. Returning to ride radar.", "Ride cancelled. Getting next request."),
    ("Driver ", "Your driver "),
    (" is on the way!", " is coming!"),

    # Cancellation risk messages in JS
    ("High Reliability \u2014 Only ", "Very reliable \u2014 Only "),
    ("% chance of cancellation", "% chance of cancellation"),
    ("Moderate \u2014 ", "May cancel \u2014 "),
    ("% cancellation chance. We will find backup driver.", "% chance of cancelling. We will find another driver."),

    # API offline error
    ("API OFFLINE \u2014 START api_server.py ON PORT 8000", "Not connected. Please restart the app."),
    ("Cannot reach API. Make sure api_server.py is running on port 8000.",
     "Could not load data. Please restart the app."),

    # Demand card labels
    ("Waiting riders:", "Riders waiting:"),
    ("Avg income:", "You can earn:"),
]

count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f'OK: {old[:65]}')
    else:
        print(f'SKIP: {old[:65]}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone! Changed {count} items.')
