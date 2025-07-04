
import mysql.connector
import hashlib
import os
from datetime import datetime, timedelta
from db_alchemy import get_sqlalchemy_engine

# === DB Configuration ===
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "atla1v",
    "password": "mypass",
    "database": "BIS698W1830_GRP12"
}

#-----------------------------------------------------------------------------------------------------------------------------

def connect_db():
    """
    Establish a connection to the MySQL database using provided credentials.
    """
    return mysql.connector.connect(**DB_CONFIG)

#-----------------------------------------------------------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash the password using SHA-256 and return the hexadecimal digest.
    """
    return hashlib.sha256(password.encode()).hexdigest()

#-----------------------------------------------------------------------------------------------------------------------------

def insert_user(first_name, last_name, email, phone, password_hash, role):
    """
    Insert a new user into the users table.

    Returns:
        Tuple: (True, "Success message") if insertion is successful,
               (False, "Error message") if insertion fails.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO users (first_name, last_name, email, phone, password, role, pwd_change_req)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
        """
        cursor.execute(query, (first_name, last_name, email, phone, password_hash, role))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Hurray! Registered successfully. Redirecting to Login Page..."
    except mysql.connector.Error as e:
        return False, f"Database Error: {e}"
    
#-----------------------------------------------------------------------------------------------------------------------------


def user_exists(email, phone):
    """
    Checks if a user with the same email or phone already exists.
    Returns: (True, "Reason") or (False, "")
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT email, phone FROM users WHERE email = %s OR phone = %s"
        cursor.execute(query, (email, phone))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            if result[0] == email:
                return True, "Email already exists."
            if result[1] == phone:
                return True, "Phone Number already exists."
        return False, ""
    except mysql.connector.Error as e:
        return True, f"Database error: {e}"

#-----------------------------------------------------------------------------------------------------------------------------


def validate_user(email, password):
    """
    Validates user credentials and returns (True, role) or (False, "error").
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        SELECT user_id, first_name, last_name, email, phone, password, role, active_status, pwd_change_req 
        FROM users WHERE email = %s
    """

        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            user_id, first_name, last_name, email, phone, stored_hash, role, active_status, pwd_change_req = result
            hashed_input = hash_password(password)
            if hashed_input == stored_hash:
                if active_status != 1:
                    return False, "Account inactive. Please contact admin."

                user_info = {
                    "user_id": user_id,
                    "email": email,
                    "phone": phone,
                    "first_name": first_name,
                    "last_name": last_name,
                    "full_name": f"{first_name} {last_name}",
                    "role": role,
                    "pwd_change_req": pwd_change_req,
                    "active_status": active_status
                }
                return True, user_info
            else:
                return False, "Incorrect password"
        return False, "User not found, Please Signup..."
    except mysql.connector.Error as e:
        return False, f"Database error: {e}"

#-----------------------------------------------------------------------------------------------------------------------------

def get_user_details(user_id):
    """
    Fetch full user details based on user_id.
    Returns: dict with keys [id, email, first_name, last_name, full_name, role]
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT user_id, email, phone, first_name, last_name, role FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            uid, email, phone, fname, lname, role = result
            return {
                "user_id": uid,
                "email": email,
                "phone": phone,
                "first_name": fname,
                "last_name": lname,
                "full_name": f"{fname} {lname}",
                "role": role
            }
        return None
    except mysql.connector.Error as e:
        print(f"DB Error: {e}")
        return None




#-----------------------------------------------------------------------------------------------------------------------------

def insert_car_with_images(car_data, image_paths, main_image_path):
    """
    Insert car listing into `cars` and uploaded images into `cars_images` in a transaction.
    Rolls back if any step fails.

    Params:
        car_data (dict): car details from form
        image_paths (list): list of file paths to uploaded images
        main_image_path (str): path of selected main image

    Returns:
        (bool, str): (True, "Success message") or (False, "Error message")
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        conn.start_transaction()

        # === Insert into `car` table
        insert_car_query = """
            INSERT INTO car (
                make, model, year, VIN, drivetrain, price, mileage, fuel_type, transmission,
                car_condition, car_color, status, description, title, economy, staff_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        car_values = (
            car_data['Make'], car_data['Model'], car_data['Year'], car_data['VIN Number'], car_data['Drivetrain'],
            car_data['Price ($)'], car_data['Mileage (mi)'], car_data['Fuel Type'], car_data['Transmission'],
            car_data['Condition'], car_data['Color'], car_data['Status'],
            car_data['description'], car_data['Title'], car_data['Economy'], car_data["staff_id"]
        )
        cursor.execute(insert_car_query, car_values)
        car_id = cursor.lastrowid
        # === Insert images into `carimages`
        image_query = "INSERT INTO carimages (car_id, image, is_main_image) VALUES (%s, %s, %s)"
        for path in image_paths:
            with open(path, 'rb') as f:
                image_blob = f.read()
            is_main = 1 if path == main_image_path else 0
            cursor.execute(image_query, (car_id, image_blob, is_main))

            # 🧠 Store the DB id of main image
            if is_main:
                main_image_db_id = cursor.lastrowid

        if main_image_db_id:
            update_query = "UPDATE car SET main_image_id = %s WHERE car_id = %s"
            cursor.execute(update_query, (main_image_db_id, car_id))

        # === COMMIT if all successful
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Car listing and images saved successfully.", car_id

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return False, f"Database error: {str(e)}", None




#-----------------------------------------------------------------------------------------------------------------------------

def insert_staff(first_name, last_name, email, phone, password_hash, role, status):
    """
    Inserts a new staff member into the 'users' table of the database.

    Parameters:
        first_name (str): The staff member's first name.
        last_name (str): The staff member's last name.
        email (str): The staff member's email address.
        phone (str): The staff member's phone number.
        password_hash (str): The hashed password (default assigned).
        role (str): The role assigned to the staff member (e.g., 'Admin', 'Staff').
        status (int): Active status of the staff (1 = Active, 0 = Inactive).

    Returns:
        tuple:
            (True, user_id) if insertion is successful,
            (False, "Database Error: ...") if any error occurs.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO users (first_name, last_name, email, phone, password, role, active_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (first_name, last_name, email, phone, password_hash, role, status))
        user_id = cursor.lastrowid  # 🆕 Get the inserted user ID
        conn.commit()
        cursor.close()
        conn.close()
        return True, user_id
    except mysql.connector.Error as e:
        return False, f"Database Error: {e}"

#-----------------------------------------------------------------------------------------------------------------------------

def get_staff(search_text=None, status_filter="All"):
    """
    Fetch staff records from the 'users' table with optional search and status filter.

    Parameters:
        search_text (str, optional): Partial match on full name, email, or exact match on user ID.
        status_filter (str): "Active", "Inactive", or "All" (default).

    Returns:
        List[Dict]: List of matching staff users with fields:
                    user_id, full_name, email, phone, role, status
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT user_id, first_name, last_name, CONCAT(first_name, ' ', last_name) AS name,
                   email, phone, role, active_status AS status, created_at, updated_at
            FROM users
            WHERE role IN ('Admin', 'Staff')
        """
        params = []

        if search_text:
            query += " AND (CONCAT(first_name, ' ', last_name) LIKE %s OR email LIKE %s OR user_id = %s)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param, search_text if search_text.isdigit() else -1])

        if status_filter != "All":
            query += " AND active_status = %s"
            params.append(1 if status_filter == "Active" else 0)

        query += " ORDER BY user_id DESC"
        cursor.execute(query, params)
        results = cursor.fetchall()

        for user in results:
            user["status"] = "Active" if user["status"] == 1 else "Inactive"

        cursor.close()
        conn.close()
        return results

    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return []


#-----------------------------------------------------------------------------------------------------------------------------

