# queries.py
# Add your actual Trino SQL queries here

"""
IMPORTANT: Replace these template queries with your actual Trino queries
that match the structure of your MIS report.
"""

# ============================================================================
# SOUND BOX QUERIES
# ============================================================================

SOUNDBOX_DAILY = """
-- Sound Box Daily Metrics
-- Replace with your actual table and column names
SELECT 
    deployment_date,
    channel,
    deployments,
    general_trade_diy,
    general_trade_non_diy,
    net_device_addition,
    deployed_base,
    deployment_new_pct,
    deployment_refurbished_pct,
    active_merchant,
    active_merchant_pct,
    broadcasting_device,
    broadcasting_device_pct,
    replacement_devices,
    pickup_devices
FROM soundbox_daily_metrics
WHERE deployment_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY deployment_date DESC
"""

SOUNDBOX_MTD = """
-- Sound Box MTD Summary
SELECT 
    channel,
    SUM(deployments) as mtd_deployments,
    SUM(net_device_addition) as mtd_net_addition,
    MAX(deployed_base) as current_deployed_base,
    AVG(active_merchant_pct) as avg_active_merchant_pct,
    SUM(replacement_devices) as total_replacements,
    SUM(pickup_devices) as total_pickups
FROM soundbox_daily_metrics
WHERE deployment_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY channel
"""

# ============================================================================
# EDC QUERIES
# ============================================================================

EDC_DAILY = """
-- EDC Daily Metrics
SELECT 
    deployment_date,
    channel,
    deployments,
    general_trade_diy,
    general_trade_edc,
    general_trade_so,
    net_device_addition,
    deployed_base,
    deployment_new_pct,
    deployment_refurbished_pct,
    active_merchant,
    active_merchant_pct,
    engaged_merchant,
    engaged_merchant_pct,
    multi_tid_devices,
    pickup_devices,
    replacements
FROM edc_daily_metrics
WHERE deployment_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY deployment_date DESC
"""

EDC_GMV_TXN = """
-- EDC GMV & Transaction Metrics
SELECT 
    transaction_date,
    channel,
    edc_nonpos_gmv_cr,
    cc_gmv_cr,
    dc_gmv_cr,
    emi_gmv_cr,
    bank_gmv_cr,
    brand_gmv_cr,
    brand_fs_gmv_cr,
    upi_gmv_cr,
    upi_above_2k_gmv_cr,
    upi_below_2k_gmv_cr,
    upi_cc_gmv_cr,
    edc_pos_gmv_cr,
    total_gmv_cr
FROM edc_gmv_daily
WHERE transaction_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY transaction_date DESC
"""

EDC_RENTAL = """
-- EDC Rental Collection
SELECT 
    collection_date,
    channel,
    rental_collectable_devices,
    rental_collected_devices,
    rental_collectable_current_month_cr,
    rental_collected_total_amount_cr,
    collection_rate_pct
FROM edc_rental_collection
WHERE collection_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY collection_date DESC
"""

# ============================================================================
# QR CODE QUERIES
# ============================================================================

QR_DAILY = """
-- QR Code Daily Metrics
SELECT 
    onboarding_date,
    channel,
    onboarding,
    diy_onboarding,
    non_diy_onboarding,
    active_merchant,
    active_merchant_pct,
    engaged_merchant,
    gmv_cr,
    gmv_per_active_merchant
FROM qr_daily_metrics
WHERE onboarding_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY onboarding_date DESC
"""

QR_DYNAMIC = """
-- Dynamic QR Metrics
SELECT 
    date,
    channel,
    onboarding,
    active_merchant,
    active_merchant_pct,
    gmv_cr,
    gmv_per_merchant,
    transactions_mn
FROM dynamic_qr_metrics
WHERE date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY date DESC
"""

# ============================================================================
# UPI TRANSACTION QUERIES
# ============================================================================

UPI_DAILY = """
-- UPI Daily Transactions
SELECT 
    txn_date,
    channel,
    upi_gmv_cr,
    upi_txn_mn,
    upi_below_2000_gmv_cr,
    upi_above_2000_gmv_cr,
    upi_below_2000_txn_mn,
    upi_above_2000_txn_mn,
    cc_upi_gmv_cr,
    cc_upi_txn_mn,
    creditline_upi_gmv_cr,
    creditline_upi_txn_mn
FROM upi_daily_transactions
WHERE txn_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY txn_date DESC
"""

UPI_CHANNEL_SUMMARY = """
-- UPI Channel Summary MTD
SELECT 
    channel,
    SUM(upi_gmv_cr) as total_upi_gmv_cr,
    SUM(upi_txn_mn) as total_upi_txn_mn,
    AVG(upi_gmv_cr / upi_txn_mn) as avg_ticket_size,
    SUM(upi_below_2000_gmv_cr) as total_small_ticket_gmv,
    SUM(upi_above_2000_gmv_cr) as total_large_ticket_gmv
FROM upi_daily_transactions
WHERE txn_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY channel
"""

