import psycopg2
import csv
DB_NAME = "lab10_db"
DB_USER = "postgres"
DB_PASS = "gogetthem"
DB_HOST = "localhost"
DB_PORT = "5432"
conn = None
cursor = None


def is_valid_phone(phone):
    return all(c.isdigit() or c in [' ', '+', '-'] for c in phone)

#CHANGED
def find_contacts_by_pattern(cur, pattern):
    try:

        cur.execute("SELECT * FROM find_contacts_by_pattern(%s)", (pattern,))
        results = cur.fetchall()
        return results
    except psycopg2.Error as e:
        print(f"Error calling find_contacts_by_pattern function: {e}")
        return []

#CHANGED
def insert_or_update_user(cur, name, phone):
    try:
        if not is_valid_phone(phone):
         return False, "Invalid phone number format (checked in Python)."
        cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))
        return True, f"Procedure insert_or_update_user called for {name}."
    except psycopg2.Error as e:
        print(f"Database error calling insert_or_update_user: {e}")
        return False, str(e)

#CHANGED
def insert_many_users(cur, users):
    valid_users = []
    incorrect_data = []
    for name, phone in users:
        if not is_valid_phone(phone):
            incorrect_data.append({"name": name, "phone": phone, "error": "Invalid phone number format."})
        else:
            valid_users.append((name, phone))
        if valid_users:
            try:
                cur.execute("SELECT * FROM insert_many_users_func(%s)", (valid_users,))  
                db_errors = cur.fetchall()
                db_errors_list = [{"name": row[0], "phone": row[1], "error": row[2]} for row in db_errors]
                incorrect_data.extend(db_errors_list)  

            except psycopg2.Error as e:
                print(f"Error calling insert_many_users_func: {e}")
                db_error_users = [{"name": u[0], "phone": u[1], "error": str(e)} for u in valid_users]
                incorrect_data.extend(db_error_users)


        return incorrect_data



#CHANGED
def get_contacts_paginated(cur, limit, offset):
    try:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        results = cur.fetchall()
        return results
    except psycopg2.Error as e:
        print(f"Error fetching paginated contacts: {e}")
        return []

#CHANGED
def delete_contact_by_username_or_phone(cur, search_term):
    try:
        cursor.execute("CALL delete_contact_by_username_or_phone(%s)", (search_term,))
        print(f"Procedure delete_contact_by_username_or_phone called for '{search_term}'. Check DB messages for details.")
        return True
    except psycopg2.Error as e:
        print(f"Error calling delete_contact_by_username_or_phone procedure: {e}")
        return False


def insert_from_console(cur):
    try:
        name = input("Enter user name: ")
        phone = input("Enter phone number: ")
        if not name or not phone:
            print("Name and phone number cannot be empty. Insertion cancelled.")
            return
        if not is_valid_phone(phone):
            print("Invalid phone number format. Please use numbers, spaces, +, or -.")
            return
        insert_query = "INSERT INTO phonebook (user_name, phone_number) VALUES (%s, %s)"
        cur.execute(insert_query, (name, phone))
        print(f"Data ({name}, {phone}) successfully added from console.")
    except psycopg2.Error as e:
        print(f"Error inserting data from console: {e}")

def insert_from_csv(cur, filename='contacts.csv'):
    inserted_count = 0
    failed_count = 0
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            print(f"Reading from CSV file '{filename}' with columns: {header}")
            insert_query = "INSERT INTO phonebook (user_name, phone_number) VALUES (%s, %s)"
            for i, row in enumerate(reader, start=1):
                if len(row) == 2:
                    user_name = row[0].strip()
                    phone_number = row[1].strip()
                    if not user_name or not phone_number:
                        print(f"Skipping row {i+1}: empty values ({row})")
                        failed_count += 1
                        continue
                    if not is_valid_phone(phone_number):
                        print(f"Skipping row {i+1}: invalid phone number format ({phone_number})")
                        failed_count += 1
                        continue
                    try:
                        cur.execute(insert_query, (user_name, phone_number))
                        inserted_count += 1
                    except psycopg2.Error as e:
                        print(f"Error inserting row {i+1} {row}: {e}")
                        failed_count += 1
                else:
                    print(f"Skipping invalid row {i+1} in CSV (expected 2 columns): {row}")
                    failed_count += 1
        print(f"CSV import finished. Success: {inserted_count}, Errors/Skipped: {failed_count}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred during CSV import: {e}")

