from datetime import date, datetime
import csv
from io import StringIO
import streamlit as st
import plotly.express as px

from streamlit.runtime.uploaded_file_manager import UploadedFile

# Wells Fargo Dictionary key
headers = {0: "Date", 1: "Amount", 4:"Transaction Name"}

credits: list[dict] = []
debits: list[dict] = []
zeros: list[dict] = []

uploaded_file_names_and_total_credits_map: dict[str, int] = {}

start_date: date = date(1900, 1, 1)
end_date: date = date.today()

def process_csv(uploaded_file: UploadedFile):
    csv_name: str = uploaded_file.name

    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    parsed_csv = csv.reader(stringio)
    
    local_credit_total = 0
    for row in parsed_csv:
        curr_row_dict = {}
        for index in headers.keys():
            curr_row_dict[headers[index]] = row[index]
        
        curr_row_dict["Source"] = csv_name

        if 'Amount' not in curr_row_dict:
            raise Exception("no amount present, investigate !!")

        if curr_row_dict['Amount'] == 'Amount':
            continue

        if float(curr_row_dict['Amount']) < 0:
            local_credit_total += float(curr_row_dict['Amount'])
            credits.append(curr_row_dict)
        elif float(curr_row_dict['Amount']) > 0:
            debits.append(curr_row_dict)
        else:
            zeros.append(curr_row_dict)

    if csv_name not in uploaded_file_names_and_total_credits_map:
        uploaded_file_names_and_total_credits_map[csv_name] = abs(local_credit_total)

def render_credits():
    total = 0
    valid_credits: list[dict] = []

    for credit in credits:
        credit_date = datetime.strptime(credit['Date'], "%m/%d/%Y").date()

        if credit_date >= start_date and credit_date <= end_date:
            valid_credits.append(credit)
            total += abs(float(credit['Amount']))
        

    st.header("Total Spend Graph")

    labels = [f"{tx.get("Transaction Name")} {tx['Date']}" for tx in valid_credits]
    values = [abs(float(tx["Amount"])) for tx in valid_credits]

    fig = px.pie(
        names=labels,
        values=values,
        title="Individual Credit Transactions"
    )

    st.plotly_chart(fig)

    # Summary Graph

    st.subheader("Summary")
    summary_data = {"Total Spend": total}
    for uploaded_file_name in uploaded_file_names_and_total_credits_map:
        summary_data[uploaded_file_name] = uploaded_file_names_and_total_credits_map[uploaded_file_name]
    st.dataframe(data=summary_data)


def main():
    st.set_page_config(page_title="Jeff's Finance Tracker", page_icon="💰")
    st.title("Card Spend Tracker")
    st.markdown("Import CSV in the format ```Date | Amount | ANY | ANY | Transaction Name```")
    st.text("The above is the default export format for Wells Fargo cards (including Bilt card).")
    # input
    date_range = st.date_input(
        "Select date range",
        value=(date(2025, 1, 1), date.today()),
        min_value=date(2000, 1, 1),
        max_value=date.today()
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        global start_date, end_date
        start_date = date_range[0]
        end_date = date_range[1]

    uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            process_csv(uploaded_file=uploaded_file)

    if len(uploaded_files) == 0:
        st.write("Upload a CSV to start")
        return
    
    st.write(f"Analyzing expenses from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")
    render_credits()

    
if __name__ == "__main__":
    main()