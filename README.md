# Airbnb-style DSA Mini Project — Python + MySQL

## Technologies
- Frontend: HTML, CSS, JavaScript
- Backend: Python + Flask
- Database: **MySQL** (`airbnb_clone`)
- DSA: Linear Search, Bubble Sort, BST with **Preorder traversal only**, Graph + BFS, Greedy budget selection.

## Before running
1. Make sure **MySQL Server is running**.
2. Open MySQL Workbench or your MySQL terminal.
3. Use the existing database `airbnb_clone`. The project does not drop or recreate it.
4. The backend checks for the extra display columns needed by the website (`Category`, `Image_URL`, `Description`) and adds only those missing columns. It also adds `Guests` to `Booking` if needed. Existing property and booking data is preserved.
5. Make sure the database login in `app.py` is correct. Defaults are:
   - host: `localhost`
   - user: `root`
   - password: empty string
   - database: `airbnb_clone`
   - port: `3306`

## Run in VS Code (Windows PowerShell)
Open the project folder in VS Code. In Terminal → New Terminal, run each command:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser. Keep the terminal open while using the website. Press Ctrl+C to stop.

## What it does
- Displays properties from MySQL.
- Searches property names and locations using Linear Search in Python.
- Filters by category.
- Provides Bubble Sort by price through `/api/properties?sort=price`.
- Shows BST price organization using Preorder traversal only.
- Shows location traversal using BFS.
- Chooses the cheapest property within a budget using a Greedy algorithm.
- Saves booking requests to MySQL.

## Important
- This is a learning/demo booking request; it does not process payments or verify live availability.
- Internet is required for the external property images and Google Fonts.


## DSA structures included in this updated version

- **Linked List:** traverses the property records; the demo insert/delete endpoints operate on a temporary in-memory list and do not delete or duplicate rows in MySQL.
- **Stack using a linked list:** property detail pages push recently viewed properties onto the stack (LIFO).
- **Queue using a linked list:** successful booking requests are added to the in-memory FIFO queue after they are saved to MySQL.
- **Binary Search Tree:** properties organized by price and shown using preorder traversal.
- **Graph and BFS:** explores the configured connections between locations.
- **Linear Search, Bubble Sort, and Greedy selection:** existing search/sort/budget demonstration retained.

### DSA API endpoints

- `GET /api/dsa` — combined DSA demonstration data
- `GET /api/dsa/properties` — linked-list traversal
- `POST /api/dsa/properties` with JSON `{"property_id": 101}` — demo insert into a temporary list
- `DELETE /api/dsa/properties?property_id=101` — demo delete from a temporary list
- `GET /api/dsa/recent` and `DELETE /api/dsa/recent` — inspect/pop the recent-property stack
- `GET /api/dsa/booking-queue` and `DELETE /api/dsa/booking-queue` — inspect/dequeue the booking queue

**Important:** The linked-list stack and queue are in memory for DSA demonstration and reset whenever Flask restarts. MySQL remains the permanent store for property, account, and booking data.
