from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
from dsa_structures import PropertyLinkedList, LinkedListStack, LinkedListQueue

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY", "replace-with-a-long-random-secret-for-local-testing"
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DB_CONFIG = {
    "host": os.getenv("AIRBNB_DB_HOST", "localhost"),
    "user": os.getenv("AIRBNB_DB_USER", "root"),
    "password": os.getenv("AIRBNB_DB_PASSWORD", "ADBMS@2026"),
    "database": os.getenv("AIRBNB_DB_NAME", "airbnb_clone"),
    "port": int(os.getenv("AIRBNB_DB_PORT", "3306")),
}

SAMPLE_PROPERTIES = [
    (101, "Cozy Apartment", "Bangalore", 2500, 4.5, "Apartment",
     "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=900&q=85",
     "Warm, stylish apartment close to cafes and city attractions."),
    (102, "Beach House", "Chennai", 4000, 4.7, "Beach",
     "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?auto=format&fit=crop&w=900&q=85",
     "Relaxing coastal home with breezy rooms and a bright living space."),
    (103, "Hill View Stay", "Coorg", 3000, 4.6, "Hill",
     "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=900&q=85",
     "A peaceful stay surrounded by greenery and beautiful hill views."),
    (104, "City Studio", "Bangalore", 1800, 4.2, "City",
     "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=85",
     "Compact, comfortable studio for a quick city break."),
    (105, "Lake House", "Mysore", 2800, 4.4, "Lake",
     "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=900&q=85",
     "A quiet hideaway for slow mornings and peaceful evenings."),
    (106, "Forest Nook", "Coorg", 3200, 4.8, "Hill",
     "https://images.unsplash.com/photo-1449158743715-0a90c1c2d519?auto=format&fit=crop&w=900&q=85",
     "Woodland escape with a private deck and a calm atmosphere."),
    (107, "Sea Breeze Flat", "Chennai", 3500, 4.6, "Beach",
     "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?auto=format&fit=crop&w=900&q=85",
     "Bright flat for beach days and sunset walks."),
    (108, "Garden Loft", "Bangalore", 2900, 4.5, "Apartment",
     "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=900&q=85",
     "A leafy, modern loft with thoughtful interiors.")
]


def connect():
    return mysql.connector.connect(**DB_CONFIG)


# In-memory DSA demonstrations (MySQL remains the permanent data store).
property_list = PropertyLinkedList()
recent_properties = LinkedListStack()
booking_queue = LinkedListQueue()


class User(UserMixin):
    def __init__(self, user_id, full_name, email):
        self.id = str(user_id)
        self.full_name = full_name
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT User_ID, Full_Name, Email FROM Users WHERE User_ID = %s",
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            return User(row["User_ID"], row["Full_Name"], row["Email"])
        return None
    finally:
        cursor.close()
        conn.close()