# ============================================================================
# RENTAL COLLECTION QUERIES
# ============================================================================

RENTAL_SOUNDBOX = """
-- Sound Box Rental Collection
SELECT 
    collection_date,
    channel,
    rental_collectable_merchants,
    rental_collected_merchants,
    rental_collectable_current_month_cr,
    rental_collected_total_amount_cr,
    collection_rate_pct
FROM soundbox_rental_collection
WHERE collection_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY collection_date DESC
"""

RENTAL_EDC = """
-- EDC Rental Collection
SELECT 
    collection_date,
    channel,
    rental_collectable_devices,
    rental_collected_devices,
    rental_collectable_current_month_cr,
    rental_collected_total_amount_cr,
    collection_rate_pct
FROM edc_rental_collection
WHERE collection_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY collection_date DESC
"""

# ============================================================================
# OVERALL SUMMARY QUERIES
# ============================================================================

OVERALL_DAILY_SUMMARY = """
-- Overall Daily Summary
SELECT 
    report_date,
    SUM(total_deployments) as total_deployments,
    SUM(total_active_merchants) as total_active_merchants,
    SUM(total_gmv_cr) as total_gmv_cr,
    SUM(total_transactions_mn) as total_transactions_mn,
    AVG(active_merchant_pct) as avg_active_merchant_pct
FROM daily_summary
WHERE report_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY report_date
ORDER BY report_date DESC
"""

CHANNEL_MTD_SUMMARY = """
-- Channel-wise MTD Summary
SELECT 
    channel,
    SUM(deployments) as total_deployments,
    SUM(active_merchants) as total_active_merchants,
    SUM(gmv_cr) as total_gmv_cr,
    SUM(transactions_mn) as total_transactions_mn,
    AVG(growth_pct) as avg_growth_pct,
    SUM(rental_collected_cr) as total_rental_collected
FROM channel_daily_summary
WHERE report_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY channel
ORDER BY total_gmv_cr DESC
"""

YESTERDAY_VS_LAST_7_DAYS = """
-- Yesterday vs Last 7 Days Average Comparison
SELECT 
    channel,
    yesterday_deployments,
    last_7_days_avg_deployments,
    yesterday_gmv_cr,
    last_7_days_avg_gmv_cr,
    yesterday_active_merchants,
    last_7_days_avg_active_merchants,
    growth_pct
FROM yesterday_vs_last_7_comparison
ORDER BY channel
"""

MTD_VS_LMTD_COMPARISON = """
-- MTD vs LMTD (Last Month To Date) Comparison
SELECT 
    channel,
    mtd_deployments,
    lmtd_deployments,
    mtd_vs_lmtd_deployment_growth_pct,
    mtd_gmv_cr,
    lmtd_gmv_cr,
    mtd_vs_lmtd_gmv_growth_pct,
    mtd_active_merchants,
    lmtd_active_merchants,
    mtd_vs_lmtd_merchant_growth_pct
FROM mtd_vs_lmtd_comparison
ORDER BY channel
"""

# ============================================================================
# HELPER FUNCTION TO GET ALL QUERIES
# ============================================================================

def get_all_queries():
    """Return dictionary of all queries"""
    return {
        # Sound Box
        'soundbox_daily': SOUNDBOX_DAILY,
        'soundbox_mtd': SOUNDBOX_MTD,
        
        # EDC
        'edc_daily': EDC_DAILY,
        'edc_gmv_txn': EDC_GMV_TXN,
        'edc_rental': EDC_RENTAL,
        
        # QR
        'qr_daily': QR_DAILY,
        'qr_dynamic': QR_DYNAMIC,
        
        # UPI
        'upi_daily': UPI_DAILY,
        'upi_channel_summary': UPI_CHANNEL_SUMMARY,
        
        # Rental
        'rental_soundbox': RENTAL_SOUNDBOX,
        'rental_edc': RENTAL_EDC,
        
        # Summary
        'overall_daily_summary': OVERALL_DAILY_SUMMARY,
        'channel_mtd_summary': CHANNEL_MTD_SUMMARY,
        'yesterday_vs_last_7': YESTERDAY_VS_LAST_7_DAYS,
        'mtd_vs_lmtd': MTD_VS_LMTD_COMPARISON,
    }

# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

"""
HOW TO USE THIS FILE:

1. Replace the template queries above with your actual Trino queries
2. Make sure column names match your database schema
3. Test each query individually in Trino first
4. Import into app.py:
   
   from queries import get_all_queries
   
   QUERIES = get_all_queries()
   df = execute_query(QUERIES['soundbox_daily'])

5. Update the query names in app.py to match the keys above
"""
