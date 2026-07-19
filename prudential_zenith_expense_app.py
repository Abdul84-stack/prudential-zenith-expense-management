# app.py - Modified version without ReportLab
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import hashlib
import json
import os
import io
import base64
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_department' not in st.session_state:
    st.session_state.user_department = None
if 'requests' not in st.session_state:
    st.session_state.requests = []
if 'vendors' not in st.session_state:
    st.session_state.vendors = []
if 'users' not in st.session_state:
    st.session_state.users = {}

# Default users
DEFAULT_USERS = {
    'head_admin': {'password': '123456', 'role': 'Head of Admin', 'department': 'Administration', 'admin_right': True},
    'head_it': {'password': '123456', 'role': 'Head of IT', 'department': 'IT', 'admin_right': True},
    'cfo_ed': {'password': '123456', 'role': 'CFO/ED', 'department': 'Finance & Investment', 'admin_right': False},
    'cco': {'password': '123456', 'role': 'CCO', 'department': 'Corporate Sales', 'admin_right': False},
    'csr': {'password': '123456', 'role': 'Chief Risk Officer', 'department': 'Internal Control & Risk', 'admin_right': False},
    'co': {'password': '123456', 'role': 'Chief Compliance Officer', 'department': 'Legal and Compliance', 'admin_right': False},
    'coo': {'password': '123456', 'role': 'COO', 'department': 'Corporate and Business Support', 'admin_right': False},
    'head_finance': {'password': '123456', 'role': 'Head of Finance', 'department': 'Finance & Investment', 'admin_right': False},
    'head_investment': {'password': '123456', 'role': 'Head of Investment', 'department': 'Finance & Investment', 'admin_right': False},
    'head_compliance': {'password': '123456', 'role': 'Head of Compliance', 'department': 'Legal and Compliance', 'admin_right': False},
    'head_internal_control': {'password': '123456', 'role': 'Head of Internal Control', 'department': 'Internal Control & Risk', 'admin_right': False},
}

# Expense lines budget data
EXPENSE_BUDGET = {
    '430106 WEEKEND WORK ALLOWANCE': 3042,
    '430608 PRINTING & STATIONERY': 29849,
    '430609 ENTERTAINMENT EXPS': 28888,
    '430610 OFFICE CONSUMABLES/GENERAL RUNNING EXPS': 55359,
    '430612 COMMUNICATION /TELEPHONE EXPS': 20172,
    '430657 CLEANING EXPENSE': 24536,
    '430658 CIIN PICNIC': 13338,
    '430619 REPAIRS AND MAINTENANCE-MOTOR VEHICLE': 72512,
    '430620 VEHICLE RUNNING EXPENSES': 11443,
    '430624 DIESEL AND FUELING': 254972,
    '430625 POSTAGES': 25556,
    '430626 NEWSPAPERS AND DAILIES': 1592,
    '430631 INSURANCE COST': 105237,
    '430633 SERVICE CHARGE': 82242,
    '430644 REPAIRS AND MAINTENANCE-FURNITURE': 3730,
    '430645 REPAIRS AND MAINTENANCE-EQUIPMENT': 17562,
    '430647 BID EXPENSE': 739,
    '430648 LATE NIGHT ALLOWANCE': 624,
    '430663 RENT': 222164,
    '430611 TRANSPORT & TRAVELLING': 119794,
    '430629 HOTEL ACCOMMODATION': 100070,
    'NEW GL DRIVERS SALARY': 150000,
}

