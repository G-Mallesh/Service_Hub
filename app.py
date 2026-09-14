from datetime import datetime, date
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "servicehub-new-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///servicehub.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


# =========================================================
# USER MODEL
# =========================================================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# WORKER MODEL
# =========================================================

class Worker(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    location = db.Column(
        db.String(255),
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    availability = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "worker_profile",
            uselist=False
        )
    )


# =========================================================
# SERVICE MODEL
# =========================================================

class Service(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )


# =========================================================
# WORKER SERVICE MODEL
# =========================================================

class WorkerService(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("worker.id"),
        nullable=True
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=False
    )

    worker = db.relationship(
        "Worker",
        backref="worker_services"
    )

    service = db.relationship(
        "Service",
        backref="worker_services"
    )


# =========================================================
# BOOKING MODEL
# =========================================================

class Booking(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=False
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("worker.id"),
        nullable=True
    )

    booking_date = db.Column(
        db.Date,
        nullable=False
    )

    booking_time = db.Column(
        db.Time,
        nullable=False
    )

    customer_phone = db.Column(
        db.String(20),
        nullable=True
    )

    customer_location = db.Column(
        db.String(255),
        nullable=True
    )

    customer_latitude = db.Column(
        db.Float,
        nullable=True
    )

    customer_longitude = db.Column(
        db.Float,
        nullable=True
    )

    worker_latitude = db.Column(
        db.Float,
        nullable=True
    )

    worker_longitude = db.Column(
        db.Float,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="bookings"
    )

    service = db.relationship(
        "Service",
        backref="bookings"
    )

    worker = db.relationship(
        "Worker",
        backref="bookings"
    )


# =========================================================
# MESSAGE MODEL
# =========================================================

class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("booking.id"),
        nullable=True
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id]
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id]
    )

    booking = db.relationship(
        "Booking",
        backref="messages"
    )


# =========================================================
# REVIEW MODEL
# =========================================================

class Review(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=False
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("booking.id"),
        nullable=False,
        unique=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="reviews"
    )

    service = db.relationship(
        "Service",
        backref="reviews"
    )

    booking = db.relationship(
        "Booking",
        backref=db.backref(
            "review",
            uselist=False
        )
    )


# =========================================================
# LOGIN USER
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =========================================================
# ADMIN DECORATOR
# =========================================================

def admin_required(function):

    @wraps(function)
    @login_required
    def decorated_function(
        *args,
        **kwargs
    ):

        if current_user.role != "admin":

            flash(
                "Access denied. Admin access required."
            )

            return redirect(
                url_for("index")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    services = Service.query.limit(6).all()

    return render_template(
        "index.html",
        services=services
    )


# =========================================================
# REGISTER
# =========================================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()

        account_type = request.form.get(
            "account_type",
            "customer"
        )


        # Validate common fields

        if not name or not email or not password:

            flash("Please fill all required fields.")

            return redirect(
                url_for("register")
            )


        # Check duplicate email

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already registered.")

            return redirect(
                url_for("register")
            )


        # Worker validation

        if account_type == "worker":

            if not phone or not location:

                flash(
                    "Workers must provide phone number and location."
                )

                return redirect(
                    url_for("register")
                )


        # Create User

        if account_type == "worker":

            role = "worker"

        else:

            role = "user"


        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            phone=phone
        )

        db.session.add(user)

        db.session.flush()


        # Create Worker profile

        if account_type == "worker":

            worker = Worker(
                user_id=user.id,
                phone=phone,
                location=location,
                availability=True
            )

            db.session.add(worker)


        db.session.commit()


        flash(
            "Registration successful. Please login."
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )

# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            if user.role == "admin":

                return redirect(
                    url_for("admin_dashboard")
                )

            if user.role == "worker":

                return redirect(
                    url_for("worker_dashboard")
                )

            return redirect(
                url_for("index")
            )

        flash(
            "Invalid email or password."
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("index")
    )

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    users = User.query.all()

    workers = Worker.query.all()

    services = Service.query.all()

    bookings = Booking.query.all()

    reviews = Review.query.all()

    return render_template(
        "admin_dashboard.html",
        users=users,
        workers=workers,
        services=services,
        bookings=bookings,
        reviews=reviews
    )
# =========================================================
# WORKER DASHBOARD
# =========================================================