def update_contact(cur):
    try:
        search_term = input("Enter ID, name, or phone number of the contact to update: ")
        find_query = """
            SELECT id, user_name, phone_number FROM phonebook
            WHERE CAST(id AS TEXT) = %s OR user_name = %s OR phone_number = %s
        """
        cur.execute(find_query, (search_term, search_term, search_term))
        contacts = cur.fetchall()

        if not contacts:
            print(f"Contact '{search_term}' not found.")
            return
        elif len(contacts) > 1:
            print("Multiple contacts found. Please refine your search by ID.")
            for contact in contacts:
                print(f"  ID={contact[0]}, Name={contact[1]}, Phone={contact[2]}")
            return
        else:
            contact = contacts[0]
            print(f"Contact found: ID={contact[0]}, Name={contact[1]}, Phone={contact[2]}")
            current_id = contact[0]
            new_name = input(f"Enter new name (leave empty to keep '{contact[1]}'): ").strip()
            new_phone = input(f"Enter new phone number (leave empty to keep '{contact[2]}'): ").strip()

            update_fields = []
            update_values = []

            if new_name:
                update_fields.append("user_name = %s")
                update_values.append(new_name)
            if new_phone:
                if not is_valid_phone(new_phone):
                    print("Invalid phone number format. Update cancelled.")
                    return
                update_fields.append("phone_number = %s")
                update_values.append(new_phone)

            if not update_fields:
                print("No data to update.")
                return

            update_values.append(current_id)
            update_query = f"UPDATE phonebook SET {', '.join(update_fields)} WHERE id = %s"

            try:
                cur.execute(update_query, tuple(update_values))
                updated_rows = cur.rowcount
                print(f"Contact successfully updated. Rows affected: {updated_rows}")
            except psycopg2.Error as e:
                print(f"Error updating contact: {e}")

    except psycopg2.Error as e:
        print(f"Error searching for contact to update: {e}")

def query_contacts(cur, limit=None):
    try:
        print("\n--- Contact Search ---")
        name_pattern = input("Enter part of the name to search (Enter to skip): ").strip()
        phone_pattern = input("Enter part of the phone number to search (Enter to skip): ").strip()
        base_query = "SELECT id, user_name, phone_number FROM phonebook"
        filters = []
        params = []

        if name_pattern:
            filters.append("user_name ILIKE %s")
            params.append(f"%{name_pattern}%")
        if phone_pattern:
            filters.append("phone_number LIKE %s")
            params.append(f"%{phone_pattern}%")

        if filters:
            query = f"{base_query} WHERE {' AND '.join(filters)}"
        else:
            show_all = input("No filters set. Show all records? (yes/no, default: yes): ").lower().strip()
            if show_all == 'no':
                print("Search cancelled.")
                return
            query = base_query

        query += " ORDER BY user_name"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cur.execute(query, tuple(params))
        results = cur.fetchall()

        if results:
            print("\n--- Search Results ---")
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
            print(f"Records found: {len(results)}")
            print("----------------------\n")
        else:
            print("No contacts matching the search criteria were found.")
    except psycopg2.Error as e:
        print(f"Error querying data: {e}")