# Vendor data (mock)
VENDOR_DATA = {
    'Vendor A': {'account': '1234567890', 'bank': 'First Bank', 'tin': '12345678-0001', 'contact': 'John Doe'},
    'Vendor B': {'account': '0987654321', 'bank': 'GTBank', 'tin': '87654321-0002', 'contact': 'Jane Smith'},
    'Vendor C': {'account': '1122334455', 'bank': 'Access Bank', 'tin': '11223344-0003', 'contact': 'Bob Johnson'},
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    if username in DEFAULT_USERS:
        if DEFAULT_USERS[username]['password'] == password:
            return True
    return False

def get_user_data(username):
    if username in DEFAULT_USERS:
        return DEFAULT_USERS[username]
    return None

def generate_html_report(request_data):
    """Generate an HTML report instead of PDF"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #1E88E5; color: white; padding: 20px; text-align: center; }}
            .content {{ margin: 20px 0; }}
            .field {{ margin: 10px 0; }}
            .label {{ font-weight: bold; display: inline-block; width: 150px; }}
            .status-approved {{ color: green; font-weight: bold; }}
            .status-pending {{ color: orange; font-weight: bold; }}
            .status-rejected {{ color: red; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #1E88E5; color: white; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Prudential Zenith Life Insurance</h1>
            <h2>Expense Requisition Report</h2>
        </div>
        <div class="content">
            <div class="field"><span class="label">Request ID:</span> {request_data.get('id', 'N/A')}</div>
            <div class="field"><span class="label">Request Type:</span> {request_data.get('request_type', 'N/A')}</div>
            <div class="field"><span class="label">Expense Line:</span> {request_data.get('expense_line', 'N/A')}</div>
            <div class="field"><span class="label">Total Amount:</span> NGN {request_data.get('total_amount', 0):,.2f}</div>
            <div class="field"><span class="label">VAT (7.5%):</span> NGN {request_data.get('vat', 0):,.2f}</div>
            <div class="field"><span class="label">WHT:</span> NGN {request_data.get('wht', 0):,.2f}</div>
            <div class="field"><span class="label">Net Amount:</span> NGN {request_data.get('net_amount', 0):,.2f}</div>
            <div class="field"><span class="label">Vendor:</span> {request_data.get('vendor', 'N/A')}</div>
            <div class="field"><span class="label">Department:</span> {request_data.get('department', 'N/A')}</div>
            <div class="field"><span class="label">Status:</span> <span class="status-{request_data.get('status', '').lower()}">{request_data.get('status', 'N/A')}</span></div>
            <div class="field"><span class="label">Requested By:</span> {request_data.get('requested_by', 'N/A')}</div>
            <div class="field"><span class="label">Date:</span> {request_data.get('date', 'N/A')}</div>
            <div class="field"><span class="label">Justification:</span> {request_data.get('justification', 'N/A')}</div>
            
            <h3>Approval Chain</h3>
            <table>
                <tr>
                    <th>Level</th>
                    <th>Approver</th>
                    <th>Status</th>
                    <th>Date</th>
                </tr>
    """
    
    for approval in request_data.get('approvals', []):
        status_color = 'green' if approval['status'] == 'Approved' else 'red' if approval['status'] == 'Rejected' else 'orange'
        html += f"""
                <tr>
                    <td>{approval.get('level', '') + 1}</td>
                    <td>{approval.get('approver', '')}</td>
                    <td style="color: {status_color};">{approval.get('status', 'Pending')}</td>
                    <td>{approval.get('date', '')}</td>
                </tr>
        """
    
    html += f"""
            </table>
        </div>
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>&copy; 2024 Prudential Zenith Life Insurance. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    return html

def login_page():
    st.markdown("""
        <style>
        .main { padding: 0; }
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .login-container h1 { text-align: center; color: #333; margin-bottom: 30px; }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Prudential Zenith</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #666;'>Expense Management</h2>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True):
            if authenticate_user(username, password):
                user_data = get_user_data(username)
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = user_data['role']
                st.session_state.user_department = user_data['department']
                st.session_state.admin_right = user_data.get('admin_right', False)
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.markdown("</div>", unsafe_allow_html=True)

def register_page():
    st.markdown("""
        <style>
        .register-container {
            max-width: 600px;
            margin: 50px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Create Account</h1>", unsafe_allow_html=True)
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            grade = st.selectbox("Grade", ["MD", "ED", "GM", "DGM", "AGM", "PM", "SM", "M", "DM", "AM", "Officer", "EA"])
            department = st.selectbox("Department", [
                "Administration", "Finance & Investment", "Bancassurance", "Corporate Sales", 
                "Agencies", "Actuary", "Legal and Compliance", "Internal Audit", 
                "Internal Control & Risk", "Corporate and Business Support", "Agencies Support", 
                "Claims and Underwriting", "Customer Service", "Strategy and Execution", "IT",
                "Telesales", "HR"
            ])
            role = st.selectbox("Role", [
                "CFO/ED", "COO", "CAO", "CCO", "Chief Risk Officer", "Chief Compliance Officer",
                "Head of Investment", "National Sales Manager", "Head Customer Service", 
                "Head of Admin", "Head of IT", "Head of Actuary", "Head of Commercial Support",
                "Head of Agencies Support", "Head Strategy and Operations", "Head Corporate Sales",
                "Head of HR", "employee", "Head of Compliance", "Head of Internal Audit",
                "Head of Internal Control"
            ])
        
        with col2:
            dob = st.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date(2005, 12, 31))
            marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])
            nationality = st.text_input("Nationality")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            bank_details = st.text_area("Bank Details")
            profile_picture = st.file_uploader("Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif username in DEFAULT_USERS or username in st.session_state.users:
                st.error("Username already exists!")
            else:
                st.session_state.users[username] = {
                    'full_name': full_name,
                    'password': hash_password(password),
                    'grade': grade,
                    'department': department,
                    'role': role,
                    'dob': str(dob),
                    'marital_status': marital_status,
                    'nationality': nationality,
                    'bank_details': bank_details,
                    'admin_right': False
                }
                st.success("Account created successfully! Please login.")
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_request():
    st.header("Create Expense Requisition")
    
    with st.form("request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            request_type = st.selectbox("Request Type", ["OPEX", "CAPEX"])
            expense_line = st.selectbox("Expense Line", list(EXPENSE_BUDGET.keys()))
            vendor = st.selectbox("Vendor", list(VENDOR_DATA.keys()))
            total_amount = st.number_input("Total Amount (NGN)", min_value=0.0, step=1000.0)
            
            if vendor:
                vendor_info = VENDOR_DATA.get(vendor, {})
                st.info(f"""
                    **Vendor Details:**
                    - Name: {vendor}
                    - Account: {vendor_info.get('account', 'N/A')}
                    - Bank: {vendor_info.get('bank', 'N/A')}
                    - TIN: {vendor_info.get('tin', 'N/A')}
                """)
        
        with col2:
            vat = st.checkbox("Apply VAT (7.5%)")
            wht_rate = st.selectbox("WHT Rate", ["None", "2%", "2.5%", "5%", "10%"])
            justification = st.text_area("Justification")
            supporting_doc = st.file_uploader("Supporting Document (Invoice)", type=['pdf', 'jpg', 'png'])
            
            budgeted = EXPENSE_BUDGET.get(expense_line, 0)
            st.info(f"""
                **Budget Information:**
                - Budgeted Cost: NGN {budgeted:,.2f}
                - Current Balance: NGN {budgeted:,.2f}
            """)
        
        submitted = st.form_submit_button("Submit Requisition")
        
        if submitted:
            if total_amount <= 0:
                st.error("Total amount must be greater than 0")
            else:
                vat_amount = total_amount * 0.075 if vat else 0
                wht_amount = 0
                if wht_rate != "None":
                    rate = float(wht_rate.replace('%', '')) / 100
                    wht_amount = total_amount * rate
                
                net_amount = total_amount + vat_amount - wht_amount
                
                request = {
                    'id': f"REQ-{len(st.session_state.requests) + 1:04d}",
                    'request_type': request_type,
                    'expense_line': expense_line,
                    'vendor': vendor,
                    'total_amount': total_amount,
                    'vat': vat_amount,
                    'wht': wht_amount,
                    'net_amount': net_amount,
                    'justification': justification,
                    'department': st.session_state.user_department,
                    'requested_by': st.session_state.username,
                    'status': 'Pending',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'budgeted': budgeted,
                    'approvals': [],
                    'current_level': 0
                }
                
                approval_chain = get_approval_chain(st.session_state.user_department, net_amount)
                request['approval_chain'] = approval_chain
                request['approvals'] = [{'level': i, 'approver': approver, 'status': 'Pending', 'date': ''} 
                                       for i, approver in enumerate(approval_chain)]
                
                st.session_state.requests.append(request)
                st.success(f"Request {request['id']} submitted successfully!")
                st.rerun()

def get_approval_chain(department, amount):
    if department == 'Administration':
        chain = ['Head of Admin']
        if amount > 250000:
            chain.append('Head of Investment')
        else:
            chain.append('Head of Finance')
        chain.extend(['Head of Compliance', 'Head of Internal Control'])
        if amount > 5000000:
            chain.append('CFO/ED')
        return chain
    return ['Head of Department', 'Head of Finance', 'Head of Compliance', 'Head of Internal Control']

def view_requests():
    st.header("View Requests")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Approved", "Rejected", "More Info"])
    with col2:
        if st.session_state.admin_right:
            dept_filter = st.selectbox("Department", ["All"] + list(set([r['department'] for r in st.session_state.requests])))
        else:
            dept_filter = st.session_state.user_department
    
    filtered_requests = st.session_state.requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['status'] == status_filter]
    if dept_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['department'] == dept_filter]
    
    if filtered_requests:
        df = pd.DataFrame(filtered_requests)
        display_cols = ['id', 'request_type', 'expense_line', 'total_amount', 'net_amount', 'status', 'requested_by', 'date']
        st.dataframe(df[display_cols], use_container_width=True)
        
        for request in filtered_requests:
            with st.expander(f"{request['id']} - {request['expense_line']} - {request['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Request Type:** {request['request_type']}")
                    st.write(f"**Total Amount:** NGN {request['total_amount']:,.2f}")
                    st.write(f"**VAT:** NGN {request['vat']:,.2f}")
                    st.write(f"**WHT:** NGN {request['wht']:,.2f}")
                    st.write(f"**Net Amount:** NGN {request['net_amount']:,.2f}")
                    st.write(f"**Vendor:** {request['vendor']}")
                    st.write(f"**Justification:** {request['justification']}")
                
                with col2:
                    st.write(f"**Department:** {request['department']}")
                    st.write(f"**Requested By:** {request['requested_by']}")
                    st.write(f"**Date:** {request['date']}")
                    st.write(f"**Budgeted:** NGN {request['budgeted']:,.2f}")
                    st.write(f"**Budget Balance:** NGN {request['budgeted'] - request['net_amount']:,.2f}")
                
                st.subheader("Approval Chain")
                approval_data = []
                for approval in request['approvals']:
                    status_color = "🟢" if approval['status'] == 'Approved' else "🔴" if approval['status'] == 'Rejected' else "🟡" if approval['status'] == 'More Info' else "⚪"
                    approval_data.append([approval['level'] + 1, approval['approver'], f"{status_color} {approval['status']}", approval['date']])
                
                st.table(pd.DataFrame(approval_data, columns=['Level', 'Approver', 'Status', 'Date']))
                
                user_role = st.session_state.user_role
                current_level = request['current_level']
                if current_level < len(request['approvals']) and request['approvals'][current_level]['approver'] == user_role:
                    st.subheader("Approval Actions")
                    action = st.radio("Action", ["Approve", "Reject", "Request More Information"], key=f"action_{request['id']}")
                    comments = st.text_area("Comments", key=f"comments_{request['id']}")
                    
                    if st.button("Submit Action", key=f"submit_{request['id']}"):
                        request['approvals'][current_level]['status'] = action
                        request['approvals'][current_level]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        if action == "Approve":
                            if current_level == len(request['approvals']) - 1:
                                request['status'] = 'Approved'
                            else:
                                request['current_level'] = current_level + 1
                        elif action == "Reject":
                            request['status'] = 'Rejected'
                        elif action == "Request More Information":
                            request['status'] = 'More Info'
                        
                        st.success(f"Action submitted for {request['id']}")
                        st.rerun()
                
                if request['status'] == 'Approved':
                    if st.button(f"Generate Report for {request['id']}"):
                        html_report = generate_html_report(request)
                        st.download_button(
                            label="Download Report (HTML)",
                            data=html_report,
                            file_name=f"{request['id']}_report.html",
                            mime="text/html"
                        )
    else:
        st.info("No requests found")

def vendor_management():
    st.header("Vendor Management")
    
    tab1, tab2 = st.tabs(["Register Vendor", "Vendor Analytics"])
    
    with tab1:
        with st.form("vendor_registration"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_name = st.text_input("Vendor Name")
                contact_person = st.text_input("Contact Person")
                class_of_business = st.text_input("Class of Business")
                email = st.text_input("Email Address")
                rc_number = st.text_input("RC Number")
                address = st.text_area("Address")
                tin_number = st.text_input("TIN Number")
            
            with col2:
                st.subheader("Bank Information")
                account_name = st.text_input("Account Name")
                account_number = st.text_input("Account Number")
                service_provided = st.text_area("Service Provided")
                
                st.subheader("Supporting Documents")
                cac_doc = st.file_uploader("CAC Document", type=['pdf'], key="cac")
                pca_doc = st.file_uploader("PCA Third Party Profiler", type=['pdf'], key="pca")
                abc_doc = st.file_uploader("ABC DD for Supplier", type=['pdf'], key="abc")
                hse_doc = st.file_uploader("HSE Policy", type=['pdf'], key="hse")
                continuity_doc = st.file_uploader("Business Continuity Policy", type=['pdf'], key="continuity")
            
            submitted = st.form_submit_button("Submit Vendor Registration")
            
            if submitted:
                vendor = {
                    'vendor_name': vendor_name,
                    'contact_person': contact_person,
                    'class_of_business': class_of_business,
                    'email': email,
                    'rc_number': rc_number,
                    'address': address,
                    'tin_number': tin_number,
                    'account_name': account_name,
                    'account_number': account_number,
                    'service_provided': service_provided,
                    'status': 'Pending',
                    'approvals': [
                        {'level': 1, 'approver': 'Head of Compliance', 'status': 'Pending'},
                        {'level': 2, 'approver': 'Head of Internal Control', 'status': 'Pending'}
                    ],
                    'current_level': 0,
                    'submitted_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.vendors.append(vendor)
                st.success("Vendor registration submitted for approval!")
    
    with tab2:
        if st.session_state.vendors:
            df = pd.DataFrame(st.session_state.vendors)
            st.subheader("Vendor Analytics")
            
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, title="Vendor Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Approved Vendors")
            approved_vendors = [v for v in st.session_state.vendors if v['status'] == 'Approved']
            if approved_vendors:
                st.dataframe(pd.DataFrame(approved_vendors)[['vendor_name', 'contact_person', 'email', 'service_provided']])
            else:
                st.info("No approved vendors yet")
        else:
            st.info("No vendors registered yet")

def dashboard():
    st.title("Expense Management Dashboard")
    
    total_requests = len(st.session_state.requests)
    pending_requests = len([r for r in st.session_state.requests if r['status'] == 'Pending'])
    approved_requests = len([r for r in st.session_state.requests if r['status'] == 'Approved'])
    total_amount = sum([r['net_amount'] for r in st.session_state.requests if r['status'] == 'Approved'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requests", total_requests)
    with col2:
        st.metric("Pending", pending_requests)
    with col3:
        st.metric("Approved", approved_requests)
    with col4:
        st.metric("Total Spend", f"NGN {total_amount:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.requests:
            df = pd.DataFrame(st.session_state.requests)
            dept_counts = df['department'].value_counts()
            fig = px.bar(x=dept_counts.index, y=dept_counts.values, title="Requests by Department")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.session_state.requests:
            approved = [r for r in st.session_state.requests if r['status'] == 'Approved']
            if approved:
                df_approved = pd.DataFrame(approved)
                expense_summary = df_approved.groupby('expense_line')['net_amount'].sum().reset_index()
                expense_summary['budget'] = expense_summary['expense_line'].map(EXPENSE_BUDGET)
                expense_summary = expense_summary[expense_summary['budget'].notna()]
                
                if not expense_summary.empty:
                    fig = go.Figure(data=[
                        go.Bar(name='Budget', x=expense_summary['expense_line'], y=expense_summary['budget']),
                        go.Bar(name='Actual', x=expense_summary['expense_line'], y=expense_summary['net_amount'])
                    ])
                    fig.update_layout(title="Budget vs Actual by Expense Line", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Recent Requests")
    if st.session_state.requests:
        recent = pd.DataFrame(st.session_state.requests[-5:])
        st.dataframe(recent[['id', 'expense_line', 'total_amount', 'status', 'requested_by', 'date']], use_container_width=True)

def user_management():
    if not st.session_state.admin_right:
        st.error("You don't have permission to access this page")
        return
    
    st.header("User Management")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("All Users")
        users_data = []
        for username, data in DEFAULT_USERS.items():
            users_data.append({
                'Username': username,
                'Role': data['role'],
                'Department': data['department'],
                'Admin': data.get('admin_right', False)
            })
        for username, data in st.session_state.users.items():
            users_data.append({
                'Username': username,
                'Role': data['role'],
                'Department': data['department'],
                'Admin': data.get('admin_right', False)
            })
        st.dataframe(pd.DataFrame(users_data), use_container_width=True)
    
    with col2:
        st.subheader("Add New User")
        with st.form("add_user_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.text_input("Role")
            department = st.text_input("Department")
            admin_right = st.checkbox("Admin Rights")
            
            if st.form_submit_button("Add User"):
                if username in DEFAULT_USERS or username in st.session_state.users:
                    st.error("Username already exists")
                else:
                    st.session_state.users[username] = {
                        'password': hash_password(password),
                        'role': role,
                        'department': department,
                        'admin_right': admin_right
                    }
                    st.success(f"User {username} added successfully!")

def main():
    st.set_page_config(
        page_title="Prudential Zenith Expense Management",
        page_icon="💰",
        layout="wide"
    )
    
    st.sidebar.image("https://via.placeholder.com/200x60?text=Prudential+Zenith", use_column_width=True)
    
    if not st.session_state.authenticated:
        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            login_page()
        with register_tab:
            register_page()
    else:
        st.sidebar.markdown(f"**Welcome, {st.session_state.username}**")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
        st.sidebar.markdown(f"**Department:** {st.session_state.user_department}")
        st.sidebar.markdown("---")
        
        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",
                options=["Dashboard", "Create Request", "View Requests", "Vendor Management", "User Management"],
                icons=["house", "plus-circle", "list-task", "building", "people"],
                menu_icon="cast",
                default_index=0,
            )
        
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.user_department = None
            st.rerun()
        
        if selected == "Dashboard":
            dashboard()
        elif selected == "Create Request":
            create_request()
        elif selected == "View Requests":
            view_requests()
        elif selected == "Vendor Management":
            vendor_management()
        elif selected == "User Management":
            user_management()

if __name__ == "__main__":
    main()
