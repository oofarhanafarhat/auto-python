# vehicle_rental.py
# Author: YOU
# Date  : 2025-07-20
# A simple yet complete OOP + Streamlit Vehicle Rental System

import datetime as dt
from abc import ABC, abstractmethod
import uuid
import streamlit as st

# -----------------------------------------------------------
# 1. DATA STORE (in-memory for demo)
# -----------------------------------------------------------
class DataStore:
    """Singleton in-memory DB."""
    vehicles: list["Vehicle"] = []
    users: list["User"] = []
    bookings: list["Booking"] = []

    @classmethod
    def reset(cls):
        cls.vehicles.clear()
        cls.users.clear()
        cls.bookings.clear()

# -----------------------------------------------------------
# 2. ABSTRACT USER
# -----------------------------------------------------------
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
        """Each subclass renders its own dashboard."""
        pass

# -----------------------------------------------------------
# 3. CONCRETE USERS
# -----------------------------------------------------------
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
        st.write(f"Welcome {self.name}")
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
                st.success(f"Booked! Total: ${booking.total_price:.2f}")

        st.subheader("My bookings")
        my_bookings = [b for b in DataStore.bookings if b.customer == self]
        for b in my_bookings:
            st.write(f"{b.vehicle.brand} {b.vehicle.model} | "
                     f"{b.start} → {b.end} | ${b.total_price}")

# -----------------------------------------------------------
# 4. BOOKING ENTITY
# -----------------------------------------------------------
class Booking:
    def __init__(self, vehicle: "Vehicle", customer: Customer,
                 start: dt.date, end: dt.date):
        self.vehicle = vehicle
        self.customer = customer
        self.start = start
        self.end = end
        self.total_price = vehicle.calculate_rental_price(start, end)

# -----------------------------------------------------------
# 5. ABSTRACT VEHICLE
# -----------------------------------------------------------
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

    def is_available(self):
        return self._is_available

    def rent_vehicle(self, customer: Customer, start: dt.date, end: dt.date):
        if not self._is_available:
            st.error("Vehicle already booked.")
            return None
        self._is_available = False
        return Booking(self, customer, start, end)

    def return_vehicle(self):
        self._is_available = True

    @abstractmethod
    def calculate_rental_price(self, start: dt.date, end: dt.date) -> float:
        pass

    def __repr__(self):
        return f"{self.type}({self.brand} {self.model})"

# -----------------------------------------------------------
# 6. CONCRETE VEHICLES
# -----------------------------------------------------------
class Car(Vehicle):
    def calculate_rental_price(self, start, end):
        days = (end - start).days
        return self._daily_rate * days * 1.0  # no surcharge

class Bike(Vehicle):
    def calculate_rental_price(self, start, end):
        days = (end - start).days
        return self._daily_rate * days * 0.8  # 20 % discount

class Truck(Vehicle):
    def calculate_rental_price(self, start, end):
        days = (end - start).days
        return self._daily_rate * days * 1.5  # 50 % surcharge

# -----------------------------------------------------------
# 7. STREAMLIT APP LAYOUT
# -----------------------------------------------------------
def login_page():
    st.title("🚗 Vehicle Rental System")
    role = st.selectbox("Login as", ["Admin", "Customer"])
    name = st.text_input("Name")
    email = st.text_input("Email")
    if st.button("Login / Register"):
        user = None
        for u in DataStore.users:
            if u.email == email:
                user = u
                break
        if not user:
            user = Admin(name, email) if role == "Admin" else Customer(name, email)
            DataStore.users.append(user)
        st.session_state["user"] = user
        st.rerun()

def main():
    if "user" not in st.session_state:
        login_page()
    else:
        user = st.session_state["user"]
        user.dashboard()
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()

if __name__ == "__main__":
    # Seed demo data
    if not DataStore.vehicles:
        DataStore.vehicles.extend([
            Car("Toyota", "Camry", 2023, 55),
            Bike("Yamaha", "R15", 2022, 25),
            Truck("Ford", "F150", 2021, 100)
        ])
    main()
