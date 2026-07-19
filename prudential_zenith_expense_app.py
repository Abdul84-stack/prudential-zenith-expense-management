# app.py - Complete Fixed Version with Working Approvals & PDF Reports
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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Page Configuration
st.set_page_config(
    page_title="Prudential Zenith Expense Management",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --pz-red: #ED1C24;
        --pz-dark: #1a1a1a;
        --pz-light: #f8f9fa;
        --pz-gray: #666666;
    }
    
    .stApp {
        background-color: #f5f5f5;
    }
    
    .login-container {
        max-width: 380px !important;
        margin: 60px auto !important;
        padding: 35px 40px !important;
        background: white !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12) !important;
        border-top: 5px solid #ED1C24 !important;
    }
    
    .login-container h1 {
        color: #1a1a1a;
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .login-container .subtitle {
        text-align: center;
        color: #666;
        font-size: 13px;
        margin-bottom: 25px;
    }
    
    .login-container .brand-logo {
        text-align: center;
        margin-bottom: 15px;
    }
    
    .login-container .brand-logo .pz-red {
        color: #ED1C24;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    .login-container .brand-logo .pz-dark {
        color: #1a1a1a;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    .login-container .brand-logo .pz-sub {
        font-size: 11px;
        color: #666;
        letter-spacing: 3px;
        font-weight: 600;
    }
    
    .metric-card {
        background: white;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #ED1C24;
        margin-bottom: 12px;
        transition: all 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.10);
    }
    
    .metric-card .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    .metric-card .metric-label {
        font-size: 13px;
        color: #666;
        font-weight: 500;
    }
    
    .approval-card {
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        min-height: 90px;
        border: 1px solid #ddd;
        background: white;
    }
    
    .approval-card .emoji {
        font-size: 24px;
    }
    
    .approval-card .approver-name {
        font-weight: 600;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .approval-card .status-text {
        font-size: 11px;
        margin-top: 3px;
    }
    
    .approval-card .date-text {
        font-size: 10px;
        color: #999;
        margin-top: 2px;
    }
    
    .approval-card .action-required {
        font-size: 10px;
        color: #ED1C24;
        font-weight: 600;
        margin-top: 3px;
    }
    
    .approval-card-current {
        border: 2px solid #ED1C24;
        background: #fff8f8;
    }
    
    .approval-card-approver {
        border: 2px solid #ED1C24;
        background: #fff0f0;
    }
    
    .pending-card {
        background: #FFF8F8;
        border: 1px solid #ED1C24;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        transition: all 0.3s;
    }
    
    .pending-card:hover {
        box-shadow: 0 4px 15px rgba(237, 28, 36, 0.15);
        transform: translateX(5px);
    }
    
    .stButton > button {
        background-color: #ED1C24;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: #cc0000;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(237, 28, 36, 0.3);
    }
</style>
""", unsafe_allow_html=True)

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
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'approve_request_id' not in st.session_state:
    st.session_state.approve_request_id = None

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

# Budget Data
EXPENSE_BUDGET = {
    '430106 WEEKEND WORK ALLOWANCE': 3042000.00,
    '430608 PRINTING & STATIONERY': 29849000.00,
    '430609 ENTERTAINMENT EXPS': 28887582.06,
    '430610 OFFICE CONSUMABLES/GENERAL RUNNING EXPS': 55359000.00,
    '430612 COMMUNICATION /TELEPHONE EXPS': 20172000.00,
    '430657 CLEANING EXPENSE': 24536000.00,
    '430658 CIIN PICNIC': 13338000.00,
    '430619 REPAIRS AND MAINTENANCE-MOTOR VEHICLE': 72512000.00,
    '430620 VEHICLE RUNNING EXPENSES': 11443000.00,
    '430624 DIESEL AND FUELING': 254972000.00,
    '430625 POSTAGES': 25556000.00,
    '430626 NEWSPAPERS AND DAILIES': 1592000.00,
    '430631 INSURANCE COST': 105237000.00,
    '430633 SERVICE CHARGE': 82242000.00,
    '430644 REPAIRS AND MAINTENANCE-FURNITURE': 3730000.00,
    '430645 REPAIRS AND MAINTENANCE-EQUIPMENT': 17561815.57,
    '430647 BID EXPENSE': 739030.50,
    '430648 LATE NIGHT ALLOWANCE': 624000.00,
    '430663 RENT': 222163727.50,
    '430611 TRANSPORT & TRAVELLING': 119794000.00,
    '430629 HOTEL ACCOMMODATION': 100070000.00,
    'NEW GL DRIVERS SALARY': 150000000.00,
}

# Vendor data
VENDOR_DATA = {
    'Vendor A': {'account': '1234567890', 'bank': 'First Bank', 'tin': '12345678-0001', 'contact': 'John Doe'},
    'Vendor B': {'account': '0987654321', 'bank': 'GTBank', 'tin': '87654321-0002', 'contact': 'Jane Smith'},
    'Vendor C': {'account': '1122334455', 'bank': 'Access Bank', 'tin': '11223344-0003', 'contact': 'Bob Johnson'},
}

# Department approval mapping
DEPARTMENT_APPROVAL_MAP = {
    'Administration': ['Head of Admin', 'Head of Investment', 'Head of Compliance', 'Head of Internal Control'],
    'Finance & Investment': ['Head of Finance', 'Head of Investment', 'Head of Compliance', 'Head of Internal Control'],
    'IT': ['Head of IT', 'Head of Admin', 'Head of Compliance', 'Head of Internal Control'],
    'Corporate Sales': ['Head Corporate Sales', 'Head of Compliance', 'Head of Internal Control'],
    'Legal and Compliance': ['Head of Compliance', 'Head of Internal Control'],
    'Internal Control & Risk': ['Head of Internal Control', 'Head of Compliance'],
    'HR': ['Head of HR', 'Head of Admin', 'Head of Compliance', 'Head of Internal Control'],
}

def get_approval_chain(department, amount):
    """Get approval chain based on department and amount"""
    base_chain = DEPARTMENT_APPROVAL_MAP.get(department, ['Head of Department', 'Head of Compliance', 'Head of Internal Control'])
    
    chain = []
    for approver in base_chain:
        # Skip Investment for amounts <= 250,000
        if approver == 'Head of Investment' and amount <= 250000:
            continue
        # Skip Finance for amounts > 250,000
        if approver == 'Head of Finance' and amount > 250000:
            continue
        # Skip CFO for amounts <= 5,000,000
        if approver == 'CFO/ED' and amount <= 5000000:
            continue
        chain.append(approver)
    
    # Add CFO for amounts > 5,000,000
    if amount > 5000000 and 'CFO/ED' not in chain:
        chain.append('CFO/ED')
    
    # Ensure minimum chain
    if not chain:
        chain = ['Head of Department']
    
    return chain

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

def generate_pdf_report(request_data):
    """Generate PDF report using reportlab"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ED1C24'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    story.append(Paragraph("PRUDENTIAL ZENITH LIFE INSURANCE", title_style))
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    story.append(Paragraph("Expense Requisition Report", subtitle_style))
    story.append(Spacer(1, 12))
    
    # Request details table
    data = [
        ['Field', 'Value'],
        ['Request ID', request_data.get('id', 'N/A')],
        ['Request Type', request_data.get('request_type', 'N/A')],
        ['Expense Line', request_data.get('expense_line', 'N/A')],
        ['Vendor', request_data.get('vendor', 'N/A')],
        ['Total Amount', f"NGN {request_data.get('total_amount', 0):,.2f}"],
        ['VAT (7.5%)', f"NGN {request_data.get('vat', 0):,.2f}"],
        ['WHT', f"NGN {request_data.get('wht', 0):,.2f}"],
        ['Net Amount', f"NGN {request_data.get('net_amount', 0):,.2f}"],
        ['Department', request_data.get('department', 'N/A')],
        ['Requested By', request_data.get('requested_by', 'N/A')],
        ['Date', request_data.get('date', 'N/A')],
        ['Status', request_data.get('status', 'N/A')],
        ['Justification', request_data.get('justification', 'N/A')],
    ]
    
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ED1C24')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Approval chain
    story.append(Paragraph("Approval Chain", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    approval_data = [['Level', 'Approver', 'Status', 'Date']]
    for approval in request_data.get('approvals', []):
        approval_data.append([
            str(approval.get('level', 0) + 1),
            approval.get('approver', ''),
            approval.get('status', 'Pending'),
            approval.get('date', '')
        ])
    
    t2 = Table(approval_data, colWidths=[60, 150, 100, 150])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ED1C24')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    story.append(Paragraph("Generated on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), footer_style))
    story.append(Paragraph("© 2024 Prudential Zenith Life Insurance. All rights reserved.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def login_page():
    st.markdown("""
    <div class="login-container">
        <div class="brand-logo">
            <span class="pz-red">PRUDENTIAL</span><br>
            <span class="pz-dark">ZENITH</span><br>
            <span class="pz-sub">LIFE INSURANCE</span>
        </div>
        <h1>Welcome Back</h1>
        <p class="subtitle">Sign in to access your expense management dashboard</p>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username", key="login_username", label_visibility="collapsed")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign In", use_container_width=True):
            if authenticate_user(username, password):
                user_data = get_user_data(username)
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = user_data['role']
                st.session_state.user_department = user_data['department']
                st.session_state.admin_right = user_data.get('admin_right', False)
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    st.markdown("""
        <div style="text-align: center; margin-top: 15px; color: #999; font-size: 12px;">
            <p>Contact your system administrator for access</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def register_page():
    st.markdown("""
    <div class="login-container" style="max-width: 500px !important;">
        <div class="brand-logo">
            <span class="pz-red">PRUDENTIAL</span><br>
            <span class="pz-dark">ZENITH</span><br>
            <span class="pz-sub">LIFE INSURANCE</span>
        </div>
        <h1>Create Account</h1>
        <p class="subtitle">Register for expense management access</p>
    """, unsafe_allow_html=True)
    
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
                "Head of HR", "Employee", "Head of Compliance", "Head of Internal Audit",
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
                st.success("✅ Account created successfully! Please login.")
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_request():
    st.header("📝 Create Expense Requisition")
    st.markdown("---")
    
    with st.form("request_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            request_type = st.selectbox("Request Type", ["OPEX", "CAPEX"])
            expense_line = st.selectbox("Expense Line", list(EXPENSE_BUDGET.keys()))
            vendor = st.selectbox("Vendor", list(VENDOR_DATA.keys()))
            total_amount = st.number_input("Total Amount (NGN)", min_value=0.0, step=1000.0, format="%.2f")
            
            if vendor:
                vendor_info = VENDOR_DATA.get(vendor, {})
                st.info(f"""
                    **🏢 Vendor Details:**
                    - **Name:** {vendor}
                    - **Account:** {vendor_info.get('account', 'N/A')}
                    - **Bank:** {vendor_info.get('bank', 'N/A')}
                    - **TIN:** {vendor_info.get('tin', 'N/A')}
                """)
        
        with col2:
            vat = st.checkbox("Apply VAT (7.5%)")
            wht_rate = st.selectbox("WHT Rate", ["None", "2%", "2.5%", "5%", "10%"])
            justification = st.text_area("Justification / Business Case", height=100)
            supporting_doc = st.file_uploader("Supporting Document (Invoice)", type=['pdf', 'jpg', 'png'])
            
            budgeted = EXPENSE_BUDGET.get(expense_line, 0)
            st.info(f"""
                **💰 Budget Information:**
                - **Budgeted Cost:** NGN {budgeted:,.2f}
                - **Current Balance:** NGN {budgeted:,.2f}
            """)
        
        submitted = st.form_submit_button("Submit Requisition", use_container_width=True)
        
        if submitted:
            if total_amount <= 0:
                st.error("❌ Total amount must be greater than 0")
            elif not justification:
                st.error("❌ Please provide a justification")
            else:
                vat_amount = total_amount * 0.075 if vat else 0
                wht_amount = 0
                if wht_rate != "None":
                    rate = float(wht_rate.replace('%', '')) / 100
                    wht_amount = total_amount * rate
                
                net_amount = total_amount + vat_amount - wht_amount
                
                # Get approval chain
                approval_chain = get_approval_chain(st.session_state.user_department, net_amount)
                
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
                    'approval_chain': approval_chain,
                    'approvals': [{'level': i, 'approver': approver, 'status': 'Pending', 'date': ''} 
                                   for i, approver in enumerate(approval_chain)],
                    'current_level': 0,
                    'rejection_reason': ''
                }
                
                st.session_state.requests.append(request)
                
                if approval_chain:
                    st.session_state.notifications.append({
                        'request_id': request['id'],
                        'message': f"New requisition {request['id']} from {request['requested_by']} requires your approval",
                        'approver': approval_chain[0],
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'read': False
                    })
                
                st.success(f"✅ Request {request['id']} submitted successfully!")
                st.balloons()
                st.rerun()

def view_requests():
    st.header("📋 Requests Management")
    st.markdown("---")
    
    # Get user's pending approvals
    user_role = st.session_state.user_role
    pending_for_user = []
    for req in st.session_state.requests:
        if req['status'] == 'Pending':
            # Check if user is the current approver
            current_level = req['current_level']
            if current_level < len(req['approvals']):
                if req['approvals'][current_level]['approver'] == user_role:
                    pending_for_user.append(req)
    
    # Show pending approvals
    if pending_for_user:
        st.warning(f"🔔 You have {len(pending_for_user)} pending approval(s) requiring your action!")
        
        st.subheader("📋 Your Pending Approvals - Click Review to Approve")
        
        for req in pending_for_user:
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 1])
            with col1:
                st.markdown(f"**{req['id']}**")
            with col2:
                st.markdown(f"{req['expense_line'][:35]}...")
            with col3:
                st.markdown(f"**NGN {req['net_amount']:,.2f}**")
            with col4:
                st.markdown(f"👤 {req['requested_by']}")
            with col5:
                if st.button("Review", key=f"review_btn_{req['id']}"):
                    st.session_state.approve_request_id = req['id']
                    st.rerun()
            st.markdown("---")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Approved", "Rejected", "More Info"])
    with col2:
        if st.session_state.admin_right:
            all_depts = list(set([r['department'] for r in st.session_state.requests])) if st.session_state.requests else []
            dept_filter = st.selectbox("Department", ["All"] + all_depts)
        else:
            dept_filter = st.session_state.user_department
    with col3:
        show_pending_only = st.checkbox("Show only my pending approvals", value=bool(pending_for_user))
    
    # Filter requests
    filtered_requests = st.session_state.requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['status'] == status_filter]
    if dept_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['department'] == dept_filter]
    if show_pending_only:
        filtered_requests = [r for r in filtered_requests if r in pending_for_user]
    
    if filtered_requests:
        # Create a dataframe for display
        df = pd.DataFrame(filtered_requests)
        display_cols = ['id', 'request_type', 'expense_line', 'total_amount', 'net_amount', 'status', 'requested_by', 'date']
        st.dataframe(df[display_cols].style.format({
            'total_amount': 'NGN {:,.2f}',
            'net_amount': 'NGN {:,.2f}'
        }), use_container_width=True, height=300)
        
        # Detailed view for each request
        for request in filtered_requests:
            # Check if this request should be expanded
            is_pending_for_user = request in pending_for_user
            is_selected = st.session_state.approve_request_id == request['id']
            is_expanded = is_pending_for_user or is_selected
            
            expander_title = f"{request['id']} - {request['expense_line'][:30]}... - {request['status']}"
            if is_pending_for_user:
                expander_title = f"🔔 {expander_title}"
            
            with st.expander(expander_title, expanded=is_expanded):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📌 Request Details**")
                    st.write(f"**Type:** {request['request_type']}")
                    st.write(f"**Line:** {request['expense_line']}")
                    st.write(f"**Vendor:** {request['vendor']}")
                    st.write(f"**Total Amount:** NGN {request['total_amount']:,.2f}")
                    st.write(f"**VAT:** NGN {request['vat']:,.2f}")
                    st.write(f"**WHT:** NGN {request['wht']:,.2f}")
                    st.write(f"**Net Amount:** **NGN {request['net_amount']:,.2f}**")
                
                with col2:
                    st.markdown(f"**👤 Request Information**")
                    st.write(f"**Department:** {request['department']}")
                    st.write(f"**Requested By:** {request['requested_by']}")
                    st.write(f"**Date:** {request['date']}")
                    st.write(f"**Budgeted:** NGN {request['budgeted']:,.2f}")
                    balance = request['budgeted'] - request['net_amount']
                    st.write(f"**Budget Balance:** NGN {balance:,.2f}")
                    st.write(f"**Justification:** {request['justification']}")
                
                # Approval chain
                st.markdown("---")
                st.markdown("**📊 Approval Chain**")
                
                approval_cols = st.columns(len(request['approvals']))
                
                for idx, (col, approval) in enumerate(zip(approval_cols, request['approvals'])):
                    status_emoji = "✅" if approval['status'] == 'Approved' else "❌" if approval['status'] == 'Rejected' else "⏳"
                    status_color = "#28a745" if approval['status'] == 'Approved' else "#dc3545" if approval['status'] == 'Rejected' else "#ffc107"
                    is_current = idx == request['current_level'] and request['status'] == 'Pending'
                    is_approver = approval['approver'] == user_role and approval['status'] == 'Pending'
                    
                    card_class = "approval-card"
                    if is_approver:
                        card_class += " approval-card-approver"
                    elif is_current:
                        card_class += " approval-card-current"
                    
                    with col:
                        st.markdown(f"""
                            <div class="{card_class}">
                                <div class="emoji">{status_emoji}</div>
                                <div class="approver-name">{approval['approver']}</div>
                                <div class="status-text" style="color: {status_color};">{approval['status']}</div>
                                <div class="date-text">{approval['date']}</div>
                                {f'<div class="action-required">⬅️ Your Action Required</div>' if is_approver else ''}
                                {f'<div class="action-required" style="color: #ffc107;">⬅️ Current Step</div>' if is_current and not is_approver else ''}
                            </div>
                        """, unsafe_allow_html=True)
                
                # Approval form - Show if user is the current approver
                current_level = request['current_level']
                is_approver = False
                
                # Check if current level is valid and user is the approver
                if current_level < len(request['approvals']):
                    if request['approvals'][current_level]['approver'] == user_role and request['approvals'][current_level]['status'] == 'Pending':
                        is_approver = True
                
                if is_approver:
                    st.markdown("---")
                    st.markdown("## ✋ Your Approval Required")
                    st.info(f"You are the current approver for this request. Please review the details and take action.")
                    
                    with st.form(key=f"approval_form_{request['id']}"):
                        action = st.radio("Select Action", ["Approve", "Reject", "Request More Information"], 
                                        key=f"action_{request['id']}", horizontal=True)
                        comments = st.text_area("Comments / Notes", placeholder="Add your comments here...", key=f"comments_{request['id']}")
                        
                        if st.form_submit_button("Submit Decision", use_container_width=True):
                            # Update the approval
                            request['approvals'][current_level]['status'] = action
                            request['approvals'][current_level]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                            if action == "Approve":
                                # Check if this is the last approval
                                if current_level == len(request['approvals']) - 1:
                                    request['status'] = 'Approved'
                                    st.success(f"✅ Request {request['id']} has been FULLY APPROVED!")
                                    st.balloons()
                                else:
                                    # Move to next approver
                                    request['current_level'] = current_level + 1
                                    request['status'] = 'Pending'
                                    # Notify next approver
                                    next_approver = request['approvals'][current_level + 1]['approver']
                                    st.session_state.notifications.append({
                                        'request_id': request['id'],
                                        'message': f"Request {request['id']} has been approved by {user_role}. Now awaiting your approval.",
                                        'approver': next_approver,
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                        'read': False
                                    })
                                    st.success(f"✅ Request {request['id']} approved. Sent to {next_approver} for further review.")
                            
                            elif action == "Reject":
                                request['status'] = 'Rejected'
                                request['rejection_reason'] = comments
                                st.error(f"❌ Request {request['id']} has been rejected.")
                            
                            elif action == "Request More Information":
                                request['status'] = 'More Info'
                                st.warning(f"ℹ️ More information requested for {request['id']}")
                            
                            # Clear the approval request ID after action
                            st.session_state.approve_request_id = None
                            st.rerun()
                else:
                    # Show who the current approver is
                    if current_level < len(request['approvals']):
                        st.info(f"⏳ Currently awaiting approval from: **{request['approvals'][current_level]['approver']}**")
                
                # Generate PDF report for approved requests
                if request['status'] == 'Approved':
                    if st.button(f"📄 Generate PDF Report for {request['id']}", key=f"pdf_report_{request['id']}"):
                        pdf_buffer = generate_pdf_report(request)
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_buffer,
                            file_name=f"{request['id']}_report.pdf",
                            mime="application/pdf"
                        )
    else:
        st.info("📭 No requests found matching your criteria")

def vendor_management():
    st.header("🏢 Vendor Management")
    st.markdown("---")
    
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
            
            submitted = st.form_submit_button("Submit Vendor Registration", use_container_width=True)
            
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
                st.success("✅ Vendor registration submitted for approval!")
    
    with tab2:
        if st.session_state.vendors:
            df = pd.DataFrame(st.session_state.vendors)
            st.subheader("Vendor Analytics")
            
            col1, col2 = st.columns(2)
            with col1:
                status_counts = df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, 
                           title="Vendor Status Distribution",
                           color_discrete_sequence=['#ED1C24', '#1a1a1a', '#28a745', '#17a2b8'])
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Approved Vendors")
                approved_vendors = [v for v in st.session_state.vendors if v['status'] == 'Approved']
                if approved_vendors:
                    st.dataframe(pd.DataFrame(approved_vendors)[['vendor_name', 'contact_person', 'email', 'service_provided']])
                else:
                    st.info("No approved vendors yet")
        else:
            st.info("📭 No vendors registered yet")

