"""
functions.py - Malaysian Tax Input Program (YA 2026)
Contains all user-defined functions used by main.py.
"""

import os
import pandas as pd

# Constant filenames for persistent CSV storage
USERS_FILE = "users.csv"
TAX_RECORDS_FILE = "tax_records.csv"

# Column headers / dictionary keys used for tax_records.csv
TAX_RECORD_KEYS = [
    "User ID",
    "Test Case ID",
    "Year of Assessment",
    "Annual Income",
    "Total Tax Relief",
    "Chargeable Income",
    "Tax Before Rebate",
    "Tax Rebate",
    "Final Tax Payable",
]

VALID_TEST_CASES = ["T01", "T02", "T03", "T04", "T05"]


def load_users(filename=USERS_FILE):
    """
    Load registered users from users.csv into a pandas DataFrame.
    Returns an empty DataFrame if the file does not exist or is blank.
    """
    if not os.path.exists(filename):
        return pd.DataFrame(columns=["User ID", "IC Number"])
    try:
        # dtype=str preserves leading zeros in Malaysian IC numbers
        return pd.read_csv(filename, dtype=str)
    except (pd.errors.EmptyDataError, OSError):
        return pd.DataFrame(columns=["User ID", "IC Number"])


def validate_ic(ic_number):
    """
    Validate that the IC number consists of exactly 12 digits
    (no dashes, spaces or letters).
    """
    return ic_number.isdigit() and len(ic_number) == 12


def register_user(user_id, ic_number, filename=USERS_FILE):
    """
    Validate and register a new user, then append the details to users.csv.
    Data flow: List -> Dictionary -> pandas DataFrame -> CSV.
    Returns (success, message).
    """
    user_id = user_id.strip()
    ic_number = ic_number.strip()

    if not user_id:
        return False, "Error: User ID cannot be empty."
    if not validate_ic(ic_number):
        return False, "Error: Invalid IC number. Please enter exactly 12 digits (no dashes)."

    users_df = load_users(filename)
    if user_id in users_df["User ID"].values:
        return False, "Error: User ID already exists. Please choose another ID or log in."

    try:
        # Step 1: store user details in a Python list
        user_list = [user_id, ic_number]
        # Step 2: convert the list into a dictionary with meaningful keys
        user_dict = dict(zip(["User ID", "IC Number"], user_list))
        # Step 3: convert a list of dictionaries into a pandas DataFrame
        new_user_df = pd.DataFrame([user_dict])
        # Step 4: append to existing records and save to CSV
        updated_df = pd.concat([users_df, new_user_df], ignore_index=True)
        updated_df.to_csv(filename, index=False)

        return True, (
            f"Registration successful! User ID: {user_id}. "
            f"Your login password is the last 4 digits of your IC ({ic_number[-4:]})."
        )
    except OSError as error:
        return False, f"Error saving user data to CSV: {error}"


def verify_user(user_id, password, filename=USERS_FILE):
    """
    Authenticate a registered user using the User ID and the last 4 digits
    of the registered IC number as the password.
    Returns (success, message).
    """
    users_df = load_users(filename)
    if users_df.empty:
        return False, "No registered users found. Please register an account first."

    matched_user = users_df[users_df["User ID"] == user_id.strip()]
    if matched_user.empty:
        return False, "Login failed: User ID not found."

    stored_ic = str(matched_user.iloc[0]["IC Number"])
    if password.strip() == stored_ic[-4:]:
        return True, "Login successful! Welcome to the tax calculator."
    return False, "Login failed: Incorrect password (use the last 4 digits of your IC)."


def get_valid_float(prompt):
    """
    Repeatedly prompt until a valid, non-negative number is entered.
    Commas used as thousand separators are removed before conversion.
    """
    while True:
        raw_input = input(prompt).replace(",", "").strip()
        try:
            amount = float(raw_input)
            if amount < 0:
                print("Error: Amount cannot be negative. Please enter 0 or a positive number.")
            else:
                return amount
        except ValueError:
            print("Error: Invalid input. Please enter numbers only (e.g., 40000).")


def get_test_case_id(prompt):
    """
    Ask for a Test Case ID (T01 to T05) or N/A for a normal calculation.
    Repeats until a valid value is entered. Blank input is treated as N/A.
    """
    while True:
        value = input(prompt).strip().upper()
        if value in ("", "N/A", "NA"):
            return "N/A"
        if value in VALID_TEST_CASES:
            return value
        print("Error: Enter T01 to T05, or N/A for a normal calculation.")


def calculate_malaysian_tax(annual_income, tax_relief):
    """
    Calculate Malaysian resident individual income tax for YA 2026.

    Rules:
    1. Chargeable Income = max(0, Annual Income - Total Tax Relief)
    2. Progressive tax bands from 0% up to 30%
    3. RM400 individual rebate if Chargeable Income <= RM35,000
    4. Final Tax Payable = max(0, Tax Before Rebate - Tax Rebate)

    Returns (chargeable_income, tax_before_rebate, tax_rebate, final_tax_payable).
    """
    chargeable_income = max(0.0, annual_income - tax_relief)

    # (upper_limit, tax_rate) for each band
    tax_brackets = [
        (5000, 0.00),
        (20000, 0.01),
        (35000, 0.03),
        (50000, 0.06),
        (70000, 0.11),
        (100000, 0.19),
        (400000, 0.25),
        (600000, 0.26),
        (2000000, 0.28),
        (float("inf"), 0.30),
    ]

    tax_before_rebate = 0.0
    previous_limit = 0.0

    # Tax only the slice of income that falls inside each band
    for upper_limit, rate in tax_brackets:
        if chargeable_income > previous_limit:
            taxable_slice = min(chargeable_income, upper_limit) - previous_limit
            tax_before_rebate += taxable_slice * rate
            previous_limit = upper_limit
        else:
            break

    tax_rebate = 400.0 if chargeable_income <= 35000 else 0.0

    # Unused rebate is not refundable, so final tax cannot be negative
    final_tax_payable = max(0.0, tax_before_rebate - tax_rebate)

    return (
        round(chargeable_income, 2),
        round(tax_before_rebate, 2),
        round(tax_rebate, 2),
        round(final_tax_payable, 2),
    )