def update_staff(user_id, first_name, last_name, email, phone, role, status):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE users
            SET first_name = %s,
                last_name = %s,
                email = %s,
                phone = %s,
                role = %s,
                active_status = %s,
                updated_at = NOW()
            WHERE user_id = %s
        """
        cursor.execute(query, (first_name, last_name, email, phone, role, status, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Staff updated successfully"
    except mysql.connector.Error as e:
        print(f"[DB ERROR] {e}")
        return False, "Database update failed"



#-----------------------------------------------------------------------------------------------------------------------------

def get_customers(search_text=None, status_filter="All"):
    """
    Retrieve a list of customers from the 'users' table based on optional search and status filter.

    Parameters:
        search_text (str, optional): A keyword to search by full name, email, or user ID.
                                     Supports partial match for names and email.
        status_filter (str, optional): Status filter to apply. Can be "Active", "Inactive", or "All" (default).

    Returns:
        List[Dict]: A list of dictionaries, each representing a customer record, including:
                    - user_id
                    - name (concatenated first and last name)
                    - email
                    - phone
                    - role (always 'Customer')
                    - status (as string: "Active" or "Inactive")
                    - created_at
                    - updated_at

    Notes:
        - Customers are filtered by role='Customer'.
        - Results are sorted by user_id in descending order.
    """

    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT user_id, first_name, last_name, email, phone, role, active_status AS status, created_at, updated_at 
            FROM users
            WHERE role = 'customer'
        """
        params = []

        if search_text:
            query += " AND (CONCAT(first_name, ' ', last_name) LIKE %s OR email LIKE %s OR user_id = %s)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param, search_text if search_text.isdigit() else -1])

        if status_filter != "All":
            query += " AND active_status = %s"
            params.append(1 if status_filter == "Active" else 0)

        query += " ORDER BY user_id DESC"
        cursor.execute(query, params)
        results = cursor.fetchall()

        for user in results:
            user["status"] = "Active" if user["status"] == 1 else "Inactive"

        cursor.close()
        conn.close()
        return results

    except mysql.connector.Error as e:
        print(f"[DB ERROR] {e}")
        return []


#-----------------------------------------------------------------------------------------------------------------------------

def insert_customer(first_name, last_name, email, phone, password_hash, role, status):
    """
    Inserts a new customer into the 'users' table.

    Parameters:
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        email (str): Customer's email.
        phone (str): Customer's phone.
        password_hash (str): Default hashed password.
        role (str): Fixed as 'Customer'.
        status (int): 1 = Active, 0 = Inactive

    Returns:
        tuple: (True, user_id) on success, (False, error message) on failure.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO users (first_name, last_name, email, phone, password, role, active_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (first_name, last_name, email, phone, password_hash, role, status))
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return True, user_id
    except mysql.connector.Error as e:
        return False, f"Database Error: {e}"


#-----------------------------------------------------------------------------------------------------------------------------

def update_customer_db(user_id, first_name, last_name, email, phone, status):
    """
    Updates customer information in the 'users' table.

    Parameters:
        user_id (int): ID of the customer to update.
        first_name (str): Updated first name.
        last_name (str): Updated last name.
        email (str): Updated email.
        phone (str): Updated phone number.
        status (int): 1 for Active, 0 for Inactive.

    Returns:
        Tuple: (True, message) on success, (False, error) on failure.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE users
            SET first_name = %s,
                last_name = %s,
                email = %s,
                phone = %s,
                active_status = %s,
                updated_at = NOW()
            WHERE user_id = %s AND role = 'customer'
        """
        cursor.execute(query, (first_name, last_name, email, phone, status, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Customer updated successfully"
    except mysql.connector.Error as e:
        print(f"[DB ERROR] {e}")
        return False, "Customer update failed"



#-----------------------------------------------------------------------------------------------------------------------------

def get_all_car_listings(search_text=None, filters=None, status="All"):
    """
    Fetch car listings with optional search, filters, and status.
    Used in manage_car_listing.py for admin view.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                c.car_id, c.make, c.model, c.year, c.price, c.vin, c.fuel_type, c.transmission,
                c.car_color, c.car_condition, c.economy, c.mileage, c.status, ci.image AS main_image
            FROM car c
            JOIN carimages ci ON c.main_image_id = ci.image_id
            WHERE 1=1
        """
        params = []

        # === 1. Status Filter
        if status != "All":
            query += " AND c.status = %s"
            params.append(status)

        # === 2. Search Text Filter
        if search_text:
            query += " AND LOWER(CONCAT_WS(' ', c.make, c.model, c.year, c.vin)) LIKE %s"
            params.append(f"%{search_text.lower()}%")

        # === 3. Checkbox Filters (multi-selects)
        if filters:
            for field in ['make', 'model', 'fuel_type', 'transmission', 'car_color', 'car_condition', 'title']:
                if field in filters:
                    values = filters[field]
                    if values:
                        placeholders = ','.join(['%s'] * len(values))
                        query += f" AND c.{field} IN ({placeholders})"
                        params.extend(values)

            # === 4. Range Filters (sliders)
            range_map = {
                'price': 'c.price',
                'year': 'c.year',
                'mileage': 'c.mileage',
                'economy': 'c.economy'
            }
            for key, column in range_map.items():
                if key in filters and isinstance(filters[key], tuple):
                    min_val, max_val = filters[key]
                    query += f" AND {column} BETWEEN %s AND %s"
                    params.extend([min_val, max_val])

        if status == "All":
            query += """
                ORDER BY 
                    CASE 
                        WHEN c.status = 'Available' THEN 1
                        WHEN c.status = 'Sold' THEN 2
                        WHEN c.status = 'Archived' THEN 3
                        ELSE 4
                    END,
                    c.car_id DESC
            """
        else:
            query += " ORDER BY c.car_id DESC"


        cursor.execute(query, params)
        cars = cursor.fetchall()

        os.makedirs("temp_images", exist_ok=True)
        for car in cars:
            car['name'] = f"{car['make']} {car['model']} {car['year']}"
            if car['main_image']:
                image_path = f"temp_images/{car['car_id']}.jpg"
                with open(image_path, 'wb') as f:
                    f.write(car['main_image'])
                car['img'] = image_path
            else:
                car['img'] = "icons/default_car.png"

        cursor.close()
        conn.close()
        return cars

    except Exception as e:
        print(f"[DB ERROR] get_all_car_listings: {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def search_cars(search_text=None, filters=None):
    """
    Search and filter available cars from the database.

    Args:
        search_text (str): Keyword to search across car fields.
        filters (dict): Filter dictionary like:
            {
                'make': [...],
                'model': [...],
                'fuel_type': [...],
                'transmission': [...],
                'car_color': [...],
                'car_condition': [...],
                'title': [...],
                'price_range': (min, max),
                'year_range': (min, max),
                'mileage_range': (min, max),
                'economy_range': (min, max)
            }

    Returns:
        List[Dict]: Filtered car listings.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        base_query = """
            SELECT 
                c.car_id, c.make, c.model, c.year, c.price, c.mileage, c.fuel_type, c.transmission, 
                c.car_color, c.car_condition, c.title, c.economy, ci.image AS main_image
            FROM car c
            JOIN carimages ci ON c.main_image_id = ci.image_id
            WHERE c.status = 'Available'
        """

        conditions = []
        params = []

        # === Search Text Logic ===
        if search_text:
            conditions.append("""
                (LOWER(CONCAT_WS(' ', c.make, c.model, c.year, c.fuel_type, c.transmission, c.car_color, 
                                 c.car_condition, c.title)) LIKE %s)
            """)
            params.append(f"%{search_text.lower()}%")

        # === Multi-value filters
        multi_fields = ['make', 'model', 'fuel_type', 'transmission', 'car_color', 'car_condition', 'title']
        if filters:
            for field in multi_fields:
                if field in filters and filters[field]:
                    placeholders = ','.join(['%s'] * len(filters[field]))
                    conditions.append(f"c.{field} IN ({placeholders})")
                    params.extend(filters[field])

            # === Range filters
            range_map = {
                'price_range': 'c.price',
                'year_range': 'c.year',
                'mileage_range': 'c.mileage',
                'economy_range': 'c.economy'
            }
            for key, column in range_map.items():
                if key in filters and isinstance(filters[key], tuple) and len(filters[key]) == 2:
                    min_val, max_val = filters[key]
                    conditions.append(f"{column} BETWEEN %s AND %s")
                    params.extend([min_val, max_val])

        # === Add conditions to base query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)


        # === Sorting Logic (Multiple Fields)
        if filters and "sort_by" in filters:
            sort_clauses = []
            for field, direction in filters["sort_by"]:
                if field in ["price", "mileage", "year", "economy"] and direction in ["asc", "desc"]:
                    sort_clauses.append(f"c.{field} {direction.upper()}")
            if sort_clauses:
                base_query += f" ORDER BY {', '.join(sort_clauses)}"
            else:
                base_query += " ORDER BY c.car_id DESC"
        else:
            base_query += " ORDER BY c.car_id DESC"


        cursor.execute(base_query, params)
        cars = cursor.fetchall()
        cursor.close()
        conn.close()

        # === Load Images from BLOBs
        os.makedirs("temp_images", exist_ok=True)
        for car in cars:
            car['name'] = f"{car['make'].title()} {car['model'].title()} {car['year']}"
            if car['main_image']:
                safe_title = car['name'].replace(" ", "_").replace("/", "_")
                image_path = f"temp_images/{safe_title}.jpg"
                with open(image_path, 'wb') as f:
                    f.write(car['main_image'])
                car['img'] = image_path
            else:
                car['img'] = "icons/default_car.png"

        return cars

    except Exception as e:
        print(f"[DB ERROR] {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def get_available_makes():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT make FROM car WHERE status = 'Available'")
        results = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except mysql.connector.Error as e:
        print("[DB ERROR]", e)
        return []



