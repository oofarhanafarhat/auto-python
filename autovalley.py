# vehicle_rental.py
# Author: YOU
# Date  : 2025-07-21

import datetime as dt
from abc import ABC, abstractmethod
import uuid
import streamlit as st

# -----------------------------
# 👮 Admin Credentials (Demo Only)
# -----------------------------
ADMIN_EMAIL = "farhanafarhat012@gmail.com"
ADMIN_PASSWORD = "01234"

# -----------------------------
# 1. Data Store
# -----------------------------
class DataStore:
    vehicles: list["Vehicle"] = []
    users: list["User"] = []
    bookings: list["Booking"] = []

    @classmethod
    def reset(cls):
        cls.vehicles.clear()
        cls.users.clear()
        cls.bookings.clear()

# -----------------------------
# 2. Abstract User
# -----------------------------
class User(ABC):
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email
        self._id = str(uuid.uuid4())

    @property
    def id(self): return self._id
    @property
    def name(self): return self._name
    @property
    def email(self): return self._email

    @abstractmethod
    def dashboard(self):
        pass

# -----------------------------
# 3. Users
# -----------------------------
class Admin(User):
    def dashboard(self):
        st.header("👨‍💼 Admin Dashboard")

        st.subheader("Add new vehicle")
        v_type = st.selectbox("Type", ["Car", "Bike", "Truck"])
        brand = st.text_input("Brand")
        model = st.text_input("Model")
        year = st.number_input("Year", min_value=2000, max_value=2025)
        daily = st.number_input("Daily Rate (USD)", min_value=1.0, value=50.0)

        if st.button("Add"):
            if v_type == "Car":
                v = Car(brand, model, year, daily)
            elif v_type == "Bike":
                v = Bike(brand, model, year, daily)
            else:
                v = Truck(brand, model, year, daily)
            DataStore.vehicles.append(v)
            st.success("Vehicle added!")

        st.subheader("All Vehicles")
        for v in DataStore.vehicles:
            st.write(f"{v.type} | {v.brand} {v.model} ({v.year}) | "
                     f"${v.daily_rate} | {'✅' if v.is_available() else '❌'}")

class Customer(User):
    def dashboard(self):
        st.header("🧑‍💼 Customer Dashboard")
        st.write(f"Welcome {self.name}!")

        available = [v for v in DataStore.vehicles if v.is_available()]
        if not available:
            st.info("No vehicles available.")
            return

        selected = st.selectbox("Choose a vehicle", available,
                                format_func=lambda v: f"{v.brand} {v.model} ({v.type})")
        start = st.date_input("Start date", dt.date.today())
        end = st.date_input("End date", dt.date.today() + dt.timedelta(days=1))
        if start >= end:
            st.warning("End date must be after start date.")
            return

        if st.button("Rent"):
            booking = selected.rent_vehicle(self, start, end)
            if booking:
                DataStore.bookings.append(booking)
                st.success(f"Booked! ✅ Booking ID: `{booking.booking_id}` — Total: ${booking.total_price:.2f}")

        st.subheader("📜 My Bookings")
        my_bookings = [b for b in DataStore.bookings if b.customer == self]
        for b in my_bookings:
            st.markdown(
                f"- **Booking ID**: `{b.booking_id}` | {b.vehicle.brand} {b.vehicle.model} "
                f"({b.start} → {b.end}) | 💲{b.total_price:.2f} | "
                f"{'✅ Returned' if b.returned else '🚗 Active'}"
            )

        st.subheader("↩️ Return a Vehicle")
        return_id = st.text_input("Enter Booking ID to Return")
        if st.button("Return Vehicle"):
            booking = next((b for b in my_bookings if b.booking_id == return_id), None)
            if booking:
                if booking.returned:
                    st.warning("This booking has already been returned.")
                else:
                    booking.vehicle.return_vehicle()
                    booking.returned = True
                    st.success("✅ Vehicle returned successfully.")
            else:
                st.error("❌ Invalid Booking ID.")