@app.route("/worker")
@login_required
def worker_dashboard():

    if current_user.role != "worker":

        flash(
            "Access denied. Worker access required."
        )

        return redirect(
            url_for("index")
        )

    worker = Worker.query.filter_by(
        user_id=current_user.id
    ).first()

    if not worker:

        flash(
            "Worker profile not found."
        )

        return redirect(
            url_for("index")
        )

    services = Service.query.join(
        WorkerService,
        Service.id == WorkerService.service_id
    ).filter(
        WorkerService.worker_id == worker.id
    ).all()

    bookings = Booking.query.filter_by(
        worker_id=worker.id
    ).order_by(
        Booking.created_at.desc()
    ).all()

    return render_template(
        "worker_dashboard.html",
        worker=worker,
        services=services,
        bookings=bookings
    )
# =========================================================
# WORKER ACCEPT BOOKING
# =========================================================

@app.route("/worker/booking/<int:booking_id>/accept", methods=["POST"])
@login_required
def worker_accept_booking(booking_id):

    if current_user.role != "worker":

        flash("Access denied. Worker access required.")

        return redirect(
            url_for("index")
        )

    worker = Worker.query.filter_by(
        user_id=current_user.id
    ).first()

    if not worker:

        flash("Worker profile not found.")

        return redirect(
            url_for("index")
        )

    booking = Booking.query.get_or_404(
        booking_id
    )

    # Make sure this booking belongs to this worker

    if booking.worker_id != worker.id:

        flash("You cannot manage this booking.")

        return redirect(
            url_for("worker_dashboard")
        )

    # Only Pending bookings can be accepted

    if booking.status != "Pending":

        flash("This booking cannot be accepted.")

        return redirect(
            url_for("worker_dashboard")
        )

    booking.status = "Accepted"

    # Save worker location to the booking

    booking.worker_latitude = worker.latitude
    booking.worker_longitude = worker.longitude

    db.session.commit()

    flash(
        "Booking accepted successfully."
    )

    return redirect(
        url_for("worker_dashboard")
    )


# =========================================================
# WORKER REJECT BOOKING
# =========================================================

@app.route("/worker/booking/<int:booking_id>/reject", methods=["POST"])
@login_required
def worker_reject_booking(booking_id):

    if current_user.role != "worker":

        flash("Access denied. Worker access required.")

        return redirect(
            url_for("index")
        )

    worker = Worker.query.filter_by(
        user_id=current_user.id
    ).first()

    if not worker:

        flash("Worker profile not found.")

        return redirect(
            url_for("index")
        )

    booking = Booking.query.get_or_404(
        booking_id
    )

    if booking.worker_id != worker.id:

        flash("You cannot manage this booking.")

        return redirect(
            url_for("worker_dashboard")
        )

    if booking.status != "Pending":

        flash("This booking cannot be rejected.")

        return redirect(
            url_for("worker_dashboard")
        )

    booking.status = "Rejected"

    db.session.commit()

    flash(
        "Booking rejected."
    )

    return redirect(
        url_for("worker_dashboard")
    )


# =========================================================
# WORKER UPDATE BOOKING STATUS
# =========================================================

@app.route(
    "/worker/booking/<int:booking_id>/status",
    methods=["POST"]
)
@login_required
def worker_update_booking_status(booking_id):

    if current_user.role != "worker":

        flash("Access denied. Worker access required.")

        return redirect(
            url_for("index")
        )

    worker = Worker.query.filter_by(
        user_id=current_user.id
    ).first()

    if not worker:

        flash("Worker profile not found.")

        return redirect(
            url_for("index")
        )

    booking = Booking.query.get_or_404(
        booking_id
    )

    if booking.worker_id != worker.id:

        flash("You cannot manage this booking.")

        return redirect(
            url_for("worker_dashboard")
        )

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    allowed_statuses = [
        "On the Way",
        "Arrived",
        "In Progress",
        "Completed"
    ]


    if new_status not in allowed_statuses:

        flash(
            "Invalid booking status."
        )

        return redirect(
            url_for("worker_dashboard")
        )


    # Status order protection

    status_order = {
        "Accepted": 1,
        "On the Way": 2,
        "Arrived": 3,
        "In Progress": 4,
        "Completed": 5
    }


    current_status = booking.status


    if current_status not in status_order:

        flash(
            "This booking cannot be updated."
        )

        return redirect(
            url_for("worker_dashboard")
        )


    if status_order[new_status] != status_order[current_status] + 1:

        flash(
            "Please update the booking step by step."
        )

        return redirect(
            url_for("worker_dashboard")
        )


    booking.status = new_status

    db.session.commit()


    flash(
        f"Booking status updated to {new_status}."
    )


    return redirect(
        url_for("worker_dashboard")
    )
