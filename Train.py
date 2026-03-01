import uuid
from datetime import datetime

# ==========================================
# 1. Custom Exceptions
# ==========================================
class BookingError(Exception):
    """Base class for booking errors."""
    pass

class SeatUnavailableError(BookingError):
    """Raised when a seat is already booked or invalid."""
    pass

class InvalidBookingIDError(BookingError):
    """Raised when a cancellation is attempted with a wrong ID."""
    pass

class InvalidInputError(Exception):
    """Raised for general user input errors."""
    pass

# ==========================================
# 2. Models (OOP: Encapsulation & Abstraction)
# ==========================================

class Train:
    def __init__(self, train_id, name, source, destination, total_seats):
        self.train_id = train_id
        self.name = name
        self.source = source
        self.destination = destination
        self.total_seats = total_seats
        # Dictionary to track seat status: {seat_no: is_booked_bool}
        self._seats = {i: False for i in range(1, total_seats + 1)}

    @property
    def available_seats(self):
        return [seat for seat, booked in self._seats.items() if not booked]

    def book_seat(self, seat_no):
        if seat_no not in self._seats:
            raise SeatUnavailableError(f"Seat {seat_no} does not exist on this train.")
        if self._seats[seat_no]:
            raise SeatUnavailableError(f"Seat {seat_no} is already booked.")
        
        self._seats[seat_no] = True
        return True

    def release_seat(self, seat_no):
        if seat_no in self._seats:
            self._seats[seat_no] = False

    def __str__(self):
        return f"[{self.train_id}] {self.name} ({self.source} -> {self.destination}) | Available: {len(self.available_seats)}/{self.total_seats}"


class Passenger:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

    def __str__(self):
        return f"{self.name} (Age: {self.age})"


class Booking:
    def __init__(self, train, passenger, seat_no):
        self.booking_id = str(uuid.uuid4()).split('-')[0].upper() # Short ID
        self.train = train
        self.passenger = passenger
        self.seat_no = seat_no
        self.booking_time = datetime.now()
        self.status = "CONFIRMED"

    def cancel(self):
        self.status = "CANCELLED"
        self.train.release_seat(self.seat_no)

    def __str__(self):
        return (f"Booking ID: {self.booking_id} | Train: {self.train.name} | "
                f"Seat: {self.seat_no} | Passenger: {self.passenger.name} | "
                f"Status: {self.status}")

# ==========================================
# 3. Service Layer (Business Logic)
# ==========================================

class ReservationSystem:
    def __init__(self):
        self.trains = {}
        self.bookings = {}

    def add_train(self, train):
        self.trains[train.train_id] = train

    def display_trains(self):
        print("\n--- Available Trains ---")
        for train in self.trains.values():
            print(train)
        print("------------------------")

    def book_ticket(self, train_id, passenger, seat_no):
        if train_id not in self.trains:
            raise InvalidInputError("Invalid Train ID.")
        
        train = self.trains[train_id]
        
        # Exception-safe logic: Try to book, catch errors if seat taken
        train.book_seat(seat_no)
        
        # If successful, create booking
        new_booking = Booking(train, passenger, seat_no)
        self.bookings[new_booking.booking_id] = new_booking
        return new_booking

    def cancel_ticket(self, booking_id):
        if booking_id not in self.bookings:
            raise InvalidBookingIDError("Booking ID not found.")
        
        booking = self.bookings[booking_id]
        if booking.status == "CANCELLED":
            raise InvalidInputError("Ticket is already cancelled.")
        
        booking.cancel()
        return booking

    def view_bookings(self):
        if not self.bookings:
            print("No bookings found.")
        else:
            print("\n--- All Bookings ---")
            for b in self.bookings.values():
                print(b)

# ==========================================
# 4. CLI Interface
# ==========================================

def main():
    system = ReservationSystem()
    
    # Pre-populating Data
    system.add_train(Train("T101", "Rajdhani Express", "Delhi", "Mumbai", 5))
    system.add_train(Train("T102", "Shatabdi Express", "Chennai", "Bangalore", 3))

    while True:
        print("\n=== TRAIN RESERVATION SYSTEM ===")
        print("1. View Trains")
        print("2. Book a Ticket")
        print("3. Cancel a Ticket")
        print("4. View My Bookings")
        print("5. Exit")
        
        choice = input("Enter choice: ")

        try:
            if choice == '1':
                system.display_trains()

            elif choice == '2':
                system.display_trains()
                t_id = input("Enter Train ID (e.g., T101): ").strip()
                
                name = input("Enter Passenger Name: ").strip()
                if not name: raise InvalidInputError("Name cannot be empty.")
                
                age = int(input("Enter Age: "))
                
                # Show available seats logic
                if t_id in system.trains:
                    train = system.trains[t_id]
                    print(f"Available Seats: {train.available_seats}")
                    seat = int(input("Enter Seat Number: "))
                    
                    p = Passenger(name, age, "email@example.com")
                    booking = system.book_ticket(t_id, p, seat)
                    print(f"\nSUCCESS! Ticket Booked.")
                    print(booking)
                else:
                    print("Error: Train ID not found.")

            elif choice == '3':
                b_id = input("Enter Booking ID to cancel: ").strip().upper()
                cancelled = system.cancel_ticket(b_id)
                print(f"SUCCESS: Booking {cancelled.booking_id} has been cancelled.")

            elif choice == '4':
                system.view_bookings()

            elif choice == '5':
                print("Exiting System. Goodbye!")
                break
            
            else:
                print("Invalid choice. Try again.")

        except ValueError:
            print("INPUT ERROR: Please enter valid numbers for Age/Seat.")
        except (BookingError, InvalidInputError) as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    main()