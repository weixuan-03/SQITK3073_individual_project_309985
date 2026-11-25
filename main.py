"""
main.py - Malaysian Tax Input Program (YA 2026)
Main program logic: registration, login, tax calculation, saving and viewing records.
"""

from functions import (
    register_user,
    verify_user,
    get_valid_float,
    get_test_case_id,
    build_tax_record,
    display_tax_summary,
    save_tax_records,
    retrieve_tax_records,
)


def tax_menu(current_user):
    """
    Menu for a logged-in user: calculate tax, view saved records or logout.
    """
    while True:
        print(f"\n=== Malaysian Tax Input Program (Logged in as: {current_user}) ===")
        print("1. Calculate Personal Income Tax")
        print("2. View Saved Tax Records")
        print("3. Logout")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            print("\n--- Enter Tax Details (YA 2026) ---")
            test_case_id = get_test_case_id("Enter Test Case ID (T01-T05, or N/A): ")
            annual_income = get_valid_float("Enter Annual Income (RM): ")
            tax_relief = get_valid_float("Enter Total Eligible Tax Relief (RM): ")

            # Calculate tax, then store results in a Python list and a dictionary
            record_list, record_dict = build_tax_record(
                user_id=current_user,
                test_case_id=test_case_id,
                annual_income=annual_income,
                tax_relief=tax_relief,
            )

            # Display the tax summary, the list and the dictionary
            display_tax_summary(record_dict)
            print(f"\nPython List      : {record_list}")
            print(f"Python Dictionary: {record_dict}")

            # Ask whether to save the record to CSV
            save_choice = input("\nSave record to CSV? (y/n): ").strip().lower()
            if save_choice == "y":
                saved_df = save_tax_records([record_dict])
                if saved_df is not None:
                    print("\n--- Pandas DataFrame Saved to tax_records.csv ---")
                    print(saved_df.to_string(index=False))
            else:
                print("Record not saved.")

        elif choice == "2":
            retrieve_tax_records()

        elif choice == "3":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def main():
    """
    Main menu for registration, login and exit.
    """
    while True:
        print("\n=== Welcome to Malaysian Tax Input Program ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            user_id = input("Enter new User ID: ")
            ic_number = input("Enter 12-digit IC Number (without dashes): ")
            success, message = register_user(user_id, ic_number)
            print(message)

        elif choice == "2":
            user_id = input("Enter User ID: ")
            password = input("Enter Password (last 4 digits of IC): ")
            success, message = verify_user(user_id, password)
            print(message)
            if success:
                tax_menu(user_id.strip())

        elif choice == "3":
            print("Thank you for using the Malaysian Tax Input Program. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user. Goodbye!")