def init_db():
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Property (
                Property_ID INT PRIMARY KEY,
                Property_Name VARCHAR(100) NOT NULL,
                Location VARCHAR(100) NOT NULL,
                Price DECIMAL(10,2) NOT NULL,
                Rating DECIMAL(2,1),
                Category VARCHAR(50) DEFAULT 'Apartment',
                Image_URL VARCHAR(1000),
                Description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                User_ID INT PRIMARY KEY AUTO_INCREMENT,
                Full_Name VARCHAR(100) NOT NULL,
                Email VARCHAR(150) NOT NULL UNIQUE,
                Password_Hash VARCHAR(255) NOT NULL,
                Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Booking (
                Booking_ID INT PRIMARY KEY AUTO_INCREMENT,
                Property_ID INT NOT NULL,
                Customer_Name VARCHAR(100) NOT NULL,
                Check_In DATE NOT NULL,
                Check_Out DATE NOT NULL,
                Guests INT NOT NULL DEFAULT 1,
                FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID)
            )
        """)
        conn.commit()

        cursor.execute("SHOW COLUMNS FROM Property")
        property_columns = {row[0].lower() for row in cursor.fetchall()}

        additions = [
            ("category", "ALTER TABLE Property ADD COLUMN Category VARCHAR(50) DEFAULT 'Apartment'"),
            ("image_url", "ALTER TABLE Property ADD COLUMN Image_URL VARCHAR(1000) NULL"),
            ("description", "ALTER TABLE Property ADD COLUMN Description TEXT NULL"),
        ]
        for column, sql in additions:
            if column not in property_columns:
                cursor.execute(sql)

        cursor.execute("SHOW COLUMNS FROM Booking")
        booking_columns = {row[0].lower() for row in cursor.fetchall()}

        if "guests" not in booking_columns:
            cursor.execute(
                "ALTER TABLE Booking ADD COLUMN Guests INT NOT NULL DEFAULT 1"
            )

        if "user_id" not in booking_columns:
            cursor.execute("ALTER TABLE Booking ADD COLUMN User_ID INT NULL")

        conn.commit()

        # Add the foreign key only if it does not already exist.
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = 'Booking'
              AND COLUMN_NAME = 'User_ID'
              AND REFERENCED_TABLE_NAME = 'Users'
        """, (DB_CONFIG["database"],))

        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE Booking
                ADD CONSTRAINT fk_booking_user
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
            """)

        cursor.execute("SELECT COUNT(*) FROM Property")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany("""
                INSERT INTO Property
                (Property_ID, Property_Name, Location, Price, Rating,
                 Category, Image_URL, Description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, SAMPLE_PROPERTIES)
        else:
            for p in SAMPLE_PROPERTIES:
                cursor.execute("""
                    UPDATE Property
                    SET Category = COALESCE(NULLIF(Category, ''), %s),
                        Image_URL = COALESCE(NULLIF(Image_URL, ''), %s),
                        Description = COALESCE(NULLIF(Description, ''), %s)
                    WHERE Property_ID = %s
                """, (p[5], p[6], p[7], p[0]))

        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ---------------- DSA FUNCTIONS ----------------

def linear_search(properties, query):
    query = query.lower().strip()
    if not query:
        return properties

    return [
        p for p in properties
        if query in p["Property_Name"].lower()
        or query in p["Location"].lower()
    ]


def bubble_sort(properties):
    result = properties[:]
    n = len(result)

    for i in range(n - 1):
        swapped = False
        for j in range(n - i - 1):
            if float(result[j]["Price"]) > float(result[j + 1]["Price"]):
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break

    return result


def greedy_selection(properties, budget):
    eligible = [p for p in properties if float(p["Price"]) <= budget]
    return min(eligible, key=lambda p: float(p["Price"])) if eligible else None


class BSTNode:
    def __init__(self, prop):
        self.prop = prop
        self.left = None
        self.right = None


def bst_preorder(properties):
    root = None

    def insert(node, prop):
        if node is None:
            return BSTNode(prop)
        if float(prop["Price"]) < float(node.prop["Price"]):
            node.left = insert(node.left, prop)
        else:
            node.right = insert(node.right, prop)
        return node

    for prop in properties:
        root = insert(root, prop)

    output = []

    def preorder(node):
        if node:
            output.append({
                "name": node.prop["Property_Name"],
                "price": float(node.prop["Price"])
            })
            preorder(node.left)
            preorder(node.right)

    preorder(root)
    return output


LOCATION_GRAPH = {
    "Bangalore": ["Chennai", "Coorg", "Mysore"],
    "Chennai": ["Bangalore", "Hyderabad"],
    "Coorg": ["Bangalore"],
    "Mysore": ["Bangalore"],
    "Hyderabad": ["Chennai"]
}


def bfs(start):
    if start not in LOCATION_GRAPH:
        return []

    visited = {start}
    queue = [start]
    order = []

    while queue:
        current = queue.pop(0)
        order.append(current)

        for neighbour in LOCATION_GRAPH[current]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return order