#-----------------------------------------------------------------------------------------------------------------------------


def get_available_models(selected_makes=None):
    """
    Returns a list of unique 'Make + Model' combinations,
    filtered optionally by selected makes.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if selected_makes:
            placeholders = ','.join(['%s'] * len(selected_makes))
            query = f"""
                SELECT DISTINCT CONCAT(make, ' ', model) AS make_model
                FROM car
                WHERE status = 'Available' AND make IN ({placeholders})
                ORDER BY make_model ASC
            """
            cursor.execute(query, selected_makes)
        else:
            query = """
                SELECT DISTINCT CONCAT(make, ' ', model) AS make_model
                FROM car
                WHERE status = 'Available'
                ORDER BY make_model ASC
            """
            cursor.execute(query)

        results = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results

    except mysql.connector.Error as e:
        print(f"[DB ERROR] get_available_models(): {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def get_available_options(column_name):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = f"SELECT DISTINCT {column_name} FROM car WHERE status = 'Available'"
        cursor.execute(query)
        results = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except mysql.connector.Error as e:
        print(f"[DB ERROR] column={column_name}", e)
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def get_range_bounds(column):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = f"SELECT MIN({column}), MAX({column}) FROM car WHERE status = 'Available'"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result  # (min_val, max_val)
    except:
        return (None, None)



#-----------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------

def get_car_by_id(car_id):
    """
    Fetch detailed information about a specific car by its ID, including all associated images.

    Parameters:
        car_id (int): The ID of the car to retrieve.

    Returns:
        dict or None: A dictionary with the full car details and image paths:
            {
                "car_id": ...,
                "make": ..., "model": ..., "year": ..., "vin": ...,
                "drivetrain": ..., "price": ..., "mileage": ..., "fuel_type": ...,
                "transmission": ..., "color": ..., "condition": ..., "status": ...,
                "description": ..., "title_status": ..., "economy": ...,
                "main_image": "path/to/img", "images": [ "path1", "path2", ... ]
            }
            or None if the car is not found.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        # === 1. Fetch Car Details with main_image_id ===
        cursor.execute("""
            SELECT car_id, make, model, year, vin, drivetrain, price, mileage, fuel_type,
                   transmission, car_color AS color, car_condition AS car_condition,
                   status, description, title AS title_status, economy, main_image_id
            FROM car
            WHERE car_id = %s
        """, (car_id,))
        car = cursor.fetchone()

        if not car:
            return None

        # === 2. Get Main Image Path (from carimages using main_image_id) ===
        main_img = None
        if car.get("main_image_id"):
            cursor.execute("SELECT image FROM carimages WHERE image_id = %s", (car["main_image_id"],))
            row = cursor.fetchone()
            if row and row["image"]:
                # Save main image to temp
                os.makedirs("temp_images", exist_ok=True)
                main_path = f"temp_images/main_car_{car_id}.jpg"
                with open(main_path, 'wb') as f:
                    f.write(row["image"])
                main_img = main_path

        car["main_image"] = main_img

        # === 3. Fetch All Images ===
        cursor.execute("SELECT image, image_id FROM carimages WHERE car_id = %s ORDER BY image_id", (car_id,))
        images = []
        for row in cursor.fetchall():
            image_blob = row["image"]
            image_id = row["image_id"]
            img_path = f"temp_images/car_{car_id}_img_{image_id}.jpg"

            with open(img_path, 'wb') as f:
                f.write(image_blob)

            if image_id == car["main_image_id"]:
                car["main_image"] = img_path  # Ensure this is used as main
            else:
                images.append(img_path)

        car["images"] = [car["main_image"]] + images if car.get("main_image") else images


        cursor.close()
        conn.close()
        return car

    except Exception as e:
        print(f"[DB ERROR] get_car_by_id(): {e}")
        return None



#-----------------------------------------------------------------------------------------------------------------------------

def get_make_model_pairs(selected_makes=None):
    """
    Fetch (make, model) pairs for the filter popup.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if selected_makes:
            placeholders = ','.join(['%s'] * len(selected_makes))
            query = f"""
                SELECT DISTINCT make, model
                FROM car
                WHERE status = 'Available' AND make IN ({placeholders})
                ORDER BY make ASC, model ASC
            """
            cursor.execute(query, selected_makes)
        else:
            query = """
                SELECT DISTINCT make, model
                FROM car
                WHERE status = 'Available'
                ORDER BY make ASC, model ASC
            """
            cursor.execute(query)

        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    except mysql.connector.Error as e:
        print(f"[DB ERROR] get_make_model_pairs(): {e}")
        return []


#-----------------------------------------------------------------------------------------------------------------------------

def update_user_password(email, new_hashed_password):
    """
    Update the user's password and reset pwd_change_req to 0.

    Args:
        email (str): The user's email.
        new_hashed_password (str): The new hashed password.

    Returns:
        (bool, str): Success status and message.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE users
            SET password = %s, pwd_change_req = 0
            WHERE email = %s
        """
        cursor.execute(query, (new_hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Password updated successfully."
    except mysql.connector.Error as e:
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------

def book_test_drive(customer_id, car_id, preferred_date, preferred_time, location):
    """
    Insert a new test drive booking into the testdrivebooking table.

    Args:
        customer_id (int): ID of the customer booking the test drive.
        car_id (int): ID of the car to test drive.
        preferred_date (str): Date in 'YYYY-MM-DD' format.
        preferred_time (str): Time string (e.g., '9:00 AM').
        location (str): Dealership location.

    Returns:
        Tuple: (True, "Booking successful.") or (False, "Error message")
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Convert string time (e.g. '9:00 AM') to TIME format for MySQL
        from datetime import datetime
        time_obj = datetime.strptime(preferred_time, "%I:%M %p").time()

        query = """
            INSERT INTO testdrivebooking (customer_id, car_id, preferred_date, preferred_time, status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """
        cursor.execute(query, (customer_id, car_id, preferred_date, time_obj))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Test drive booked successfully."
    except mysql.connector.Error as e:
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

