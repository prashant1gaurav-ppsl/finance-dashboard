import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import trino.dbapi
import trino.auth
from typing import Dict, List
import hashlib

# Page configuration
st.set_page_config(
    page_title="Business Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 10px;
        border-bottom: 3px solid #1f77b4;
    }
    h2 {
        color: #2c3e50;
        margin-top: 30px;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# User database - Always use secrets in production!
def get_users():
    """Get users from secrets if available, otherwise use defaults for demo"""
    if 'auth' in st.secrets:
        return {
            "admin": hash_password(st.secrets["auth"]["admin"]),
            "prashant": hash_password(st.secrets["auth"]["prashant"]),
            "user1": hash_password(st.secrets["auth"]["user1"]),
            "user2": hash_password(st.secrets["auth"]["user2"]),
        }
    else:
        # Demo mode - change these passwords!
        return {
            "demo": hash_password("demo123"),
        }

USERS = get_users()

def check_authentication(username: str, password: str) -> bool:
    """Verify username and password"""
    if username in USERS:
        return USERS[username] == hash_password(password)
    return False

def login_page():
    """Display login page"""
    st.markdown("<h1 style='text-align: center;'>🔐 Business Finance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Please login to continue</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if check_authentication(username, password):
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_trino_connection():
    """Create and cache Trino database connection"""
    try:
        # Always use secrets - never hardcode credentials!
        if 'trino' not in st.secrets:
            st.error("🔒 Database credentials not configured!")
            st.info("Please add Trino credentials in Streamlit Secrets (Settings → Secrets)")
            return None
            
        conn = trino.dbapi.connect(
            host=st.secrets["trino"]["host"],
            port=int(st.secrets["trino"]["port"]),
            user=st.secrets["trino"]["user"],
            http_scheme="https",
            auth=trino.auth.BasicAuthentication(
                st.secrets["trino"]["user"],
                st.secrets["trino"]["password"]
            ),
            catalog=st.secrets["trino"]["catalog"],
            schema=st.secrets["trino"]["schema"]
        )
        return conn
    except Exception as e:
        st.warning(f"⚠️ Database connection failed: {str(e)}")
        st.info("📊 Running in DEMO mode with sample data")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def execute_query(query: str) -> pd.DataFrame:
    """Execute query and return results as DataFrame"""
    conn = get_trino_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()

# ============================================================================
# SAMPLE QUERIES (Replace with your actual queries)
# ============================================================================

QUERIES = {
    "soundbox_deployments": """
        SELECT 
            deployment_date,
            channel,
            deployments,
            net_device_addition,
            deployed_base,
            active_merchant
        FROM soundbox_daily_metrics
        WHERE deployment_date >= DATE_ADD('day', -30, CURRENT_DATE)
        ORDER BY deployment_date DESC
    """,
    
    "edc_metrics": """
        SELECT 
            transaction_date,
            channel,
            deployments,
            active_merchant,
            gmv_cr,
            transactions_mn
        FROM edc_daily_metrics
        WHERE transaction_date >= DATE_ADD('day', -30, CURRENT_DATE)
        ORDER BY transaction_date DESC
    """,
    
    "qr_metrics": """
        SELECT 
            date,
            channel,
            onboarding,
            active_merchant,
            gmv_cr,
            gmv_per_merchant
        FROM qr_daily_metrics
        WHERE date >= DATE_ADD('day', -30, CURRENT_DATE)
        ORDER BY date DESC
    """,
    
    "upi_transactions": """
        SELECT 
            txn_date,
            channel,
            upi_gmv_cr,
            upi_txn_mn,
            upi_below_2k_gmv,
            upi_above_2k_gmv
        FROM upi_daily_transactions
        WHERE txn_date >= DATE_ADD('day', -30, CURRENT_DATE)
        ORDER BY txn_date DESC
    """,
    
    "rental_collection": """
        SELECT 
            collection_date,
            device_type,
            rental_collectable_devices,
            rental_collected_devices,
            rental_collected_amount_cr
        FROM rental_collection_daily
        WHERE collection_date >= DATE_ADD('day', -30, CURRENT_DATE)
        ORDER BY collection_date DESC
    """,
    
    "mtd_summary": """
        SELECT 
            channel,
            SUM(deployments) as total_deployments,
            SUM(active_merchant) as total_active_merchants,
            SUM(gmv_cr) as total_gmv_cr,
            AVG(active_merchant_pct) as avg_active_merchant_pct
        FROM daily_channel_summary
        WHERE date >= DATE_TRUNC('month', CURRENT_DATE)
        GROUP BY channel
    """
}

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def display_kpi_metrics(df: pd.DataFrame, col1_name: str, col2_name: str, col3_name: str, col4_name: str):
    """Display KPI metrics in columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    if not df.empty:
        with col1:
            st.metric(
                label=col1_name,
                value=f"{df[col1_name].iloc[0]:,.0f}" if col1_name in df.columns else "N/A",
                delta=f"{((df[col1_name].iloc[0] - df[col1_name].iloc[1]) / df[col1_name].iloc[1] * 100):.1f}%" if len(df) > 1 and col1_name in df.columns else None
            )
        
        with col2:
            st.metric(
                label=col2_name,
                value=f"{df[col2_name].iloc[0]:,.0f}" if col2_name in df.columns else "N/A",
                delta=f"{((df[col2_name].iloc[0] - df[col2_name].iloc[1]) / df[col2_name].iloc[1] * 100):.1f}%" if len(df) > 1 and col2_name in df.columns else None
            )
        
        with col3:
            st.metric(
                label=col3_name,
                value=f"₹{df[col3_name].iloc[0]:,.2f}" if col3_name in df.columns else "N/A",
                delta=f"{((df[col3_name].iloc[0] - df[col3_name].iloc[1]) / df[col3_name].iloc[1] * 100):.1f}%" if len(df) > 1 and col3_name in df.columns else None
            )
        
        with col4:
            st.metric(
                label=col4_name,
                value=f"{df[col4_name].iloc[0]:.1f}%" if col4_name in df.columns else "N/A",
                delta=f"{(df[col4_name].iloc[0] - df[col4_name].iloc[1]):.1f}%" if len(df) > 1 and col4_name in df.columns else None
            )

def plot_trend_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#1f77b4"):
    """Create trend line chart"""
    if df.empty:
        st.warning("No data available for chart")
        return
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        name=y_col,
        line=dict(color=color, width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#2ca02c"):
    """Create bar chart"""
    if df.empty:
        st.warning("No data available for chart")
        return
    
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str):
    """Create pie chart"""
    if df.empty:
        st.warning("No data available for chart")
        return
    
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title,
        hole=0.4
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main_dashboard():
    """Main dashboard display"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Business Finance Dashboard")
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.markdown(f"**Logged in as:** {st.session_state['username']}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['authenticated'] = False
            st.rerun()
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔧 Filters")
        
        channel_filter = st.multiselect(
            "Select Channel",
            ["General Trade", "Enterprise", "Govt+Transit", "Oil & Gas", "Retail MM"],
            default=["General Trade"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        metric_type = st.selectbox(
            "Metric Type",
            ["Deployments", "GMV", "Transactions", "Active Merchants", "Rentals"]
        )
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.success("Data refreshed!")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📦 Sound Box",
        "💳 EDC Metrics",
        "📱 QR Codes",
        "💰 UPI Transactions",
        "🏦 Rental Collection",
        "📈 Channel Summary"
    ])
    
    # ========== TAB 1: Sound Box ==========
    with tab1:
        st.header("Sound Box Deployments & Metrics")
        
        # Note: Using sample data - replace with actual query
        st.info("ℹ️ Replace the query below with your actual Trino query for Sound Box metrics")
        
        sample_soundbox_data = pd.DataFrame({
            'Date': pd.date_range(start='2026-04-15', periods=27, freq='D'),
            'Deployments': [15642, 14500, 15000, 16000, 14800, 15500, 16200] * 3 + [15642] * 6,
            'Active_Merchants': [5325228, 5300000, 5310000, 5320000, 5315000, 5318000, 5322000] * 3 + [5325228] * 6,
            'GMV_Cr': [2163, 2150, 2170, 2180, 2160, 2175, 2185] * 3 + [2163] * 6,
            'Active_Merchant_Pct': [33, 32.8, 32.9, 33.1, 32.7, 33.0, 33.2] * 3 + [33] * 6
        })
        
        # KPI Metrics
        display_kpi_metrics(sample_soundbox_data, 'Deployments', 'Active_Merchants', 'GMV_Cr', 'Active_Merchant_Pct')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_trend_chart(sample_soundbox_data.tail(15), 'Date', 'Deployments', 
                           '📦 Daily Deployments Trend (Last 15 Days)', '#1f77b4')
        
        with col2:
            plot_trend_chart(sample_soundbox_data.tail(15), 'Date', 'GMV_Cr', 
                           '💰 GMV Trend (₹ Cr)', '#2ca02c')
        
        # Data table
        with st.expander("📋 View Detailed Data"):
            st.dataframe(sample_soundbox_data, use_container_width=True)
    
    # ========== TAB 2: EDC Metrics ==========
    with tab2:
        st.header("EDC Deployments & Performance")
        
        st.info("ℹ️ Replace with your actual EDC Trino query")
        
        sample_edc_data = pd.DataFrame({
            'Date': pd.date_range(start='2026-04-15', periods=27, freq='D'),
            'Deployments': [413, 400, 420, 415, 410, 425, 418] * 3 + [413] * 6,
            'Active_Merchants': [323649, 323000, 323500, 324000, 323200, 323800, 324100] * 3 + [323649] * 6,
            'GMV_Cr': [267, 260, 270, 265, 268, 272, 269] * 3 + [267] * 6,
            'Transactions_Mn': [9, 8.8, 9.1, 8.9, 9.0, 9.2, 9.1] * 3 + [9] * 6
        })
        
        # KPI Metrics
        display_kpi_metrics(sample_edc_data, 'Deployments', 'Active_Merchants', 'GMV_Cr', 'Transactions_Mn')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_bar_chart(sample_edc_data.tail(10), 'Date', 'Deployments', 
                         '📊 EDC Deployments (Last 10 Days)', '#ff7f0e')
        
        with col2:
            plot_trend_chart(sample_edc_data.tail(15), 'Date', 'GMV_Cr', 
                           '💳 EDC GMV Trend', '#d62728')
        
        with st.expander("📋 View Detailed Data"):
            st.dataframe(sample_edc_data, use_container_width=True)
    
    # ========== TAB 3: QR Codes ==========
    with tab3:
        st.header("QR Code Onboarding & Engagement")
        
        st.info("ℹ️ Replace with your actual QR Trino query")
        
        sample_qr_data = pd.DataFrame({
            'Date': pd.date_range(start='2026-04-15', periods=27, freq='D'),
            'Onboarding': [12817, 12500, 12900, 12700, 12600, 13000, 12850] * 3 + [12817] * 6,
            'Active_Merchants': [5689707, 5670000, 5680000, 5690000, 5675000, 5685000, 5695000] * 3 + [5689707] * 6,
            'GMV_Cr': [2163, 2150, 2170, 2160, 2155, 2175, 2165] * 3 + [2163] * 6,
            'GMV_Per_Merchant': [3801, 3790, 3810, 3800, 3795, 3815, 3805] * 3 + [3801] * 6
        })
        
        # KPI Metrics
        display_kpi_metrics(sample_qr_data, 'Onboarding', 'Active_Merchants', 'GMV_Cr', 'GMV_Per_Merchant')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_trend_chart(sample_qr_data.tail(15), 'Date', 'Onboarding', 
                           '📱 Daily QR Onboarding Trend', '#9467bd')
        
        with col2:
            plot_trend_chart(sample_qr_data.tail(15), 'Date', 'GMV_Per_Merchant', 
                           '💵 GMV per Merchant Trend', '#8c564b')
        
        with st.expander("📋 View Detailed Data"):
            st.dataframe(sample_qr_data, use_container_width=True)
    
    # ========== TAB 4: UPI Transactions ==========
    with tab4:
        st.header("UPI Transaction Analytics")
        
        st.info("ℹ️ Replace with your actual UPI Trino query")
        
        sample_upi_data = pd.DataFrame({
            'Date': pd.date_range(start='2026-04-15', periods=27, freq='D'),
            'UPI_GMV_Cr': [2111, 2100, 2120, 2110, 2105, 2125, 2115] * 3 + [2111] * 6,
            'UPI_Txn_Mn': [113, 112, 114, 113, 112.5, 114.5, 113.5] * 3 + [113] * 6,
            'UPI_Below_2K': [1338, 1330, 1345, 1340, 1335, 1350, 1342] * 3 + [1338] * 6,
            'UPI_Above_2K': [773, 770, 775, 770, 770, 775, 773] * 3 + [773] * 6
        })
        
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total UPI GMV (₹ Cr)", f"₹{sample_upi_data['UPI_GMV_Cr'].iloc[0]:,.0f}")
        with col2:
            st.metric("Total Transactions (Mn)", f"{sample_upi_data['UPI_Txn_Mn'].iloc[0]:.1f}")
        with col3:
            st.metric("GMV ≤₹2K (Cr)", f"₹{sample_upi_data['UPI_Below_2K'].iloc[0]:,.0f}")
        with col4:
            st.metric("GMV >₹2K (Cr)", f"₹{sample_upi_data['UPI_Above_2K'].iloc[0]:,.0f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_trend_chart(sample_upi_data.tail(15), 'Date', 'UPI_GMV_Cr', 
                           '💰 UPI GMV Trend', '#17becf')
        
        with col2:
            # Pie chart for UPI distribution
            latest_data = sample_upi_data.iloc[0]
            distribution_df = pd.DataFrame({
                'Category': ['UPI ≤₹2K', 'UPI >₹2K'],
                'GMV': [latest_data['UPI_Below_2K'], latest_data['UPI_Above_2K']]
            })
            plot_pie_chart(distribution_df, 'Category', 'GMV', '📊 UPI GMV Distribution')
        
        with st.expander("📋 View Detailed Data"):
            st.dataframe(sample_upi_data, use_container_width=True)
    
    # ========== TAB 5: Rental Collection ==========
    with tab5:
        st.header("Rental Collection Metrics")
        
        st.info("ℹ️ Replace with your actual Rental Collection Trino query")
        
        sample_rental_data = pd.DataFrame({
            'Date': pd.date_range(start='2026-04-15', periods=27, freq='D'),
            'Collectable_Merchants': [302420, 300000, 301000, 303000, 299000, 302000, 304000] * 3 + [302420] * 6,
            'Collected_Merchants': [305067, 303000, 304000, 306000, 302000, 305000, 307000] * 3 + [305067] * 6,
            'Amount_Collected_Cr': [3, 2.9, 3.0, 3.1, 2.95, 3.05, 3.08] * 3 + [3] * 6,
            'Collection_Rate_Pct': [85, 84.5, 85.2, 85.5, 84.8, 85.3, 85.6] * 3 + [85] * 6
        })
        
        # KPI Metrics
        display_kpi_metrics(sample_rental_data, 'Collectable_Merchants', 'Collected_Merchants', 
                          'Amount_Collected_Cr', 'Collection_Rate_Pct')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_trend_chart(sample_rental_data.tail(15), 'Date', 'Amount_Collected_Cr', 
                           '💵 Rental Collection Trend (₹ Cr)', '#e377c2')
        
        with col2:
            plot_bar_chart(sample_rental_data.tail(10), 'Date', 'Collected_Merchants', 
                         '👥 Merchants Collected (Last 10 Days)', '#7f7f7f')
        
        with st.expander("📋 View Detailed Data"):
            st.dataframe(sample_rental_data, use_container_width=True)
    
    # ========== TAB 6: Channel Summary ==========
    with tab6:
        st.header("Channel-wise Performance Summary")
        
        st.info("ℹ️ Replace with your actual Channel Summary Trino query")
        
        # Sample MTD data by channel
        channel_summary = pd.DataFrame({
            'Channel': ['General Trade', 'Enterprise', 'Govt+Transit', 'Oil & Gas', 'Retail MM'],
            'Deployments': [139952, 493, 2413, 4293, 513],
            'Active_Merchants': [5325228, 58650, 49848, 191288, 48014],
            'GMV_Cr': [24482, 1019, 737, 10086, 528],
            'Growth_Pct': [-23, 2, 30, -31, -25]
        })
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Deployments", f"{channel_summary['Deployments'].sum():,.0f}")
        with col2:
            st.metric("Total Active Merchants", f"{channel_summary['Active_Merchants'].sum():,.0f}")
        with col3:
            st.metric("Total GMV (₹ Cr)", f"₹{channel_summary['GMV_Cr'].sum():,.0f}")
        with col4:
            avg_growth = channel_summary['Growth_Pct'].mean()
            st.metric("Avg Growth %", f"{avg_growth:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_bar_chart(channel_summary, 'Channel', 'GMV_Cr', 
                         '💰 GMV by Channel (₹ Cr)', '#bcbd22')
        
        with col2:
            plot_bar_chart(channel_summary, 'Channel', 'Deployments', 
                         '📦 Deployments by Channel', '#ff9896')
        
        # Detailed table
        st.subheader("📊 Detailed Channel Metrics")
        st.dataframe(
            channel_summary.style.format({
                'Deployments': '{:,.0f}',
                'Active_Merchants': '{:,.0f}',
                'GMV_Cr': '₹{:,.2f}',
                'Growth_Pct': '{:+.1f}%'
            }).background_gradient(subset=['GMV_Cr'], cmap='RdYlGn'),
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray; padding: 20px;'>
            <p>Business Finance Dashboard v1.0 | Last Data Refresh: {}</p>
            <p>⚠️ Remember to replace sample queries with your actual Trino queries</p>
        </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

# ============================================================================
# APP ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Check authentication
    if not st.session_state['authenticated']:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