def fetch_properties():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT Property_ID, Property_Name, Location, Price, Rating,
                   Category, Image_URL, Description
            FROM Property
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ---------------- PAGE ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/property/<int:property_id>")
def property_details(property_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM Property WHERE Property_ID = %s",
            (property_id,)
        )
        prop = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not prop:
        return "Property not found", 404

    # Keep the most recently viewed property at the top of the linked-list stack.
    top = recent_properties.peek()
    if top is None or int(top["Property_ID"]) != property_id:
        recent_properties.push(prop)

    return render_template("property_details.html", property=prop)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template(
                "signup.html", error="Please complete every field."
            )

        if len(password) < 8:
            return render_template(
                "signup.html",
                error="Password must contain at least 8 characters."
            )

        password_hash = generate_password_hash(password)
        conn = connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO Users (Full_Name, Email, Password_Hash)
                VALUES (%s, %s, %s)
            """, (name, email, password_hash))
            conn.commit()

            return render_template(
                "login.html",
                message="Account created successfully. Please log in."
            )
        except mysql.connector.IntegrityError:
            return render_template(
                "signup.html", error="This email is already registered."
            )
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = connect()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT User_ID, Full_Name, Email, Password_Hash
                FROM Users WHERE Email = %s
            """, (email,))
            user_data = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user_data and check_password_hash(
            user_data["Password_Hash"], password
        ):
            user = User(
                user_data["User_ID"],
                user_data["Full_Name"],
                user_data["Email"]
            )
            login_user(user)
            return redirect(url_for("home"))

        return render_template(
            "login.html", error="Invalid email or password."
        )

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ---------------- PROPERTY API ----------------

@app.route("/api/properties")
def properties_api():
    props = fetch_properties()
    query = request.args.get("q", "")
    category = request.args.get("category", "All")
    sort = request.args.get("sort", "recommended")

    if category != "All":
        props = [
            p for p in props
            if (p.get("Category") or "Apartment") == category
        ]

    props = linear_search(props, query)

    if sort == "price":
        props = bubble_sort(props)

    return jsonify(props)


# ---------------- BOOKING API ----------------