def update_car_with_images(car_id, car_data):
    """
    Update a car listing and its images in the database.
    
    Params:
        car_id (int): ID of the car to update.
        car_data (dict): Updated car data including fields, description, images, and main image.

    Returns:
        (bool, str): Success status and message.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        conn.start_transaction()

        # === Update main car table ===
        update_query = """
            UPDATE car
            SET make=%s, model=%s, year=%s, VIN=%s, drivetrain=%s, price=%s, mileage=%s,
                fuel_type=%s, transmission=%s, car_condition=%s, car_color=%s, status=%s,
                description=%s, title=%s, economy=%s
            WHERE car_id=%s
        """

        values = (
            car_data["Make"], car_data["Model"], car_data["Year"], car_data["VIN Number"],
            car_data["Drivetrain"], car_data["Price ($)"], car_data["Mileage (mi)"], car_data["Fuel Type"],
            car_data["Transmission"], car_data["Condition"], car_data["Color"], car_data["Status"],
            car_data["description"], car_data["Title"], car_data["Economy"], car_id
        )

        cursor.execute(update_query, values)

        # === Delete old images ===
        cursor.execute("DELETE FROM carimages WHERE car_id = %s", (car_id,))

        # === Re-insert updated images ===
        main_image_id = None
        for path in car_data["Images"]:
            with open(path, 'rb') as f:
                image_blob = f.read()
            is_main = 1 if path == car_data["MainImage"] else 0
            cursor.execute("INSERT INTO carimages (car_id, image, is_main_image) VALUES (%s, %s, %s)",
                           (car_id, image_blob, is_main))
            if is_main:
                main_image_id = cursor.lastrowid

        # === Update car.main_image_id ===
        if main_image_id:
            cursor.execute("UPDATE car SET main_image_id = %s WHERE car_id = %s", (main_image_id, car_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Car updated successfully."

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return False, f"Database error: {str(e)}"



#-----------------------------------------------------------------------------------------------------------------------------

def generate_invoice_number():
    """
    Generates a unique invoice number in the format PCDSYYYYMMDDXXXX
    """
    from datetime import datetime
    today_str = datetime.now().strftime("%Y%m%d")
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) FROM salesinvoice 
            WHERE DATE(sale_date) = CURDATE()
        """
        cursor.execute(query)
        count = cursor.fetchone()[0] + 2  # Next invoice number for today

        cursor.close()
        conn.close()

        # Format: PCDS + Date + 4-digit number
        return f"PCDS{today_str}{str(count).zfill(4)}"
    except Exception as e:
        print("[ERROR] generate_invoice_number:", e)
        return None



#-----------------------------------------------------------------------------------------------------------------------------


