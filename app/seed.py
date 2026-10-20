from app.extensions import db
from app.models import User, Airline, Flight, Booking
from datetime import datetime, timedelta

def seed_admin():
    from flask import current_app
    if User.query.filter_by(username=current_app.config["ADMIN_USERNAME"]).first():
        return
    u = User(username=current_app.config["ADMIN_USERNAME"], role="admin")
    u.set_password(current_app.config["ADMIN_PASSWORD"])
    db.session.add(u)
    db.session.commit()

def seed_demo():
    if Airline.query.count():
        return
    airlines = [
        Airline(name="Аэрофлот", code="SU"),
        Airline(name="S7 Airlines", code="S7"),
        Airline(name="Победа", code="DP"),
        Airline(name="Уральские авиалинии", code="U6"),
    ]
    db.session.add_all(airlines)
    db.session.commit()

    now = datetime.utcnow()
    flights = [
        Flight(flight_number="SU-123", airline_id=airlines[0].id, departure_city="Москва",
               arrival_city="Санкт-Петербург", departure_time=now+timedelta(days=1, hours=3), base_price=7500),
        Flight(flight_number="S7-450", airline_id=airlines[1].id, departure_city="Москва",
               arrival_city="Новосибирск", departure_time=now+timedelta(days=1, hours=6), base_price=12400),
        Flight(flight_number="DP-301", airline_id=airlines[2].id, departure_city="Москва",
               arrival_city="Сочи", departure_time=now+timedelta(days=2, hours=1), base_price=5100),
        Flight(flight_number="U6-780", airline_id=airlines[3].id, departure_city="Екатеринбург",
               arrival_city="Москва", departure_time=now+timedelta(days=2, hours=9), base_price=6300),
    ]
    db.session.add_all(flights)
    db.session.commit()

    bookings = [
        Booking(passenger_name="Иванов И. И.", flight_id=flights[0].id, seat_number="12A"),
        Booking(passenger_name="Петрова А. С.", flight_id=flights[1].id, seat_number="4B"),
        Booking(passenger_name="Сидоров К. П.", flight_id=flights[0].id, seat_number="18C", status="cancelled"),
        Booking(passenger_name="Кузнецов Д. В.", flight_id=flights[2].id, seat_number="7A"),
    ]
    db.session.add_all(bookings)
    db.session.commit()
