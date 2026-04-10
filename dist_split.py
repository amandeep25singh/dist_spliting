import streamlit as st
import csv
import io
import re

st.set_page_config(page_title="NIC Code Splitter", layout="wide")

st.title("📊 NIC Code Splitter Tool")

st.write("Upload a CSV file to split NIC codes and extract descriptions.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

def process_csv(file):
    output_rows = []

    file.seek(0)
    decoded = file.read().decode("utf-8").splitlines()
    reader = csv.reader(decoded)

    header = next(reader)
    header.insert(9, "NIC_Description")
    output_rows.append(header)

    for row in reader:
        if len(row) < 9 or not row[8]:
            row.insert(9, "")
            output_rows.append(row)
            continue

        activities = row[8]

        # Handle multiple NIC blocks
        nic_entries = activities.replace("{", "").split("}")

        for entry in nic_entries:
            entry = entry.strip()

            code_match = re.search(r'"(\d{5})"', entry)
            desc_match = re.search(r'"Description"\s*:\s*"([^"]+)"', entry)

            if code_match and desc_match:
                nic_code = code_match.group(1)
                description = desc_match.group(1)

                new_row = row.copy()
                new_row[8] = nic_code
                new_row.insert(9, description)
                output_rows.append(new_row)

    return output_rows


if uploaded_file is not None:
    st.success("File uploaded successfully ✅")

    output_data = process_csv(uploaded_file)

    # Convert to CSV for download
    output_buffer = io.StringIO()
    writer = csv.writer(output_buffer)
    writer.writerows(output_data)

    csv_data = output_buffer.getvalue()

    st.download_button(
        label="📥 Download Processed CSV",
        data=csv_data,
        file_name="NIC_Split_Output.csv",
        mime="text/csv"
    )

    st.write("### Preview (First 10 rows)")
    st.dataframe(output_data[:10])