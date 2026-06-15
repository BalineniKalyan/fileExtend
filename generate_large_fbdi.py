import pandas as pd
import csv
import os

# =====================================================
# CONFIGURATION
# =====================================================

INPUT_FILE = "GL Import test large data sample file.csv"
OUTPUT_FILE = "GL_Import_950MB_Group15062026.csv"

TARGET_SIZE_MB = 950
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024

GROUP_ID = "15062026"
BATCH_NAME = "GL_LOAD_15062026"

# =====================================================
# COLUMN NAMES FROM YOUR FILE
# =====================================================

DEBIT_COLUMN = "Entered Debit Amount"
CREDIT_COLUMN = "Entered Credit Amount"

CONVERTED_DEBIT_COLUMN = "Converted Debit Amount"
CONVERTED_CREDIT_COLUMN = "Converted Credit Amount"

GROUP_COLUMN = "Interface Group Identifier"

JOURNAL_NAME_COLUMN = "REFERENCE4 (Journal Entry Name)"
BATCH_NAME_COLUMN = "REFERENCE1 (Batch Name)"

# =====================================================
# READ SOURCE FILE
# =====================================================

print("Reading source file...")

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    keep_default_na=False
)

print(f"Source Rows: {len(df)}")

columns = list(df.columns)

required_columns = [
    DEBIT_COLUMN,
    CREDIT_COLUMN,
    GROUP_COLUMN,
    JOURNAL_NAME_COLUMN,
    BATCH_NAME_COLUMN
]

for col in required_columns:
    if col not in columns:
        raise Exception(f"Required column not found: {col}")

# =====================================================
# GENERATE OUTPUT
# =====================================================

print("Generating Fusion-compatible file...")

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as outfile:

    writer = csv.writer(outfile)

    # Write header
    writer.writerow(columns)

    source_row_index = 0
    journal_number = 1
    amount = 1000

    while True:

        if journal_number % 1000 == 0:

            current_size = os.path.getsize(
                OUTPUT_FILE
            )

            current_mb = round(
                current_size / (1024 * 1024),
                2
            )

            print(
                f"Current Size: {current_mb} MB"
            )

            if current_size >= TARGET_SIZE_BYTES:
                break

        base_row = (
            df.iloc[source_row_index % len(df)]
            .copy()
            .to_dict()
        )

        journal_name = f"LOAD_{journal_number}"

        # ====================================
        # DEBIT LINE
        # ====================================

        debit_row = base_row.copy()

        debit_row[GROUP_COLUMN] = GROUP_ID
        debit_row[BATCH_NAME_COLUMN] = BATCH_NAME
        debit_row[JOURNAL_NAME_COLUMN] = journal_name

        debit_row[DEBIT_COLUMN] = str(amount)
        debit_row[CREDIT_COLUMN] = ""

        if CONVERTED_DEBIT_COLUMN in columns:
            debit_row[CONVERTED_DEBIT_COLUMN] = ""

        if CONVERTED_CREDIT_COLUMN in columns:
            debit_row[CONVERTED_CREDIT_COLUMN] = ""

        writer.writerow(
            [debit_row.get(col, "") for col in columns]
        )

        # ====================================
        # CREDIT LINE
        # ====================================

        credit_row = base_row.copy()

        credit_row[GROUP_COLUMN] = GROUP_ID
        credit_row[BATCH_NAME_COLUMN] = BATCH_NAME
        credit_row[JOURNAL_NAME_COLUMN] = journal_name

        credit_row[DEBIT_COLUMN] = ""
        credit_row[CREDIT_COLUMN] = str(amount)

        if CONVERTED_DEBIT_COLUMN in columns:
            credit_row[CONVERTED_DEBIT_COLUMN] = ""

        if CONVERTED_CREDIT_COLUMN in columns:
            credit_row[CONVERTED_CREDIT_COLUMN] = ""

        writer.writerow(
            [credit_row.get(col, "") for col in columns]
        )

        amount += 100

        if amount > 999999:
            amount = 1000

        source_row_index += 1
        journal_number += 1

# =====================================================
# FINISH
# =====================================================

final_size = round(
    os.path.getsize(OUTPUT_FILE)
    / (1024 * 1024),
    2
)

print("\n====================================")
print("FILE GENERATED SUCCESSFULLY")
print("====================================")
print("Output File :", OUTPUT_FILE)
print("Final Size  :", final_size, "MB")
print("Interface Group Identifier :", GROUP_ID)
print("Batch Name :", BATCH_NAME)
print("====================================")