# =========================================================
# CUSTOMER BOOK SERVICE
# =========================================================

@app.route("/book/<int:service_id>", methods=["GET", "POST"])
@login_required
def book_service(service_id):

    if current_user.role != "user":

        flash("Only customers can book services.")

        return redirect(
            url_for("index")
        )

    service = Service.query.get_or_404(
        service_id
    )

    workers = (
        Worker.query
        .join(
            WorkerService,
            Worker.id == WorkerService.worker_id
        )
        .filter(
            WorkerService.service_id == service.id,
            Worker.availability == True
        )
        .all()
    )

    if request.method == "POST":

        worker_id_text = request.form.get(
            "worker_id",
            ""
        ).strip()

        booking_date_text = request.form.get(
            "booking_date",
            ""
        ).strip()

        booking_time_text = request.form.get(
            "booking_time",
            ""
        ).strip()

        customer_phone = request.form.get(
            "customer_phone",
            ""
        ).strip()

        customer_location = request.form.get(
            "customer_location",
            ""
        ).strip()

        customer_latitude_text = request.form.get(
            "customer_latitude",
            ""
        ).strip()

        customer_longitude_text = request.form.get(
            "customer_longitude",
            ""
        ).strip()


        # -------------------------------------------------
        # WORKER
        # -------------------------------------------------

        if not worker_id_text:

            flash("Please select a worker.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )

        try:

            worker_id = int(
                worker_id_text
            )

        except ValueError:

            flash("Invalid worker selected.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        worker = Worker.query.get(
            worker_id
        )

        if not worker:

            flash("Selected worker was not found.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        # -------------------------------------------------
        # CHECK WORKER PROVIDES SERVICE
        # -------------------------------------------------

        worker_service = WorkerService.query.filter_by(
            worker_id=worker.id,
            service_id=service.id
        ).first()

        if not worker_service:

            flash(
                "This worker does not provide the selected service."
            )

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        if not worker.availability:

            flash(
                "Selected worker is currently unavailable."
            )

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        if not booking_date_text:

            flash("Please select a booking date.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )

        try:

            booking_date = datetime.strptime(
                booking_date_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash("Invalid booking date.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        if booking_date < date.today():

            flash(
                "Booking date cannot be in the past."
            )

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        if not booking_time_text:

            flash("Please select a booking time.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )

        try:

            booking_time = datetime.strptime(
                booking_time_text,
                "%H:%M"
            ).time()

        except ValueError:

            flash("Invalid booking time.")

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        if not customer_phone:

            flash(
                "Please enter your phone number."
            )

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        if not customer_location:

            flash(
                "Please enter your location."
            )

            return redirect(
                url_for(
                    "book_service",
                    service_id=service.id
                )
            )


        # -------------------------------------------------
        # CUSTOMER LATITUDE
        # -------------------------------------------------

        if customer_latitude_text:

            try:

                customer_latitude = float(
                    customer_latitude_text
                )

            except ValueError:

                flash(
                    "Invalid customer latitude."
                )

                return redirect(
                    url_for(
                        "book_service",
                        service_id=service.id
                    )
                )

            if not -90 <= customer_latitude <= 90:

                flash(
                    "Latitude must be between -90 and 90."
                )

                return redirect(
                    url_for(
                        "book_service",
                        service_id=service.id
                    )
                )

        else:

            customer_latitude = None


        # -------------------------------------------------
        # CUSTOMER LONGITUDE
        # -------------------------------------------------

        if customer_longitude_text:

            try:

                customer_longitude = float(
                    customer_longitude_text
                )

            except ValueError:

                flash(
                    "Invalid customer longitude."
                )

                return redirect(
                    url_for(
                        "book_service",
                        service_id=service.id
                    )
                )

            if not -180 <= customer_longitude <= 180:

                flash(
                    "Longitude must be between -180 and 180."
                )

                return redirect(
                    url_for(
                        "book_service",
                        service_id=service.id
                    )
                )

        else:

            customer_longitude = None


        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------

        booking = Booking(

            user_id=current_user.id,

            service_id=service.id,

            worker_id=worker.id,

            booking_date=booking_date,

            booking_time=booking_time,

            customer_phone=customer_phone,

            customer_location=customer_location,

            customer_latitude=customer_latitude,

            customer_longitude=customer_longitude,

            worker_latitude=worker.latitude,

            worker_longitude=worker.longitude,

            status="Pending"
        )


        db.session.add(
            booking
        )

        db.session.commit()


        flash(
            "Service booking request sent successfully."
        )

        return redirect(
            url_for("my_bookings")
        )


    # -----------------------------------------------------
    # SHOW BOOKING PAGE
    # -----------------------------------------------------

    return render_template(
        "booking.html",
        service=service,
        workers=workers,
        today=date.today().isoformat()
    )


# =========================================================
# CUSTOMER ADD REVIEW / RATING
# =========================================================

@app.route(
    "/add-review/<int:booking_id>",
    methods=["GET", "POST"]
)
@login_required
def add_review(booking_id):

    if current_user.role != "user":

        flash(
            "Only customers can add reviews."
        )

        return redirect(
            url_for("index")
        )


    booking = Booking.query.get_or_404(
        booking_id
    )


    if booking.user_id != current_user.id:

        flash(
            "You are not allowed to review this booking."
        )

        return redirect(
            url_for("my_bookings")
        )


    if booking.status != "Completed":

        flash(
            "You can review the service only after it is completed."
        )

        return redirect(
            url_for("my_bookings")
        )


    existing_review = Review.query.filter_by(
        booking_id=booking.id
    ).first()


    if existing_review:

        flash(
            "You have already reviewed this service."
        )

        return redirect(
            url_for("my_bookings")
        )


    if request.method == "POST":

        rating_text = request.form.get(
            "rating",
            ""
        ).strip()

        comment = request.form.get(
            "comment",
            ""
        ).strip()


        try:

            rating = int(
                rating_text
            )

        except (ValueError, TypeError):

            flash(
                "Please select a valid rating."
            )

            return redirect(
                url_for(
                    "add_review",
                    booking_id=booking.id
                )
            )


        if rating < 1 or rating > 5:

            flash(
                "Rating must be between 1 and 5 stars."
            )

            return redirect(
                url_for(
                    "add_review",
                    booking_id=booking.id
                )
            )


        review = Review(

            rating=rating,

            comment=comment,

            user_id=current_user.id,

            service_id=booking.service_id,

            booking_id=booking.id
        )


        db.session.add(
            review
        )

        db.session.commit()


        flash(
            "Rating and review submitted successfully."
        )

        return redirect(
            url_for("my_bookings")
        )


    return render_template(
        "add_review.html",
        booking=booking
    )


# =========================================================
# SERVICE DETAILS
# =========================================================

@app.route("/service/<int:service_id>")
def service_details(service_id):

    service = Service.query.get_or_404(
        service_id
    )

    return render_template(
        "service_details.html",
        service=service
    )
# =========================================================
# SERVICES PAGE
# =========================================================
@app.route("/services")
def services():

    search = request.args.get(
        "search",
        ""
    ).strip()

    category = request.args.get(
        "category",
        ""
    ).strip()

    query = Service.query

    if search:

        query = query.filter(
            Service.name.ilike(
                f"%{search}%"
            )
        )

    if category:

        query = query.filter_by(
            category=category
        )

    services = query.all()

    categories = [
        row[0]
        for row in db.session.query(
            Service.category
        ).distinct().all()
    ]

    return render_template(
        "services.html",
        services=services,
        categories=categories,
        search=search,
        selected_category=category
    )
    
@app.route("/book/<int:booking_id>", methods=["GET", "POST"])

    
    

# =========================================================
# CUSTOMER MY BOOKINGS
# =========================================================

@app.route("/my-bookings")
@login_required
def my_bookings():

    if current_user.role != "user":

        flash(
            "Only customers can view customer bookings."
        )

        return redirect(
            url_for("index")
        )

    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Booking.created_at.desc()
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )
# =========================================================
# DATABASE CREATION
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )