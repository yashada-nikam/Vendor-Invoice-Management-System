import streamlit as st
import mysql.connector
import streamlit_authenticator as stauth


#Database Connection:
config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
  'database': 'vendorinvoicemgmt',
  'raise_on_warnings': True,
}

#Vendor logins
v_names = ['Auto Parts','Simple Machineries', 'Bearing', 'Security device', 'Black and Decker', 'Dyson Boiler', 'Stanley systems', 'Staples', 'Billi John', 'AMD']
v_usernames = ['AParts','SMachineries', 'Bearing', 'Sdevice', 'BDecker', 'DBoiler', 'SSystems', 'Staples', 'BJohn', 'AMD']
v_passwords = ['test','test', 'test','test','test', 'test', 'test', 'test', 'test', 'test']

#Purchaser Logins
names = ['Courtney Payton','Yashada Nikam', 'Sadaramana Chowdam', 'Olga Scriver', 'Deveshwari Pujari']
usernames = ['CPayton','YNikam', 'SChowdam', 'OScrivner', 'DPujari']
passwords = ['test','test', 'test','test']

def Vendor():
    st.header("Vendor Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check if the entered username and password match any registered user
        if username in v_usernames:
            user_index = v_usernames.index(username)
            if password == v_passwords[user_index]:
                st.success("Login successful!")
                st.write(f"Welcome {v_names[user_index]}!")
                vendor_image = "/Users/payto/Documents/Courses/ADT/Final_Project/Phase3/Streamlit_tast/Vendor_Icon.png"
                st.image(vendor_image, use_column_width=False, width=100)
                v_option = st.radio("View or create invoices?", ("View invoices", "Enter Invoices"))
                if v_option == "View invoices":
                    st.title("View Current Invoices")
                    invs = get_invoices()
                    if invs:
                        st.table(invs)
                    else:
                        st.warning("No current invoices.")
               # else:
                    st.title("Invoice Entry")
                    invoice_num = st.number_input("Invoice Number: ")
                    item_num = st.number_input("Item Number: ")
                    material_num = st.number_input("Material #: ")
                    material_desc = st.text_input("Material descr:")
                    quantity = st.number_input("Quantity: ")
                    UOM = st.text_input("Unit of Measurement: ")
                    unitPrice = st.number_input("Unit Price: ")
                    NetPrice = st.number_input("Net Price: ")
                    tax = st.number_input("Tax: ")
                    totalPrice = st.number_input("Total Price: ")
                    currency = st.text_input("Currency: ")
                    poNumber = st.number_input("PO Number: ")
                    poItem = st.text_input("PO Item: ")
                    
                    if st.button("Submit Invoice"):
                        insert_invoice(invoice_num, item_num, material_num, material_desc, quantity, UOM, unitPrice, NetPrice, tax, totalPrice, currency, poNumber, poItem)
                        st.success("Invoice Successfully Entered expect payment in 7-10 business days!") 
            else:
                st.error("Incorrect password. Please try again.")
        else:
            st.error("Username not found. Please try again.")

def purchaser():
    st.header("Purchaser Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check if the entered username and password match any registered user
        if username in usernames:
            user_index = usernames.index(username)
            if password == passwords[user_index]:
                st.success("Login successful!")
                st.write(f"Welcome {names[user_index]}!")
                emp_image = "/Users/payto/Documents/Courses/ADT/Final_Project/Phase3/Streamlit_tast/emp_icon.png"
                st.image(emp_image, use_column_width=False, width=100)

                
                st.title("View Current Invoices")
                invs = get_invoices()
                st.table(invs)
                
                p_invs = get_invoices_by_approvers()
                st.title("Total Dollar Amount approved by Employee: ")
                st.table(p_invs)
                
                dist = distribution()
                st.title("Distribution of invoices and their approval levels: ")
                st.table(dist)
                
                range_info = ranges()
                st.title("Count of invoices by their approval levels: ")
                st.table(range_info)
                    
            else:
                st.error("Incorrect password. Please try again.")
        else:
            st.error("Username not found. Please try again.")


def insert_invoice(invoice_num, item_num, material_num, material_desc, quantity, UOM, unitPrice, NetPrice, tax, totalPrice, currency, poNumber, poItem):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "INSERT INTO vendorinvoicemgmt.vendorinvoiceitm(invoice_num, item_num, material_num, material_desc, quantity, UOM, unitPrice, NetPrice, tax, totalPrice, currency, poNumber, poItem) VALUES (%s, %s, %s)"
    data = (invoice_num, item_num, material_num, material_desc, quantity, UOM, unitPrice, NetPrice, tax, totalPrice, currency, poNumber, poItem)
    cursor.execute(query, data)
    connection.commit()
    connection.close()
    
#Getting all invoices    
def get_invoices():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vendorinvoicemgmt.vendorinvoiceitm")
    invs = cursor.fetchall()
    connection.close()
    return invs

#Getting invoices totals by employees for what has already been approved
def get_invoices_by_approvers():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("SELECT e.employee_id, e.first_name, e.last_name, SUM(h.totalprice) AS total_amount FROM employeemaster e JOIN vendorinvoicehdr h ON e.employee_id = h.approver_id GROUP BY e.employee_id, e.first_name, e.last_name")
    p_invs = cursor.fetchall()
    connection.close
    return p_invs


def distribution():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("""
    SELECT invoice_num, totalprice,
      CASE
        WHEN totalprice <= 1000 THEN 'Low Approval'
        WHEN totalprice > 1000 AND totalprice <= 5000 THEN 'Medium Approval'
        WHEN totalprice > 5000 AND totalprice <= 10000 THEN 'High Approval'
      ELSE 'Very High Approval'
     END AS approval_range
   FROM vendorinvoicehdr""")
    dist = cursor.fetchall()
    connection.close
    return dist

def ranges():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("""
    SELECT 
    CASE
        WHEN totalprice BETWEEN 0 AND 1000 THEN '0 - 1000'
        WHEN totalprice BETWEEN 1001 AND 5000 THEN '1001 - 5000'
        WHEN totalprice BETWEEN 5001 AND 10000 THEN '5001 - 10000'
        ELSE '10001+'
    END AS approval_range,
    COUNT(*) AS invoice_count
FROM 
    vendorinvoicehdr
GROUP BY 
    approval_range;
""")
    ranges = cursor.fetchall()
    connection.close
    return ranges

def main():
    header = st.container()
    with header:
        st.title("Vendor Invoice Management")
    login_buttons = st.sidebar.radio("Select user",["Vendor", "Purchaser"])
    main_image = "/Users/payto/Documents/Courses/ADT/Final_Project/Phase3/Streamlit_tast/main_icon.jpg"
    st.image(main_image,  width=200, use_column_width=False)
       
    if login_buttons == "Vendor":
        # Login page
        Vendor()
    elif login_buttons == "Purchaser":
        purchaser()
    else:
        st.warning("Please select user: ")
        
if __name__ == "__main__":
    main()
    