# -----------------------------
# 4. Booking
# -----------------------------
class Booking:
    def __init__(self, vehicle: "Vehicle", customer: Customer, start: dt.date, end: dt.date):
        self.booking_id = str(uuid.uuid4())[:8]
        self.vehicle = vehicle
        self.customer = customer
        self.start = start
        self.end = end
        self.returned = False
        self.total_price = vehicle.calculate_rental_price(start, end)

# -----------------------------
# 5. Vehicles (Abstract)
# -----------------------------
class Vehicle(ABC):
    def __init__(self, brand: str, model: str, year: int, daily_rate: float):
        self._brand = brand
        self._model = model
        self._year = year
        self._daily_rate = daily_rate
        self._is_available = True

    brand = property(lambda self: self._brand)
    model = property(lambda self: self._model)
    year = property(lambda self: self._year)
    daily_rate = property(lambda self: self._daily_rate)
    type = property(lambda self: self.__class__.__name__)

    def is_available(self): return self._is_available

    def rent_vehicle(self, customer: Customer, start: dt.date, end: dt.date):
        if not self._is_available:
            st.error("Vehicle already booked.")
            return None
        self._is_available = False
        return Booking(self, customer, start, end)

    def return_vehicle(self): self._is_available = True

    @abstractmethod
    def calculate_rental_price(self, start: dt.date, end: dt.date) -> float: pass

    def __repr__(self): return f"{self.type}({self.brand} {self.model})"

# -----------------------------
# 6. Concrete Vehicles
# -----------------------------
class Car(Vehicle):
    def calculate_rental_price(self, start, end):
        return self._daily_rate * (end - start).days

class Bike(Vehicle):
    def calculate_rental_price(self, start, end):
        return self._daily_rate * (end - start).days * 0.8

class Truck(Vehicle):
    def calculate_rental_price(self, start, end):
        return self._daily_rate * (end - start).days * 1.5

# -----------------------------
# 7. Seed Demo Data
# -----------------------------
def seed_demo_data():
    if not DataStore.vehicles:
        DataStore.vehicles.extend([
            Car("Toyota", "Corolla", 2022, 45),
            Car("Honda", "Civic", 2021, 50),
            Car("Hyundai", "Elantra", 2023, 48),
            Car("Suzuki", "Swift", 2020, 40),
            Car("Tesla", "Model 3", 2024, 100),
            Bike("Honda", "CBR500", 2021, 25),
            Bike("Yamaha", "R15", 2022, 22),
            Bike("Suzuki", "Gixxer", 2020, 20),
            Bike("Kawasaki", "Ninja", 2023, 30),
            Truck("Volvo", "FH", 2020, 150),
            Truck("Scania", "R-Series", 2019, 140),
            Truck("MAN", "TGX", 2022, 160),
        ])
    if not DataStore.users:
        user1 = Customer("Ali", "ali@gmail.com")
        user2 = Customer("Sara", "sara@gmail.com")
        DataStore.users.extend([user1, user2])
    if not DataStore.bookings:
        b1 = DataStore.vehicles[0].rent_vehicle(DataStore.users[0], dt.date.today(), dt.date.today() + dt.timedelta(days=3))
        b2 = DataStore.vehicles[5].rent_vehicle(DataStore.users[1], dt.date.today(), dt.date.today() + dt.timedelta(days=2))
        if b1: DataStore.bookings.append(b1)
        if b2: DataStore.bookings.append(b2)

# -----------------------------
# 8. Login + App
# -----------------------------
def login_page():
    st.title("🚗 Vehicle Rental System")
    role = st.selectbox("Login as", ["Admin", "Customer"])
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if role == "Admin":
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                user = Admin(name, email)
                st.session_state["user"] = user
                st.success("Admin logged in.")
                st.rerun()
            else:
                st.error("Invalid Admin credentials.")
        else:
            user = next((u for u in DataStore.users if u.email == email), None)
            if not user:
                user = Customer(name, email)
                DataStore.users.append(user)
            st.session_state["user"] = user
            st.success("Customer logged in.")
            st.rerun()

def main():
    seed_demo_data()
    if "user" not in st.session_state:
        login_page()
    else:
        user = st.session_state["user"]
        user.dashboard()
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()

if __name__ == "__main__":
    main()