def insert_customer_and_sale(customer_id, user_data, sale_data):
    """
    Handles the full transaction:
    - Insert walk-in customer if customer_id is None
    - Insert sale record
    - Update car status to Sold
    All inside ONE transaction.

    Returns: (True, sale_id) or (False, error message)
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        conn.start_transaction()

        # Step 1: If Walk-in
        if customer_id is None:
            user_query = """
                INSERT INTO users (first_name, last_name, email, phone, password, role, active_status, pwd_change_req)
                VALUES (%s, %s, %s, %s, %s, 'customer', 1, 1)
            """
            default_password = "Customer@123"
            user_values = (
                user_data["first_name"],
                user_data["last_name"],
                user_data["email"],
                user_data["phone"],
                hash_password(default_password)
            )
            cursor.execute(user_query, user_values)
            customer_id = cursor.lastrowid # Get new user_id

        # Step 2: Insert Sale (always)
        sale_query = """
            INSERT INTO salesinvoice (
                invoice_number, car_id, customer_id, customer_first_name, customer_last_name,
                customer_email, customer_phone, id_type, id_number, address,
                listing_price, discount, tax_percent, tax_amount, total_price,
                payment_method, payment_reference, staff_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        sale_values = (
            sale_data["invoice_number"],
            sale_data["car_id"],
            customer_id,
            sale_data["customer_first_name"],
            sale_data["customer_last_name"],
            sale_data["customer_email"],
            sale_data["customer_phone"],
            sale_data["id_type"],
            sale_data["id_number"],
            sale_data["address"],
            sale_data["listing_price"],
            sale_data["discount"],
            sale_data["tax_percent"],
            sale_data["tax_amount"],
            sale_data["total_price"],
            sale_data["payment_method"],
            sale_data["payment_reference"],
            sale_data["staff_id"]
        )

        cursor.execute(sale_query, sale_values)
        sale_id = cursor.lastrowid

        # Step 3: Update Car Status to 'Sold'
        update_car_query = "UPDATE car SET status = 'Sold' WHERE car_id = %s"
        cursor.execute(update_car_query, (sale_data["car_id"],))

        # Step 4: Commit the Transaction
        conn.commit()
        
        cursor.close()
        conn.close()
        return True, sale_id

    except mysql.connector.Error as e:
        conn.rollback()
        return False, f"Transaction failed: {e}"




#-----------------------------------------------------------------------------------------------------------------------------

def fetch_invoice_data(invoice_number):
    """
    Fetches all necessary data to generate an invoice PDF:
    - Sale details from salesinvoice
    - Car details from car
    - Staff name from users
    Returns:
        dict with fields required for invoice
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        # Fetch Sale Data
        sale_query = "SELECT * FROM salesinvoice WHERE invoice_number = %s"
        cursor.execute(sale_query, (invoice_number,))
        sale = cursor.fetchone()

        if not sale:
            return None

        # Fetch Car Data
        car_query = "SELECT make, model, year, car_color, fuel_type, title, vin, transmission, mileage FROM car WHERE car_id = %s"
        cursor.execute(car_query, (sale["car_id"],))
        car = cursor.fetchone()

        # Fetch Staff Data
        staff_query = "SELECT first_name, last_name FROM users WHERE user_id = %s"
        cursor.execute(staff_query, (sale["staff_id"],))
        staff = cursor.fetchone()

        cursor.close()
        conn.close()

        # Prepare final data dictionary
        invoice_data = {
            "invoice_number": sale["invoice_number"],
            "sale_date": sale["sale_date"],
            "customer_name": f"{sale['customer_first_name']} {sale['customer_last_name']}",
            "customer_address": sale.get("address", "Not Provided"),
            "customer_email": sale.get("customer_email", "Not Provided"),
            "customer_phone": sale.get("customer_phone", "Not Provided"),
            "car_make": car["make"] if car else "N/A",
            "car_model": car["model"] if car else "N/A",
            "car_year" : car["year"] if car else "N/A",
            "car_color": car["car_color"] if car else "N/A",
            "car_vin": car["vin"] if car else "N/A",
            "car_fuel": car["fuel_type"] if car else "N/A",
            "car_transmission": car["transmission"] if car else "N/A",
            "car_title": car["title"] if car else "N/A",
            "car_mileage": car["mileage"] if car else "N/A",
            "listing_price": sale["listing_price"],
            "discount": sale["discount"],
            "tax_percent": sale["tax_percent"],
            "tax_amount": sale["tax_amount"],
            "total_price": sale["total_price"],
            "payment_method": sale["payment_method"],
            "payment_reference": sale["payment_reference"],
            "staff_name": f"{staff['first_name']} {staff['last_name']}" if staff else "Staff"
        }

        return invoice_data

    except mysql.connector.Error as e:
        print(f"[DB ERROR fetch_invoice_data]: {e}")
        return None



#-----------------------------------------------------------------------------------------------------------------------------

def get_customer_purchases(user_id):
    """
    Fetch all car purchases made by a customer.

    Args:
        user_id (int): Customer's user ID.

    Returns:
        List of lists: Each inner list contains:
            [Car Details (Make Model Year), Sale Date, Sale Price, Payment Method, Invoice Number]
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT 
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_details,
                DATE_FORMAT(s.sale_date, '%m/%d/%Y') AS formatted_sale_date,
                CONCAT('$', FORMAT(s.total_price, 2)) AS formatted_sale_price,
                s.payment_method,
                s.invoice_number
            FROM salesinvoice s
            JOIN car c ON s.car_id = c.car_id
            WHERE s.customer_id = %s
            ORDER BY s.sale_date DESC
        """

        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Each row is already a list: [Car Details, Sale Date, Sale Price, Payment Method, Invoice Number]
        return rows

    except Exception as e:
        print(f"[DB ERROR] get_customer_purchases(): {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------


def get_available_time_slots(preferred_date):
    """
    Fetch available time slots for a given date by excluding booked slots.

    Args:
        preferred_date (str): Selected date in 'YYYY-MM-DD' format.

    Returns:
        List[str]: Available time slots (like "9:00 AM", "11:00 AM", etc.)
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Step 1: Define all possible time slots
        all_slots = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM"]

        # Step 2: Fetch already booked slots (excluding Cancelled)
        query = """
            SELECT 
                CASE 
                    WHEN reschedule_time IS NOT NULL THEN reschedule_time
                    ELSE preferred_time
                END AS booked_time
            FROM testdrivebooking
            WHERE 
                (CASE 
                    WHEN reschedule_date IS NOT NULL THEN reschedule_date
                    ELSE preferred_date
                END) = %s
            AND status NOT IN ('Cancelled')
        """
        cursor.execute(query, (preferred_date,))
        booked_slots_raw = cursor.fetchall()
        booked_slots = []

        for row in booked_slots_raw:
            time_delta = row[0]
            # Convert timedelta to total seconds and then to datetime.time
            total_seconds = time_delta.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            time_obj = datetime.strptime(f"{hours}:{minutes}", "%H:%M")
            formatted_time = time_obj.strftime("%I:%M %p").lstrip('0')  # Remove leading zero manually
            booked_slots.append(formatted_time)

        cursor.close()
        conn.close()

        # Step 3: Filter out booked slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]

        return available_slots

    except Exception as e:
        print(f"[DB ERROR] get_available_time_slots(): {e}")
        return []




#-----------------------------------------------------------------------------------------------------------------------------

def get_customer_test_drives(customer_id):
    """
    Fetches all test drives for a customer.

    Args:
        customer_id (int): Customer's user ID.

    Returns:
        List[Dict]: Each dict contains slot_datetime, car_info, status, last_modified, testdrive_id
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                td.test_drive_id,
                CASE 
                    WHEN td.reschedule_date IS NOT NULL AND td.reschedule_time IS NOT NULL
                        THEN CONCAT(DATE_FORMAT(td.reschedule_date, '%m/%d/%Y'), ', ', TIME_FORMAT(td.reschedule_time, '%h:%i %p'))
                    ELSE
                        CONCAT(DATE_FORMAT(td.preferred_date, '%m/%d/%Y'), ', ', TIME_FORMAT(td.preferred_time, '%h:%i %p'))
                END AS slot_datetime,
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_info,
                td.status,
                DATE_FORMAT(td.updated_at, '%m/%d/%Y, %h:%i %p') AS last_modified,
                td.cancellation_reason
            FROM testdrivebooking td
            JOIN car c ON td.car_id = c.car_id
            WHERE td.customer_id = %s
            ORDER BY
                CASE 
                    WHEN td.reschedule_date IS NOT NULL THEN td.reschedule_date
                    ELSE td.preferred_date
                END DESC,
                CASE 
                    WHEN td.reschedule_time IS NOT NULL THEN td.reschedule_time
                    ELSE td.preferred_time
                END DESC
        """

        cursor.execute(query, (customer_id,))
        test_drives = cursor.fetchall()
        cursor.close()
        conn.close()

        return test_drives

    except Exception as e:
        print(f"[DB ERROR] get_customer_test_drives(): {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def update_test_drive_schedule(test_drive_id, new_date, new_time):
    """
    Update reschedule_date and reschedule_time for a given test drive.

    Args:
        test_drive_id (int): Test Drive ID.
        new_date (str): New date in YYYY-MM-DD format.
        new_time (str): New time in HH:MM AM/PM format.

    Returns:
        Tuple: (True, "Success message") or (False, "Error message")
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Convert string time to TIME format
        from datetime import datetime
        time_obj = datetime.strptime(new_time, "%I:%M %p").time()

        query = """
            UPDATE testdrivebooking
            SET reschedule_date = %s,
                reschedule_time = %s,
                updated_at = CURRENT_TIMESTAMP,
                status = 'Pending'
            WHERE test_drive_id = %s
        """
        cursor.execute(query, (new_date, time_obj, test_drive_id))
        conn.commit()
        cursor.close()
        conn.close()

        return True, "Test drive rescheduled."
    except Exception as e:
        print(f"[DB ERROR update_test_drive_schedule]: {e}")
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------

def cancel_test_drive(test_drive_id, reason):
    """
    Cancel a test drive by setting status to 'Cancelled' and recording reason.

    Args:
        test_drive_id (int): ID of the test drive to cancel.
        reason (str): Reason for cancelling.

    Returns:
        Tuple (bool, str): (True, "Success") or (False, "Error message")
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            UPDATE testdrivebooking
            SET status = 'Cancelled',
                cancellation_reason = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE test_drive_id = %s
        """
        cursor.execute(query, (reason, test_drive_id))
        conn.commit()
        cursor.close()
        conn.close()

        return True, "Test drive cancelled successfully."
    except Exception as e:
        print(f"[DB ERROR] cancel_test_drive(): {e}")
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------

def insert_customer_inquiry(customer_id, car_id, message_text):
    """
    Insert a new customer inquiry into the customerinquiries table.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            INSERT INTO customerinquiries (car_id, customer_id, message_text, status)
            VALUES (%s, %s, %s, 'Pending')
        """
        cursor.execute(query, (car_id, customer_id, message_text))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Inquiry submitted."
    except mysql.connector.Error as e:
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------


def get_ongoing_test_drives(car_id=None):
    """
    Fetch ongoing test drives (Pending, Confirmed) for Admin/Staff.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                td.test_drive_id,
                CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
                CONCAT(
                    CASE 
                        WHEN td.reschedule_date IS NOT NULL THEN DATE_FORMAT(td.reschedule_date, '%m/%d/%Y')
                        ELSE DATE_FORMAT(td.preferred_date, '%m/%d/%Y')
                    END,
                    ', ',
                    CASE 
                        WHEN td.reschedule_time IS NOT NULL THEN TIME_FORMAT(td.reschedule_time, '%h:%i %p')
                        ELSE TIME_FORMAT(td.preferred_time, '%h:%i %p')
                    END
                ) AS slot_datetime,
                td.preferred_date,
                td.preferred_time,
                td.reschedule_date,
                td.reschedule_time,
                td.status,
                DATE_FORMAT(td.updated_at, '%m/%d/%Y, %h:%i %p') AS updated_at,
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_info
            FROM testdrivebooking td
            JOIN users u ON td.customer_id = u.user_id
            JOIN car c ON td.car_id = c.car_id
            WHERE td.status IN ('Pending', 'Confirmed')
        """

        params = []

        if car_id:
            query += " AND td.car_id = %s"
            params.append(car_id)

        query += """
            ORDER BY 
                CASE 
                    WHEN td.reschedule_date IS NOT NULL THEN td.reschedule_date
                    ELSE td.preferred_date
                END DESC,
                CASE 
                    WHEN td.reschedule_time IS NOT NULL THEN td.reschedule_time
                    ELSE td.preferred_time
                END DESC
        """

        cursor.execute(query, params)
        ongoing = cursor.fetchall()
        cursor.close()
        conn.close()

        return ongoing

    except Exception as e:
        print(f"[DB ERROR] get_ongoing_test_drives(): {e}")
        return []


#-----------------------------------------------------------------------------------------------------------------------------

def get_previous_test_drives(car_id=None, status_filter=None, search_text=None):
    """
    Fetch previous test drives (Completed, Cancelled) with optional search and filter.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                td.test_drive_id,
                CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
                CONCAT(
                    CASE 
                        WHEN td.reschedule_date IS NOT NULL THEN DATE_FORMAT(td.reschedule_date, '%m/%d/%Y')
                        ELSE DATE_FORMAT(td.preferred_date, '%m/%d/%Y')
                    END,
                    ', ',
                    CASE 
                        WHEN td.reschedule_time IS NOT NULL THEN TIME_FORMAT(td.reschedule_time, '%h:%i %p')
                        ELSE TIME_FORMAT(td.preferred_time, '%h:%i %p')
                    END
                ) AS slot_datetime,
                td.status, td.cancellation_reason,
                DATE_FORMAT(td.updated_at, '%m/%d/%Y, %h:%i %p') AS updated_at,
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_info
            FROM testdrivebooking td
            JOIN users u ON td.customer_id = u.user_id
            JOIN car c ON td.car_id = c.car_id
            WHERE td.status IN ('Completed', 'Cancelled')
        """

        params = []

        if car_id:
            query += " AND td.car_id = %s"
            params.append(car_id)

        if status_filter and status_filter != "All":
            query += " AND td.status = %s"
            params.append(status_filter)

        if search_text:
            query += " AND (CONCAT(u.first_name, ' ', u.last_name) LIKE %s OR CONCAT(c.make, ' ', c.model) LIKE %s)"
            params.append(f"%{search_text}%")
            params.append(f"%{search_text}%")

        query += """
            ORDER BY 
                CASE 
                    WHEN td.reschedule_date IS NOT NULL THEN td.reschedule_date
                    ELSE td.preferred_date
                END DESC,
                CASE 
                    WHEN td.reschedule_time IS NOT NULL THEN td.reschedule_time
                    ELSE td.preferred_time
                END DESC
        """

        cursor.execute(query, params)
        previous = cursor.fetchall()
        cursor.close()
        conn.close()

        return previous

    except Exception as e:
        print(f"[DB ERROR] get_previous_test_drives(): {e}")
        return []


#-----------------------------------------------------------------------------------------------------------------------------

def update_test_drive_status(test_drive_id, new_status):
    """
    Update test drive status (Confirm or Complete).
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            UPDATE testdrivebooking
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE test_drive_id = %s
        """

        cursor.execute(query, (new_status, test_drive_id))
        conn.commit()
        cursor.close()
        conn.close()

        return True, "Test drive status updated successfully."

    except Exception as e:
        print(f"[DB ERROR] update_test_drive_status(): {e}")
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------

def update_inquiry_message(message_id, new_message, by_role, user_id=None):
    """
    Update inquiry message_text (customer) or response_text (admin/staff) based on role.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if by_role == "customer":
            query = """
                UPDATE customerinquiries
                SET message_text = %s, updated_at = CURRENT_TIMESTAMP
                WHERE message_id = %s AND status = 'Pending'
            """
            cursor.execute(query, (new_message, message_id))

        elif by_role == "staff" or by_role == "admin":
            query = """
                UPDATE customerinquiries
                SET response_text = %s, staff_id = %s, status = 'Responded', updated_at = CURRENT_TIMESTAMP
                WHERE message_id = %s AND status = 'Pending'
            """
            cursor.execute(query, (new_message, user_id, message_id))
        else:
            return False, "Invalid role for updating inquiry."

        
        conn.commit()
        cursor.close()
        conn.close()

        return True, "Inquiry updated successfully."

    except Exception as e:
        print(f"[DB ERROR] update_inquiry_message(): {e}")
        return False, f"Database error: {e}"



#-----------------------------------------------------------------------------------------------------------------------------

def withdraw_inquiry(message_id, by_role):
    """
    Withdraw inquiry (set status to 'Withdrawn').
    Both customer and staff can withdraw pending inquiries.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if by_role == "customer":
            query = """
                UPDATE customerinquiries
                SET status = 'Withdrawn', updated_at = CURRENT_TIMESTAMP
                WHERE message_id = %s AND status = 'Pending'
            """
        elif by_role == "staff" or by_role == "admin":
            query = """
                UPDATE customerinquiries
                SET status = 'Withdrawn', updated_at = CURRENT_TIMESTAMP
                WHERE message_id = %s AND (status = 'Pending' OR status = 'Responded')
            """
        else:
            return False, "Invalid role for withdrawing inquiry."

        cursor.execute(query, (message_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return True, "Inquiry withdrawn successfully."

    except Exception as e:
        print(f"[DB ERROR] withdraw_inquiry(): {e}")
        return False, f"Database error: {e}"


#-----------------------------------------------------------------------------------------------------------------------------

def fetch_customer_inquiries(cust_id=None, car_id=None, status_filter=None, search_text=None, message_id=None):
    """
    Fetch inquiries with optional filters: by customer, by car, by status, by search text.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                ci.message_id,
                ci.message_text,
                ci.response_text,
                ci.status,
                ci.staff_id,
                ci.created_at,
                DATE_FORMAT(ci.updated_at, '%m/%d/%Y, %h:%i %p') AS updated_at,
                c.make AS car_make,
                c.model AS car_model,
                c.year AS car_year,
                CONCAT(u.first_name, ' ', u.last_name) AS customer_name
            FROM
                customerinquiries ci
            JOIN
                car c ON ci.car_id = c.car_id
            JOIN
                users u ON ci.customer_id = u.user_id
            WHERE 1=1
        """
        params = []

        if message_id:
            query += " AND ci.message_id = %s"
            params.append(message_id)
        if cust_id:
            query += " AND ci.customer_id = %s"
            params.append(cust_id)

            # ❗ Additionally, hide withdrawn inquiries for customer
            query += " AND ci.status != 'Withdrawn'"

        if car_id:
            query += " AND ci.car_id = %s"
            params.append(car_id)

        if status_filter and status_filter != "All":
            query += " AND ci.status = %s"
            params.append(status_filter)

        if search_text:
            query += """ AND (
                CONCAT(c.make, ' ', c.model, ' ', c.year) LIKE %s
                OR CONCAT(u.first_name, ' ', u.last_name) LIKE %s
                OR ci.message_text LIKE %s
            )"""
            params.extend([f"%{search_text}%"] * 3)

        query += " ORDER BY ci.created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if message_id:
            return rows[0] if rows else None  # Return only one record
        else:
            return rows

    except Exception as e:
        print(f"[DB ERROR] fetch_customer_inquiries(): {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def get_distinct_payment_methods():
    """
    Fetches a list of distinct payment methods recorded in the salesinvoice table.

    Returns:
        List[str]: A list of unique payment method names, such as ['Cash', 'Card', 'Bank Transfer'].
                   Returns an empty list if no methods found or on database error.

    Usage:
        Used to dynamically populate the 'Payment Filter' dropdown in Sales History page.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT payment_method 
            FROM salesinvoice 
            WHERE payment_method IS NOT NULL
        """
        cursor.execute(query)
        methods = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return methods
    except Exception as e:
        print(f"[DB ERROR] get_distinct_payment_methods: {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def get_distinct_sale_years():
    """
    Fetches a list of distinct years extracted from the sale_date column in the salesinvoice table.

    Returns:
        List[str]: A list of unique years as strings, sorted in descending order (e.g., ['2025', '2024', '2023']).
                   Returns an empty list if no years found or on database error.

    Usage:
        Used to dynamically populate the 'Year Filter' dropdown in Sales History page.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT YEAR(sale_date) 
            FROM salesinvoice 
            WHERE sale_date IS NOT NULL
            ORDER BY YEAR(sale_date) DESC
        """
        cursor.execute(query)
        years = [str(row[0]) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return years
    except Exception as e:
        print(f"[DB ERROR] get_distinct_sale_years: {e}")
        return []


#-----------------------------------------------------------------------------------------------------------------------------

def fetch_sales_records(payment_filter=None, year_filter=None, search_value=None):
    """
    Fetches sales records from the database with optional payment method, year, and smart multi-field search.

    Args:
        payment_filter (str, optional): Payment method to filter (e.g., "Cash", "Card"). Defaults to None (All).
        year_filter (str, optional): Year to filter (e.g., "2025"). Defaults to None (All).
        search_value (str, optional): Search keyword to match across multiple fields:
                                      Sale ID, Car ID, Invoice No, Customer Name, Customer ID, VIN, Car Name, Sale Date.

    Returns:
        List[Dict]: List of sales records, each as a dictionary.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                si.sale_id,
                si.car_id,
                DATE_FORMAT(si.sale_date, '%m/%d/%Y') AS formatted_sale_date,
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_details,
                CONCAT(si.customer_first_name, ' ', si.customer_last_name) AS customer_name,
                c.vin AS vin_number,
                CONCAT('$', FORMAT(si.total_price, 0)) AS formatted_price,
                si.payment_method,
                si.invoice_number
            FROM salesinvoice si
            JOIN car c ON si.car_id = c.car_id
            WHERE 1=1
        """

        params = []

        # Payment Method Filter
        if payment_filter and payment_filter != "All":
            query += " AND si.payment_method = %s"
            params.append(payment_filter)

        # Year Filter
        if year_filter and year_filter != "All":
            query += " AND YEAR(si.sale_date) = %s"
            params.append(year_filter)

        # Smart Search across multiple fields
        if search_value:
            query += """
            AND (
                si.sale_id LIKE %s
                OR c.car_id LIKE %s
                OR si.invoice_number LIKE %s
                OR CONCAT(si.customer_first_name, ' ', si.customer_last_name) LIKE %s
                OR si.customer_id LIKE %s
                OR c.vin LIKE %s
                OR CONCAT(c.make, ' ', c.model, ' ', c.year) LIKE %s
                OR DATE_FORMAT(si.sale_date, '%%m/%%d/%%Y') LIKE %s
            )
            """
            wildcard_search = f"%{search_value}%"
            params.extend([wildcard_search] * 8)

        query += " ORDER BY si.sale_date DESC"

        cursor.execute(query, params)
        sales = cursor.fetchall()

        cursor.close()
        conn.close()
        return sales

    except Exception as e:
        print(f"[DB ERROR fetch_sales_records]: {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def update_user_profile(user_id, role, updated_data):
    """
    Update a user's profile (first name, last name, email, phone) in the users table.

    Parameters:
        user_id (int): The user's ID
        role (str): Role of the user (Customer, Admin, Staff)
        updated_data (dict): Dict of changed fields: { "first_name": ..., "email": ... }

    Returns:
        (bool, str): Success flag and message
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if not updated_data:
            return False, "No changes provided."

        # Dynamically build SET clause
        set_clause = ", ".join([f"{field} = %s" for field in updated_data])
        values = list(updated_data.values())

        query = f"""
            UPDATE users
            SET {set_clause}, updated_at = NOW()
            WHERE user_id = %s AND role = %s
        """
        values.extend([user_id, role])

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Profile updated successfully."
    except Exception as e:
        print(f"[DB ERROR] update_user_profile(): {e}")
        return False, f"Database error: {str(e)}"



#-----------------------------------------------------------------------------------------------------------------------------

def get_user_profile(user_id):
    """
    Fetches the profile details of a user based on user_id.

    Args:
        user_id (int): The unique ID of the user.

    Returns:
        dict: Profile info including first name, last name, email, phone, role, user_since, last_updated
              OR None if not found.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                first_name,
                last_name,
                email,
                phone,
                role,
                DATE_FORMAT(created_at, '%m/%d/%Y') AS user_since,
                DATE_FORMAT(updated_at, '%m/%d/%Y %r') AS last_updated
            FROM users
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"[DB ERROR] get_user_profile(): {e}")
        return None


#-----------------------------------------------------------------------------------------------------------------------------


def get_customer_reviewable_purchases(customer_id):
    """
    Returns a list of purchases made by the customer, along with review info if exists.

    Each item:
        {
            "car_id": ...,
            "car_name": "Make Model Year",
            "sale_date": "MM/DD/YYYY",
            "rating": int or None,
            "review_text": str or None,
            "review_id": int or None
        }
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                s.car_id,
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_name,
                DATE_FORMAT(s.sale_date, '%m/%d/%Y') AS sale_date,
                r.rating,
                r.review_text,
                r.review_id,
                r.response_text,
                r.status
            FROM salesinvoice s
            JOIN car c ON s.car_id = c.car_id
            LEFT JOIN reviewandrating r 
                ON r.car_id = s.car_id AND r.customer_id = s.customer_id
            WHERE s.customer_id = %s 
            ORDER BY s.sale_date DESC
        """

        cursor.execute(query, (customer_id,))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    except Exception as e:
        print(f"[DB ERROR] get_customer_reviewable_purchases(): {e}")
        return []





#-----------------------------------------------------------------------------------------------------------------------------

def insert_customer_review(car_id, customer_id, rating, review_text):
    """
    Inserts a review from a customer for a car they've purchased.

    Args:
        car_id (int): ID of the car being reviewed
        customer_id (int): ID of the customer
        rating (int): Star rating (1 to 5)
        review_text (str): Optional review message

    Returns:
        Tuple (bool, str): Success status and message
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO reviewandrating (car_id, customer_id, rating, review_text, status)
            VALUES (%s, %s, %s, %s, 'Active')
        """
        cursor.execute(query, (car_id, customer_id, rating, review_text))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Review submitted successfully."
    except Exception as e:
        print(f"[DB ERROR] insert_customer_review(): {e}")
        return False, "Failed to submit review."


#-----------------------------------------------------------------------------------------------------------------------------

def update_customer_review(review_id, new_rating, new_review):
    """
    Updates an existing customer review by review_id.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE reviewandrating
            SET rating = %s,
                review_text = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
        """
        cursor.execute(query, (new_rating, new_review, review_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Review updated successfully."
    except Exception as e:
        print(f"[DB ERROR] update_customer_review(): {e}")
        return False, "Failed to update review."



#-----------------------------------------------------------------------------------------------------------------------------

def get_all_reviews(search_text=None, status_filter="All"):
    """
    Fetches all reviews from the system with optional filters.

    Returns: list of dicts with:
        review_id, car_name, customer_name, rating, review_text, status, reviewed_date
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                r.review_id,
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS car_name,
                CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
                r.rating,
                r.review_text,
                r.status,
                DATE_FORMAT(r.created_at, '%%m/%%d/%%Y') AS reviewed_date,
                r.response_text
            FROM reviewandrating r
            JOIN car c ON r.car_id = c.car_id
            JOIN users u ON r.customer_id = u.user_id
            WHERE 1=1
        """
        params = []

        if status_filter != "All":
            query += " AND r.status = %s"
            params.append(status_filter)

        if search_text:
            query += """ AND (
                CONCAT(c.make, ' ', c.model, ' ', c.year) LIKE %s OR
                CONCAT(u.first_name, ' ', u.last_name) LIKE %s OR
                r.review_text LIKE %s
            )"""
            like = f"%{search_text}%"
            params.extend([like, like, like])

        query += " ORDER BY r.created_at DESC"

        cursor.execute(query, params)
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        return reviews

    except Exception as e:
        print(f"[DB ERROR] get_all_reviews(): {e}")
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def update_review_status(review_id, new_status):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reviewandrating
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
        """, (new_status, review_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] update_review_status(): {e}")
        return False


#-----------------------------------------------------------------------------------------------------------------------------

def respond_to_review(review_id, response_text):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE reviewandrating
            SET response_text = %s, updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
        """
        cursor.execute(query, (response_text, review_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Response saved."
    except Exception as e:
        print(f"[DB ERROR] respond_to_review(): {e}")
        return False, "Failed to save response."


#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------

def fetch_sales_kpis(start_date=None, end_date=None):
    """
    Fetch sales KPIs filtered by a given date range.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        base_query = """
            SELECT 
                COUNT(*) AS total_sales,
                IFNULL(SUM(total_price), 0) AS revenue,
                IFNULL(AVG(total_price), 0) AS avg_price
            FROM salesinvoice
            WHERE 1=1
        """
        params = []

        if start_date and end_date:
            base_query += " AND DATE(sale_date) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        cursor.execute(base_query, params)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "cars_sold": result[0],
            "revenue": float(result[1]),
            "avg_price": float(result[2])
        }

    except Exception as e:
        print(f"[DB ERROR fetch_sales_kpis]: {e}")
        return {"cars_sold": 0, "revenue": 0.0, "avg_price": 0.0}



#-----------------------------------------------------------------------------------------------------------------------------

def get_sales_trend_data(start_date, end_date, group_by="day"):
    """
    Returns {label: sales_count} based on date range and grouping (day, month, year)
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if group_by == "day":
            query = """
                SELECT DATE(sale_date) as label, COUNT(*) as total
                FROM salesinvoice
                WHERE DATE(sale_date) BETWEEN %s AND %s
                GROUP BY label ORDER BY label
            """
        elif group_by == "month":
            query = """
                SELECT DATE_FORMAT(sale_date, '%b-%Y') as label, COUNT(*) as total
                FROM salesinvoice
                WHERE DATE(sale_date) BETWEEN %s AND %s
                GROUP BY label ORDER BY sale_date
            """
        elif group_by == "year":
            query = """
                SELECT YEAR(sale_date) as label, COUNT(*) as total
                FROM salesinvoice
                WHERE DATE(sale_date) BETWEEN %s AND %s
                GROUP BY label ORDER BY label
            """
        else:
            return {}

        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        return {str(row[0]): row[1] for row in rows}

    except Exception as e:
        print(f"[DB ERROR get_sales_trend_data]: {e}")
        return {}


#-----------------------------------------------------------------------------------------------------------------------------

def fetch_sales_reports(start_date, end_date):
    """
    Fetches filtered sales records for export, grouped by day/month/year if needed.
    Returns a list of dictionaries suitable for table or download.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                CONCAT(c.make, ' ', c.model, ' ', c.year) AS Car,
                DATE_FORMAT(si.sale_date, '%Y-%m-%d') AS Date,
                si.total_price AS Price,
                si.payment_method AS Payment,
                si.invoice_number AS `Invoice Number`
            FROM salesinvoice si
            JOIN car c ON si.car_id = c.car_id
            WHERE DATE(si.sale_date) BETWEEN %s AND %s
            ORDER BY si.sale_date ASC
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return rows

    except Exception as e:
        print("[DB ERROR fetch_sales_records]:", e)
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def fetch_operations_kpis(start_date, end_date):
    """
    Returns KPI metrics for Operations:
    - Total test drives
    - Completed test drives
    - Inquiry totals
    - Inquiries responded
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Test Drive Counts
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
            FROM testdrivebooking
            WHERE DATE(updated_at) BETWEEN %s AND %s
        """, (start_date, end_date))
        td_total, td_completed = cursor.fetchone()

        # Inquiry Counts
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Responded' THEN 1 ELSE 0 END) AS responded
            FROM customerinquiries
            WHERE DATE(updated_at) BETWEEN %s AND %s
        """, (start_date, end_date))
        iq_total, iq_responded = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "test_drives_total": td_total or 0,
            "test_drives_completed": td_completed or 0,
            "inquiries_total": iq_total or 0,
            "inquiries_responded": iq_responded or 0
        }

    except Exception as e:
        print("[DB ERROR fetch_operations_kpis]:", e)
        return {
            "test_drives_total": 0,
            "test_drives_completed": 0,
            "inquiries_total": 0,
            "inquiries_responded": 0
        }



#-----------------------------------------------------------------------------------------------------------------------------


def get_test_drive_trend_data(start_date, end_date, group_by="day"):
    """
    Returns {label: count} for test drive bookings over time, grouped by day/month/year.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        if group_by == "day":
            query = """
                SELECT DATE(updated_at) AS label, COUNT(*) AS total
                FROM testdrivebooking
                WHERE DATE(updated_at) BETWEEN %s AND %s
                GROUP BY label ORDER BY label
            """
        elif group_by == "month":
            query = """
                SELECT DATE_FORMAT(updated_at, '%b-%Y') AS label, COUNT(*) AS total
                FROM testdrivebooking
                WHERE DATE(updated_at) BETWEEN %s AND %s
                GROUP BY label ORDER BY MIN(updated_at)
            """
        elif group_by == "year":
            query = """
                SELECT YEAR(updated_at) AS label, COUNT(*) AS total
                FROM testdrivebooking
                WHERE DATE(updated_at) BETWEEN %s AND %s
                GROUP BY label ORDER BY label
            """
        else:
            return {}

        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {str(label): count for label, count in rows}

    except Exception as e:
        print("[DB ERROR get_test_drive_trend_data]:", e)
        return {}