@app.route("/api/bookings", methods=["POST"])
@login_required
def create_booking():
    data = request.get_json(silent=True) or {}
    required = ["property_id", "check_in", "check_out"]

    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({
            "ok": False,
            "message": "Please complete all booking fields."
        }), 400

    try:
        property_id = int(data["property_id"])
        guests = int(data.get("guests", 1))

        if guests < 1 or guests > 20:
            return jsonify({
                "ok": False,
                "message": "Guest count must be between 1 and 20."
            }), 400

        check_in = datetime.strptime(data["check_in"], "%Y-%m-%d").date()
        check_out = datetime.strptime(data["check_out"], "%Y-%m-%d").date()

        if check_out <= check_in:
            return jsonify({
                "ok": False,
                "message": "Check-out must be after check-in."
            }), 400

        if check_in < datetime.today().date():
            return jsonify({
                "ok": False,
                "message": "Check-in cannot be in the past."
            }), 400

        conn = connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT Property_Name FROM Property WHERE Property_ID = %s",
                (property_id,)
            )
            row = cursor.fetchone()

            if not row:
                return jsonify({
                    "ok": False, "message": "Property not found."
                }), 404

            cursor.execute("""
                INSERT INTO Booking
                (Property_ID, Customer_Name, Check_In, Check_Out, Guests, User_ID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                property_id,
                current_user.full_name,
                check_in,
                check_out,
                guests,
                int(current_user.id)
            ))

            booking_id = cursor.lastrowid
            conn.commit()

            # Demonstrate FIFO booking requests. The permanent booking is in MySQL.
            booking_queue.enqueue({
                "booking_id": booking_id,
                "property_id": property_id,
                "property_name": row[0],
                "customer_name": current_user.full_name,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "guests": guests
            })

            return jsonify({
                "ok": True,
                "message": f"Booking request saved for {row[0]}.",
                "booking_id": booking_id
            })
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        return jsonify({
            "ok": False,
            "message": "Please enter valid dates and guest count."
        }), 400
    except Error:
        app.logger.exception("Booking insert failed")
        return jsonify({
            "ok": False,
            "message": "Database error while saving booking."
        }), 500


# ---------------- DSA DEMONSTRATION API ----------------

@app.route("/api/dsa")
def dsa_api():
    props = fetch_properties()
    property_list.load(props)
    budget = request.args.get("budget", type=float, default=3000)
    start = request.args.get("location", default="Bangalore")
    cheapest = greedy_selection(props, budget)
    sorted_props = bubble_sort(props)

    return jsonify({
        "search_algorithm": "Linear Search",
        "sorting_algorithm": "Bubble Sort",
        "linked_list": {
            "size": property_list.size,
            "properties": [{
                "id": p["Property_ID"],
                "name": p["Property_Name"],
                "location": p["Location"],
                "price": float(p["Price"])
            } for p in property_list.traverse()]
        },
        "recent_stack": [{
            "id": p["Property_ID"], "name": p["Property_Name"],
            "location": p["Location"], "price": float(p["Price"])
        } for p in recent_properties.traverse()],
        "booking_queue": booking_queue.traverse(),
        "sorted_properties": [{
            "id": p["Property_ID"], "name": p["Property_Name"],
            "location": p["Location"], "price": float(p["Price"])
        } for p in sorted_props],
        "bst_preorder": bst_preorder(props),
        "bfs": bfs(start),
        "greedy": ({
            "name": cheapest["Property_Name"],
            "location": cheapest["Location"],
            "price": float(cheapest["Price"])
        } if cheapest else None)
    })


@app.route("/api/dsa/properties", methods=["GET", "POST", "DELETE"])
def dsa_properties_api():
    """Demonstrate linked-list traversal/insert/delete without deleting DB rows."""
    props = fetch_properties()
    demo_list = PropertyLinkedList()
    demo_list.load(props)

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            property_id = int(data.get("property_id"))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "Send a valid property_id."}), 400
        found = next((p for p in props if int(p["Property_ID"]) == property_id), None)
        if not found:
            return jsonify({"ok": False, "message": "Property not found."}), 404
        demo_list.insert(found)
        return jsonify({"ok": True, "message": "Property inserted into the demo linked list.",
                        "size": demo_list.size, "properties": [p["Property_ID"] for p in demo_list.traverse()]})

    if request.method == "DELETE":
        property_id = request.args.get("property_id", type=int)
        if property_id is None:
            return jsonify({"ok": False, "message": "Provide property_id."}), 400
        deleted = demo_list.delete(property_id)
        return jsonify({"ok": deleted, "message": "Node deleted from demo list." if deleted else "Property not found in demo list.",
                        "size": demo_list.size, "properties": [p["Property_ID"] for p in demo_list.traverse()]})

    return jsonify({"size": demo_list.size, "properties": [
        {"id": p["Property_ID"], "name": p["Property_Name"], "price": float(p["Price"])}
        for p in demo_list.traverse()
    ]})


@app.route("/api/dsa/recent", methods=["GET", "DELETE"])
def dsa_recent_api():
    if request.method == "DELETE":
        popped = recent_properties.pop()
        return jsonify({"ok": popped is not None, "popped": popped})
    return jsonify({"size": recent_properties.size, "top_first": [{
        "id": p["Property_ID"], "name": p["Property_Name"], "location": p["Location"]
    } for p in recent_properties.traverse()]})


@app.route("/api/dsa/booking-queue", methods=["GET", "DELETE"])
def dsa_booking_queue_api():
    if request.method == "DELETE":
        item = booking_queue.dequeue()
        return jsonify({"ok": item is not None, "dequeued": item})
    return jsonify({"size": booking_queue.size, "front_first": booking_queue.traverse()})


if __name__ == "__main__":
    try:
        conn = connect()
        conn.close()
        init_db()
        print("Connected to MySQL database:", DB_CONFIG["database"])
        app.run(debug=True)
    except Error as exc:
        print("\nCould not connect to MySQL.")
        print("Check that MySQL Server is running and DB_CONFIG credentials are correct.")
        print("Details:", exc)