def delete_contact(cur):
    try:
        search_term = input("Enter ID, name, or phone number of the contact to DELETE: ")
        find_query = """
            SELECT id, user_name, phone_number FROM phonebook
            WHERE CAST(id AS TEXT) = %s OR user_name = %s OR phone_number = %s
        """
        cur.execute(find_query, (search_term, search_term, search_term))
        contacts_to_delete = cur.fetchall()

        if not contacts_to_delete:
            print(f"Contact '{search_term}' not found.")
            return

        print("The following contacts will be deleted:")
        ids_to_delete = []
        for contact in contacts_to_delete:
            print(f"  ID={contact[0]}, Name={contact[1]}, Phone={contact[2]}")
            ids_to_delete.append(contact[0])
        confirm = input(f"Are you sure you want to delete these {len(contacts_to_delete)} contact(s)? (yes/no): ").lower().strip()

        if confirm == 'yes':
            ids_tuple = tuple(ids_to_delete)
            delete_query = "DELETE FROM phonebook WHERE id = ANY(%s::int[])"
            cur.execute(delete_query, (ids_tuple,))
            deleted_rows = cur.rowcount
            print(f"Successfully deleted contacts: {deleted_rows}")
        else:
            print("Deletion cancelled.")
    except psycopg2.Error as e:
        print(f"Error deleting contact: {e}")

def print_menu():
    print("\n===== Phonebook Menu =====")
    print("1. Add contact (manually)")
    print("2. Load contacts from CSV (contacts.csv)")
    print("3. Show/Search contacts")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Find contacts by pattern")
    print("7. Insert or update user")
    print("8. Insert many users")
    print("9. Get contacts paginated")
    print("10. Delete contact by username or phone")
    print("0. Exit")
    print("==========================")

try:

    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    print("Successfully connected to the database!")
    conn.autocommit = True
    cursor = conn.cursor()
    print("Cursor created.")

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        user_name VARCHAR(100) NOT NULL,
        phone_number VARCHAR(20) NOT NULL UNIQUE
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'phonebook' created successfully or already exists.")
    except psycopg2.Error as e:
        print(f"Critical error creating table 'phonebook': {e}")
        if cursor: cursor.close()
        if conn: conn.close()
        exit()

    while True:
        print_menu()
        choice = input("Choose an action (enter number): ").strip()
        if choice == '1':
            insert_from_console(cursor)
        elif choice == '2':
            insert_from_csv(cursor)
        elif choice == '3':
            query_contacts(cursor)
        elif choice == '4':
            update_contact(cursor)
        elif choice == '5':
            delete_contact(cursor)
        elif choice == '6':
            pattern = input("Enter search pattern (name, surname, or phone): ")
            contacts = find_contacts_by_pattern(cursor, pattern)
            if contacts:
                print("\n--- Search Results ---")
                for row in contacts:
                    print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
                print(f"Records found: {len(contacts)}")
                print("----------------------\n")
            else:
                print("No contacts matching the search criteria were found.")
        elif choice == '7':
            name = input("Enter user name: ")
            phone = input("Enter phone number: ")
            success, message = insert_or_update_user(cursor, name, phone)
            if success:
                print(message)
            else:
                print(f"Error: {message}")
        elif choice == '8':
            users = []
            while True:
                name = input("Enter user name (or type 'done'): ")
                if name.lower() == 'done':
                    break
                phone = input("Enter phone number: ")
                users.append((name, phone))
            incorrect_data = insert_many_users(cursor, users)
            if incorrect_data:
                print("\n--- Incorrect Data ---")
                for data in incorrect_data:
                    print(f"Name: {data['name']}, Phone: {data['phone']}, Error: {data['error']}")
                print("----------------------\n")
            else:
                print("All users inserted successfully.")
        elif choice == '9':
            limit = int(input("Enter limit: "))
            offset = int(input("Enter offset: "))
            contacts = get_contacts_paginated(cursor, limit, offset)
            if contacts:
                print("\n--- Paginated Contacts ---")
                for row in contacts:
                    print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
                print("----------------------\n")
            else:
                print("No contacts found.")
        elif choice == '10':
            search_term = input("Enter username or phone number to delete: ")
            deleted_rows = delete_contact_by_username_or_phone(cursor, search_term)
            if deleted_rows > 0: 
                print(f"Successfully deleted contacts matching '{search_term}'.") 
            else:
                print("No contacts found for the given term or deletion failed/cancelled.") 
        elif choice == '0':
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL or performing operations: {e}")

finally:
    print("\nDatabase work is finishing.")
    if cursor is not None:
        cursor.close()
        print("Cursor closed.")
    if conn is not None:
        conn.close()
        print("PostgreSQL connection closed.")