def dashboard():
    st.title("🏦 Prudential Zenith Expense Management Dashboard")
    st.markdown("---")
    
    # Get pending approvals for current user
    user_role = st.session_state.user_role
    pending_for_user = []
    for req in st.session_state.requests:
        if req['status'] == 'Pending':
            current_level = req['current_level']
            if current_level < len(req['approvals']):
                if req['approvals'][current_level]['approver'] == user_role:
                    pending_for_user.append(req)
    
    # Display notifications
    if pending_for_user:
        st.warning(f"🔔 You have {len(pending_for_user)} pending approval(s) requiring your action!")
        
        st.subheader("📋 Quick Actions - Pending Approvals")
        for req in pending_for_user:
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 1])
            with col1:
                st.markdown(f"**{req['id']}**")
            with col2:
                st.markdown(f"{req['expense_line'][:30]}...")
            with col3:
                st.markdown(f"**NGN {req['net_amount']:,.2f}**")
            with col4:
                st.markdown(f"👤 {req['requested_by']}")
            with col5:
                if st.button(f"Review", key=f"dash_review_{req['id']}"):
                    st.session_state.approve_request_id = req['id']
                    st.rerun()
            st.markdown("---")
    
    # Key Metrics
    total_requests = len(st.session_state.requests)
    pending_requests = len([r for r in st.session_state.requests if r['status'] == 'Pending'])
    approved_requests = len([r for r in st.session_state.requests if r['status'] == 'Approved'])
    rejected_requests = len([r for r in st.session_state.requests if r['status'] == 'Rejected'])
    total_amount = sum([r['net_amount'] for r in st.session_state.requests if r['status'] == 'Approved'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_requests}</div>
                <div class="metric-label">📊 Total Requests</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ffc107;">
                <div class="metric-value" style="color: #ffc107;">{pending_requests}</div>
                <div class="metric-label">⏳ Pending</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #28a745;">
                <div class="metric-value" style="color: #28a745;">{approved_requests}</div>
                <div class="metric-label">✅ Approved</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #dc3545;">
                <div class="metric-value" style="color: #dc3545;">{rejected_requests}</div>
                <div class="metric-label">❌ Rejected</div>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ED1C24;">
                <div class="metric-value" style="color: #ED1C24;">NGN {total_amount:,.0f}</div>
                <div class="metric-label">💰 Total Spend</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.requests:
            df = pd.DataFrame(st.session_state.requests)
            dept_counts = df['department'].value_counts().head(10)
            fig = px.bar(x=dept_counts.index, y=dept_counts.values, 
                        title="Requests by Department",
                        color=dept_counts.values,
                        color_continuous_scale=['#1a1a1a', '#ED1C24'],
                        labels={'x': 'Department', 'y': 'Number of Requests'})
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.session_state.requests:
            approved = [r for r in st.session_state.requests if r['status'] == 'Approved']
            if approved:
                df_approved = pd.DataFrame(approved)
                expense_summary = df_approved.groupby('expense_line')['net_amount'].sum().reset_index()
                expense_summary = expense_summary.nlargest(10, 'net_amount')
                expense_summary['budget'] = expense_summary['expense_line'].map(EXPENSE_BUDGET)
                expense_summary = expense_summary[expense_summary['budget'].notna()]
                
                if not expense_summary.empty:
                    fig = go.Figure(data=[
                        go.Bar(name='Budget', x=expense_summary['expense_line'], y=expense_summary['budget'], 
                               marker_color='#1a1a1a'),
                        go.Bar(name='Actual', x=expense_summary['expense_line'], y=expense_summary['net_amount'],
                               marker_color='#ED1C24')
                    ])
                    fig.update_layout(title="Budget vs Actual (Top 10 Expense Lines)", 
                                     barmode='group', height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Recent Requests")
    if st.session_state.requests:
        recent = pd.DataFrame(st.session_state.requests[-5:])
        st.dataframe(recent[['id', 'expense_line', 'total_amount', 'status', 'requested_by', 'date']], 
                    use_container_width=True)

def user_management():
    if not st.session_state.admin_right:
        st.error("⛔ You don't have permission to access this page")
        return
    
    st.header("👥 User Management")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("All Users")
        users_data = []
        for username, data in DEFAULT_USERS.items():
            users_data.append({
                'Username': username,
                'Role': data['role'],
                'Department': data['department'],
                'Admin': '✅' if data.get('admin_right', False) else '❌'
            })
        for username, data in st.session_state.users.items():
            users_data.append({
                'Username': username,
                'Role': data.get('role', ''),
                'Department': data.get('department', ''),
                'Admin': '✅' if data.get('admin_right', False) else '❌'
            })
        st.dataframe(pd.DataFrame(users_data), use_container_width=True)
    
    with col2:
        st.subheader("Add New User")
        with st.form("add_user_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.text_input("Role")
            department = st.selectbox("Department", [
                "Administration", "Finance & Investment", "IT", "Corporate Sales",
                "Legal and Compliance", "Internal Control & Risk", "HR"
            ])
            admin_right = st.checkbox("Admin Rights")
            
            if st.form_submit_button("Add User", use_container_width=True):
                if username in DEFAULT_USERS or username in st.session_state.users:
                    st.error("❌ Username already exists")
                elif not username or not password:
                    st.error("❌ Username and password required")
                else:
                    st.session_state.users[username] = {
                        'password': hash_password(password),
                        'role': role,
                        'department': department,
                        'admin_right': admin_right
                    }
                    st.success(f"✅ User {username} added successfully!")

def main():
    # Custom sidebar
    st.sidebar.markdown("""
        <div style="padding: 20px 0; text-align: center; border-bottom: 2px solid #ED1C24; margin-bottom: 20px;">
            <div style="font-size: 22px; font-weight: 800; color: #ED1C24;">PRUDENTIAL</div>
            <div style="font-size: 22px; font-weight: 800; color: #1a1a1a;">ZENITH</div>
            <div style="font-size: 11px; color: #666; margin-top: 3px; letter-spacing: 2px;">LIFE INSURANCE</div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        login_tab, register_tab = st.tabs(["🔑 Sign In", "📝 Register"])
        with login_tab:
            login_page()
        with register_tab:
            register_page()
    else:
        # User info in sidebar
        st.sidebar.markdown(f"""
            <div style="background: #f8f9fa; padding: 12px 15px; border-radius: 10px; margin-bottom: 20px;">
                <div style="font-weight: 600; color: #1a1a1a; font-size: 13px;">👋 Welcome</div>
                <div style="font-size: 15px; font-weight: 700; color: #ED1C24;">{st.session_state.username}</div>
                <div style="font-size: 12px; color: #666;">{st.session_state.user_role}</div>
                <div style="font-size: 11px; color: #999;">{st.session_state.user_department}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Navigation",
                options=["Dashboard", "Create Request", "View Requests", "Vendor Management", "User Management"],
                icons=["speedometer2", "plus-circle", "list-task", "building", "people"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "#ED1C24", "font-size": "18px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", 
                                "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#ED1C24", "color": "white"},
                }
            )
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.user_department = None
            st.session_state.approve_request_id = None
            st.rerun()
        
        # Page routing
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
