from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Airline, Flight, Booking

admin_bp = Blueprint("admin", __name__, template_folder="../templates")

@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "airlines": Airline.query.count(),
        "flights": Flight.query.count(),
        "bookings": Booking.query.count(),
        "active": Booking.query.filter_by(status="active").count(),
    }
    nearest = Flight.query.order_by(Flight.departure_time).limit(5).all()
    return render_template("dashboard.html", stats=stats, nearest=nearest)

# ---------- Авиакомпании ----------
@admin_bp.route("/airlines", methods=["GET", "POST"])
@login_required
def airlines():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip().upper()
        if name and code:
            db.session.add(Airline(name=name, code=code))
            db.session.commit()
            flash("Авиакомпания добавлена", "success")
        else:
            flash("Заполните все поля", "danger")
        return redirect(url_for("admin.airlines"))
    items = Airline.query.all()
    return render_template("airlines.html", items=items)

@admin_bp.route("/airlines/<int:id>/delete")
@login_required
def delete_airline(id):
    a = Airline.query.get_or_404(id)
    if a.flights:
        flash("Нельзя удалить: у авиакомпании есть рейсы", "danger")
    else:
        db.session.delete(a)
        db.session.commit()
        flash("Авиакомпания удалена", "info")
    return redirect(url_for("admin.airlines"))

# ---------- Рейсы ----------
@admin_bp.route("/flights", methods=["GET", "POST"])
@login_required
def flights():
    if request.method == "POST":
        try:
            f = Flight(
                flight_number=request.form["flight_number"],
                airline_id=int(request.form["airline_id"]),
                departure_city=request.form["departure_city"],
                arrival_city=request.form["arrival_city"],
                departure_time=datetime.strptime(request.form["departure_time"], "%Y-%m-%dT%H:%M"),
                base_price=float(request.form["base_price"]),
            )
            db.session.add(f)
            db.session.commit()
            flash("Рейс добавлен", "success")
        except Exception as e:
            flash(f"Ошибка: {e}", "danger")
        return redirect(url_for("admin.flights"))

    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    q = Flight.query
    if search:
        q = q.filter(
            (Flight.flight_number.ilike(f"%{search}%")) |
            (Flight.departure_city.ilike(f"%{search}%")) |
            (Flight.arrival_city.ilike(f"%{search}%"))
        )
    pagination = q.order_by(Flight.departure_time).paginate(page=page, per_page=5, error_out=False)
    airlines_list = Airline.query.all()
    return render_template("flights.html", pagination=pagination, airlines=airlines_list, search=search)

@admin_bp.route("/flights/<int:id>/tariff", methods=["POST"])
@login_required
def update_tariff(id):
    f = Flight.query.get_or_404(id)
    try:
        f.base_price = float(request.form["base_price"])
        db.session.commit()
        flash("Тариф обновлён", "success")
    except Exception:
        flash("Некорректный тариф", "danger")
    return redirect(url_for("admin.flights"))

@admin_bp.route("/flights/<int:id>/delete")
@login_required
def delete_flight(id):
    f = Flight.query.get_or_404(id)
    db.session.delete(f)
    db.session.commit()
    flash("Рейс удалён", "info")
    return redirect(url_for("admin.flights"))

# ---------- Бронирования ----------
@admin_bp.route("/bookings")
@login_required
def bookings():
    status = request.args.get("status", "")
    search = request.args.get("q", "").strip()
    q = Booking.query
    if status:
        q = q.filter_by(status=status)
    if search:
        q = q.filter(Booking.passenger_name.ilike(f"%{search}%"))
    items = q.order_by(Booking.created_at.desc()).all()
    return render_template("bookings.html", items=items, status=status, search=search)

@admin_bp.route("/bookings/<int:id>/cancel")
@login_required
def cancel_booking(id):
    b = Booking.query.get_or_404(id)
    b.status = "cancelled"
    db.session.commit()
    flash("Бронирование отменено", "info")
    return redirect(url_for("admin.bookings"))

# ---------- Статистика ----------
@admin_bp.route("/stats")
@login_required
def stats():
    active = Booking.query.filter_by(status="active").all()
    revenue = sum(float(b.flight.base_price) for b in active if b.flight)
    avg = revenue / len(active) if active else 0
    total = Booking.query.count()
    cancel_pct = (Booking.query.filter_by(status="cancelled").count() / total * 100) if total else 0

    loads = []
    for f in Flight.query.all():
        cnt = Booking.query.filter_by(flight_id=f.id, status="active").count()
        pct = min(100, round(cnt / f.capacity * 100)) if f.capacity else 0
        loads.append({"flight": f, "count": cnt, "pct": pct})

    return render_template("stats.html",
        revenue=revenue, avg=avg, cancel_pct=cancel_pct, loads=loads)