#-----------------------------------------------------------------------------------------------------------------------------

def get_inquiry_status_breakdown(start_date, end_date):
    """
    Returns a breakdown of inquiry statuses: {status: count}
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT status, COUNT(*) AS total
            FROM customerinquiries
            WHERE DATE(updated_at) BETWEEN %s AND %s
            GROUP BY status
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {status: count for status, count in rows}

    except Exception as e:
        print("[DB ERROR get_inquiry_status_breakdown]:", e)
        return {}


#-----------------------------------------------------------------------------------------------------------------------------

def fetch_testdrive_records(start_date, end_date):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                test_drive_id, customer_id, car_id, preferred_date, preferred_time, status, staff_id, reschedule_date, 
                reschedule_time, updated_at
            FROM testdrivebooking
            WHERE DATE(updated_at) BETWEEN %s AND %s
            ORDER BY updated_at DESC
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows

    except Exception as e:
        print("[DB ERROR fetch_testdrive_records]:", e)
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def fetch_inquiry_records(start_date, end_date):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                message_id, customer_id, car_id, staff_id, message_text, response_text, status, updated_at
            FROM customerinquiries
            WHERE DATE(updated_at) BETWEEN %s AND %s
            ORDER BY updated_at DESC
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows

    except Exception as e:
        print("[DB ERROR fetch_inquiry_records]:", e)
        return []


#-----------------------------------------------------------------------------------------------------------------------------


def fetch_inventory_kpis(start_date, end_date):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = f"""
            SELECT
                (SELECT COUNT(*) FROM car WHERE status = 'Available') AS total_in_stock,
                (SELECT COUNT(*) FROM car WHERE DATE(created_at) BETWEEN %s AND %s) AS new_arrivals,
                (SELECT COUNT(*) FROM salesinvoice WHERE DATE(sale_date) BETWEEN %s AND %s) AS sold_this_period,
                (SELECT COUNT(*) FROM car WHERE status = 'Available' AND DATEDIFF(CURDATE(), created_at) > 60) AS older_stock,
                (SELECT ROUND(AVG(DATEDIFF(CURDATE(), created_at)), 1) FROM car WHERE status = 'Available') AS avg_days_in_stock
        """
        cursor.execute(query, (start_date, end_date, start_date, end_date))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    except Exception as e:
        print("[DB ERROR fetch_inventory_kpis]:", e)
        return {
            "total_in_stock": 0,
            "new_arrivals": 0,
            "sold_this_period": 0,
            "older_stock": 0,
            "avg_days_in_stock": 0.0
        }


#-----------------------------------------------------------------------------------------------------------------------------

def get_brand_distribution():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT make, COUNT(*) AS count
            FROM car
            WHERE status = 'Available'
            GROUP BY make
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {make: count for make, count in rows}

    except Exception as e:
        print("[DB ERROR get_brand_distribution]:", e)
        return {}



#-----------------------------------------------------------------------------------------------------------------------------

def fetch_available_car_records(start_date, end_date):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT car_id, make, model, year, VIN, mileage, fuel_type, car_color, car_condition,
                   price, economy, created_at
            FROM car
            WHERE status = 'Available' AND DATE(created_at) BETWEEN %s AND %s
            ORDER BY created_at DESC
        """, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print("[DB ERROR fetch_available_car_records]:", e)
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def fetch_sold_car_records(start_date, end_date):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.sale_id, s.sale_date, s.total_price, s.payment_method, s.payment_reference,
                   c.make, c.model, c.year, c.VIN
            FROM salesinvoice s
            JOIN car c ON s.car_id = c.car_id
            WHERE DATE(s.sale_date) BETWEEN %s AND %s
            ORDER BY s.sale_date DESC
        """, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print("[DB ERROR fetch_sold_car_records]:", e)
        return []



#-----------------------------------------------------------------------------------------------------------------------------

def get_fuel_type_distribution():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fuel_type, COUNT(*) AS count
            FROM car
            WHERE status = 'Available'
            GROUP BY fuel_type
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {fuel_type: count for fuel_type, count in rows}

    except Exception as e:
        print("[DB ERROR get_fuel_type_distribution]:", e)
        return {}



#-----------------------------------------------------------------------------------------------------------------------------

def get_sales_by_payment_method(start_date, end_date):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            SELECT payment_method, COUNT(*) as count
            FROM salesinvoice
            WHERE DATE(sale_date) BETWEEN %s AND %s
            GROUP BY payment_method
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {method: count for method, count in rows}
    except Exception as e:
        print("[DB ERROR get_sales_by_payment_method]:", e)
        return {}



#-----------------------------------------------------------------------------------------------------------------------------




#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------




#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------




#-----------------------------------------------------------------------------------------------------------------------------
