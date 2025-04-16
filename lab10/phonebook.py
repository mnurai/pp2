import psycopg2 #PostgreSQL database interaction 
import csv #reading CSV files

#Database connection parameters
DB_NAME = "lab10_db"  # Database name created in pgAdmin
DB_USER = "postgres"  # PostgreSQL user name 
DB_PASS = "gogetthem" #password
DB_HOST = "localhost"  # Server address 
DB_PORT = "5432"  # Server port

# Variables for connection and cursor
conn = None
cursor = None

#Function to insert data from console
def insert_from_console(cur):
    try:
        name = input("Enter user name: ")
        phone = input("Enter phone number: ")
        # Check to avoid inserting empty rows
        if not name or not phone:
            print("Name and phone number cannot be empty. Insertion cancelled.")
            return
        insert_query = "INSERT INTO phonebook (user_name, phone_number) VALUES (%s, %s)"
        cur.execute(insert_query, (name, phone))
        print(f"Data ({name}, {phone}) successfully added from console.")
    except psycopg2.Error as e: #Catch database-related errors
        print(f"Error inserting data from console: {e}")

#Function to insert data from CSV file
def insert_from_csv(cur, filename='contacts.csv'):
    inserted_count = 0
    failed_count = 0
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f) #read each row
            header = next(reader)  #read headers
            print(f"Reading from CSV file '{filename}' with columns: {header}")
            insert_query = "INSERT INTO phonebook (user_name, phone_number) VALUES (%s, %s)"
            for i, row in enumerate(reader, start=1):  # Start row numbering from 1 for messages
                if len(row) == 2: #user name and phone number
                    user_name = row[0].strip()
                    phone_number = row[1].strip()
                    if not user_name or not phone_number:
                        print(f"Skipping row {i+1}: empty values ({row})")
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

# Function to update an existing contact
def update_contact(cur):
    try:
        search_term = input("Enter ID, name, or phone number of the contact to update: ")
        # Search by ID, name, or phone
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

#Function to search and display contacts
def query_contacts(cur, limit=None):
    try:
        print("\n--- Contact Search ---")
        name_pattern = input("Enter part of the name to search (Enter to skip): ").strip()
        phone_pattern = input("Enter part of the phone number to search (Enter to skip): ").strip()

        base_query = "SELECT id, user_name, phone_number FROM phonebook"
        filters = []
        params = []

        if name_pattern:
            filters.append("user_name ILIKE %s") #ILIKE used for case-insensitive 
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

#Function to delete a contact 
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

#Function to print the menu
def print_menu():
    print("\n===== Phonebook Menu =====")
    print("1. Add contact (manually)")
    print("2. Load contacts from CSV (contacts.csv)")
    print("3. Show/Search contacts")
    print("4. Update contact")
    print("5. Delete contact")
    print("0. Exit")
    print("==========================")

#  MAIN BLOCK
try:
    # Establish connection
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    print("Successfully connected to the database!")
    conn.autocommit = True
    cursor = conn.cursor()
    print("Cursor created.")

    # Create table if it does not exist
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

    # Main interactive loop 
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
        elif choice == '0':
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL or performing operations: {e}")

finally:
    #Closing cursor and connection at the very end 
    print("\nDatabase work is finishing.")
    if cursor is not None:
        cursor.close()
        print("Cursor closed.")
    if conn is not None:
        conn.close()
        print("PostgreSQL connection closed.")