def build_tax_record(user_id, test_case_id, annual_income, tax_relief, year="YA 2026"):
    """
    Calculate tax and organise the results: Python list -> Python dictionary.
    Returns (record_list, record_dict).
    """
    chargeable, tax_before, rebate, final_tax = calculate_malaysian_tax(
        annual_income, tax_relief
    )

    record_list = [
        user_id,
        test_case_id,
        year,
        round(annual_income, 2),
        round(tax_relief, 2),
        chargeable,
        tax_before,
        rebate,
        final_tax,
    ]
    record_dict = dict(zip(TAX_RECORD_KEYS, record_list))
    return record_list, record_dict


def display_tax_summary(record_dict):
    """
    Display the tax calculation result with all amounts in RM (2 decimal places).
    """
    print("\n--- Tax Calculation Summary ---")
    print(f"User ID             : {record_dict['User ID']}")
    print(f"Test Case ID        : {record_dict['Test Case ID']}")
    print(f"Year of Assessment  : {record_dict['Year of Assessment']}")
    print(f"Annual Income       : RM {record_dict['Annual Income']:,.2f}")
    print(f"Total Tax Relief    : RM {record_dict['Total Tax Relief']:,.2f}")
    print(f"Chargeable Income   : RM {record_dict['Chargeable Income']:,.2f}")
    print(f"Tax Before Rebate   : RM {record_dict['Tax Before Rebate']:,.2f}")
    print(f"Tax Rebate          : RM {record_dict['Tax Rebate']:,.2f}")
    print(f"Final Tax Payable   : RM {record_dict['Final Tax Payable']:,.2f}")


def save_tax_records(records_dict_list, filename=TAX_RECORDS_FILE):
    """
    Convert a list of tax record dictionaries into a pandas DataFrame and
    append it to tax_records.csv while preserving existing records.
    Returns the new DataFrame, or None if saving failed.
    """
    new_df = pd.DataFrame(records_dict_list)

    try:
        if os.path.exists(filename):
            try:
                # keep_default_na=False keeps the text "N/A" instead of turning it into NaN
                existing_df = pd.read_csv(filename, keep_default_na=False)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            except pd.errors.EmptyDataError:
                combined_df = new_df
        else:
            combined_df = new_df

        combined_df.to_csv(filename, index=False)
        return new_df
    except OSError as error:
        print(f"Error saving tax record to {filename}: {error}")
        return None


def retrieve_tax_records(filename=TAX_RECORDS_FILE):
    """
    Read tax_records.csv with pandas and display all saved records.
    Shows 'No records found' if the file is missing or empty.
    """
    if not os.path.exists(filename):
        print("\nNo records found.")
        return None

    try:
        records_df = pd.read_csv(filename, keep_default_na=False)
    except (pd.errors.EmptyDataError, OSError):
        print("\nNo records found.")
        return None

    if records_df.empty:
        print("\nNo records found.")
        return None

    print("\n--- Saved Tax Records ---")
    print(records_df.to_string(index=False))
    return records_df
def display_tax_summary(record_dict):
    """
    Display a formatted summary of the tax calculation in RM with 2 decimal places.
    """
    print("\n--- Tax Calculation Summary (YA 2026) ---")
    print(f"User ID            : {record_dict['User ID']}")
    print(f"Year of Assessment : {record_dict['Year of Assessment']}")
    print(f"Annual Income      : RM {record_dict['Annual Income']:,.2f}")
    print(f"Total Tax Relief   : RM {record_dict['Total Tax Relief']:,.2f}")
    print(f"Chargeable Income  : RM {record_dict['Chargeable Income']:,.2f}")
    print(f"Tax Before Rebate  : RM {record_dict['Tax Before Rebate']:,.2f}")
    print(f"Tax Rebate         : RM {record_dict['Tax Rebate']:,.2f}")
    print(f"Final Tax Payable  : RM {record_dict['Final Tax Payable']:,.2f}")
    print("-----------------------------------------")


def retrieve_tax_records(filename=TAX_RECORDS_FILE):
    """
    Read and display all previously saved tax records from tax_records.csv using pandas.
    Handles missing or empty files gracefully.
    """
    if not os.path.exists(filename):
        print("\nNo saved tax records found yet. Please calculate income tax first.")
        return None

    try:
        df = pd.read_csv(filename)
        if df.empty:
            print("\nThe tax records file is currently empty.")
            return None

        # Configure pandas display so all columns appear neatly in one view
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 1000)

        print("\n=== Previously Saved Tax Records ===")
        print(df.to_string(index=False))
        return df
    except (pd.errors.EmptyDataError, OSError) as error:
        print(f"\nUnable to read tax records: {error}")
        return None
