import firebase_admin
from firebase_admin import credentials, db
import time
from datetime import datetime, timezone

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'DATABASE-ID.firebasedatabase.app/'
})

# Configuration
BOOKING_TIMEOUT_SECONDS = 20  # 20 seconds
SLEEP_INTERVAL_SECONDS = 10  # Check every 5 seconds

def clear_expired_bookings():
    try:
        # Reference to the seats node
        seats_ref = db.reference('seats/slot-1')
        
        # Get all seats
        seats = seats_ref.get()
        
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        
        for seat_number, seat_data in seats.items():
            # Check only booked seats
            if seat_data.get('isBooked', False):
                booking_time = datetime.fromisoformat(seat_data['timestamp'].replace('Z', '+00:00'))
                time_since_booking = (current_time - booking_time).total_seconds()
                
                # Clear booking if it exceeds timeout
                if time_since_booking > BOOKING_TIMEOUT_SECONDS:
                    seats_ref.child(seat_number).update({
                        'isBooked': False,
                        'bookedBy': None,
                        'timestamp': None
                    })
                    print(f"Cleared booking for seat {seat_number}")
    
    except Exception as e:
        print(f"Error in clearing bookings: {e}")

def main():
    print("Starting seat booking cleanup service...")
    while True:
        print("Checking for expired bookings...")
        clear_expired_bookings()
        time.sleep(SLEEP_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
