import psycopg2
import os  # Might be needed for environment variables (safer for password)

#  Database connection parameters 
DB_NAME = "lab10_db"
DB_USER = "postgres"
DB_PASS = "gogetthem"
DB_HOST = "localhost"
DB_PORT = "5432"

#  Global variables for connection and cursor
conn = None
cursor = None

#  DB initialization function (connect and create tables) 
def initialize_db():
    """
    Establishes connection to the DB, creates cursor and tables if they don't exist.
    Returns a tuple (connection, cursor) or (None, None) in case of error.
    """
    global conn, cursor  # Use global variables
    try:
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        conn.autocommit = True  # Enable auto-commit
        cursor = conn.cursor()
        print("(DB Module) Successfully connected to the database.")

        #  Create users table 
        create_users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE
        );
        '''
        cursor.execute(create_users_table)

        #  Create user_scores table 
        create_scores_table = '''
        CREATE TABLE IF NOT EXISTS user_scores (
            score_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(create_scores_table)

        print("(DB Module) Tables 'users' and 'user_scores' are ready.")
        return conn, cursor  # Return active connection and cursor

    except psycopg2.Error as e:
        print(f"(DB Module) Error initializing the database: {e}")
        # Close resources in case of initialization error
        if cursor: cursor.close()
        if conn: conn.close()
        conn, cursor = None, None  # Reset global variables
        return None, None

#  Function to close the connection 
def close_db():
    """Closes the cursor and the database connection."""
    global conn, cursor
    print("\n(DB Module) Closing the database connection.")
    if cursor is not None:
        try:
            cursor.close()
            print("(DB Module) Cursor closed.")
        except psycopg2.Error as e:
            print(f"(DB Module) Error closing cursor: {e}")
        finally:
            cursor = None  # Ensure the reference is reset
    if conn is not None:
        try:
            conn.close()
            print("(DB Module) Connection closed.")
        except psycopg2.Error as e:
            print(f"(DB Module) Error closing connection: {e}")
        finally:
            conn = None  # Ensure the reference is reset

#  Function to get user ID and their last level 
def get_or_create_user(cur, username):
    """
    Checks if the user exists in the DB. If yes, returns their ID and last level.
    If not, creates the user, returns their ID and level 1.
    Returns a tuple (user_id, current_level) or (None, 1) in case of error.
    """
    if not cur:
        print("(DB Module) Error: Database cursor not initialized for get_or_create_user.")
        return None, 1
    try:
        # 1. Check if user exists
        find_user_query = "SELECT user_id FROM users WHERE username = %s"
        cur.execute(find_user_query, (username,))
        user_result = cur.fetchone()

        if user_result:
            # User found
            user_id = user_result[0]

            # 2. Find last saved level for this user
            find_level_query = """
                SELECT level FROM user_scores
                WHERE user_id = %s
                ORDER BY saved_at DESC
                LIMIT 1
            """
            cur.execute(find_level_query, (user_id,))
            level_result = cur.fetchone()

            if level_result:
                current_level = level_result[0]
                return user_id, current_level
            else:
                return user_id, 1
        else:
            # User not found, create new
            insert_user_query = "INSERT INTO users (username) VALUES (%s) RETURNING user_id"
            cur.execute(insert_user_query, (username,))
            user_id = cur.fetchone()[0]
            print(f"(DB Module) New user '{username}' created, ID: {user_id}.")
            return user_id, 1  # New user starts at level 1

    except psycopg2.Error as e:
        print(f"(DB Module) Error working with user '{username}': {e}")
        return None, 1  # In case of error, return None and level 1
    except Exception as e:  # Catch other possible errors
        print(f"(DB Module) Unexpected error in get_or_create_user: {e}")
        return None, 1

#  Function to save current score and level for the user 
def save_game_state(cur, user_id, current_score, current_level):
    """Saves the user's score and level to the user_scores table."""
    if not cur:
        print("(DB Module) Error: Database cursor not initialized for save_game_state.")
        return False
    if user_id is None:
        print("(DB Module) Error: Cannot save state, user_id is not defined.")
        return False
    try:
        insert_score_query = """
            INSERT INTO user_scores (user_id, score, level)
            VALUES (%s, %s, %s)
        """
        cur.execute(insert_score_query, (user_id, current_score, current_level))
        print(f"(DB Module) Game state saved: UserID={user_id}, Score={current_score}, Level={current_level}")
        return True
    except psycopg2.Error as e:
        print(f"(DB Module) Error saving game state for UserID={user_id}: {e}")
        return False
    except Exception as e:  # Catch other possible errors
        print(f"(DB Module) Unexpected error in save_game_state: {e}")
        return False

#  Test block (runs if you execute snake_game_db.py directly) 
if __name__ == "__main__":
    print("Testing snake_game_db module...")

    # Initialize DB
    test_conn, test_cursor = initialize_db()

    if test_conn and test_cursor:
        print("\n--- Test 1: Get/Create User ---")
        test_username = "TestPlayerDB"
        user_id, start_level = get_or_create_user(test_cursor, test_username)
        print(f"Result for {test_username}: user_id={user_id}, start_level={start_level}")

        test_username_2 = "AnotherPlayerDB"
        user_id_2, start_level_2 = get_or_create_user(test_cursor, test_username_2)
        print(f"Result for {test_username_2}: user_id={user_id_2}, start_level={start_level_2}")

        # Repeat call for first player
        user_id_repeat, start_level_repeat = get_or_create_user(test_cursor, test_username)
        print(f"Repeat result for {test_username}: user_id={user_id_repeat}, start_level={start_level_repeat}")

        print("\n--- Test 2: Save Game State ---")
        if user_id is not None:
            save_game_state(test_cursor, user_id, 155, 3)  # Save score for TestPlayerDB
            save_game_state(test_cursor, user_id, 255, 4)  # Again for TestPlayerDB
        if user_id_2 is not None:
            save_game_state(test_cursor, user_id_2, 55, 1)  # Save score for AnotherPlayerDB

        # Check level after saving
        user_id_after_save, level_after_save = get_or_create_user(test_cursor, test_username)
        print(f"Level for {test_username} after saves: {level_after_save}")  # Should be 4

        # Close connection after tests
        close_db()
    else:
        print("Failed to initialize database for testing.")
