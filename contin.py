import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

# Configure the page
st.set_page_config(
    page_title="Delivery Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Delivery Analytics Dashboard")
st.markdown("---")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

def parse_date_column(df, column_name):
    """Parse date column with multiple possible formats"""
    if column_name not in df.columns:
        return df
    
    # Try multiple date formats
    formats_to_try = [
        '%m-%d-%Y %H:%M',  # MM-DD-YYYY HH:MM
        '%m-%d-%Y',        # MM-DD-YYYY
        '%d-%m-%Y %H:%M',  # DD-MM-YYYY HH:MM
        '%d-%m-%Y',        # DD-MM-YYYY
        '%Y-%m-%d %H:%M',  # YYYY-MM-DD HH:MM
        '%Y-%m-%d',        # YYYY-MM-DD
    ]
    
    for fmt in formats_to_try:
        try:
            parsed_dates = pd.to_datetime(df[column_name], format=fmt, errors='coerce')
            # Check if any dates were successfully parsed
            success_rate = (1 - parsed_dates.isna().mean()) * 100
            if success_rate > 50:  # If more than 50% parsed successfully
                df[column_name] = parsed_dates
                break
        except:
            continue
    else:
        # If none of the specific formats work, use pandas default parsing
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
    
    return df

def calculate_time_durations(df):
    """Calculate time durations from Picked on to Delivered on"""
    # Parse Delivered on column
    df = parse_date_column(df, 'Delivered on')
    
    # Calculate time difference in hours
    mask = (~df['Picked on'].isna()) & (~df['Delivered on'].isna())
    df.loc[mask, 'delivery_duration_hrs'] = (
        df.loc[mask, 'Delivered on'] - df.loc[mask, 'Picked on']
    ).dt.total_seconds() / 3600
    
    # Categorize into new time buckets (hourly up to 12 hours, then 12+)
    conditions = [
        df['delivery_duration_hrs'] <= 1,
        (df['delivery_duration_hrs'] > 1) & (df['delivery_duration_hrs'] <= 2),
        (df['delivery_duration_hrs'] > 2) & (df['delivery_duration_hrs'] <= 3),
        (df['delivery_duration_hrs'] > 3) & (df['delivery_duration_hrs'] <= 4),
        (df['delivery_duration_hrs'] > 4) & (df['delivery_duration_hrs'] <= 5),
        (df['delivery_duration_hrs'] > 5) & (df['delivery_duration_hrs'] <= 6),
        (df['delivery_duration_hrs'] > 6) & (df['delivery_duration_hrs'] <= 7),
        (df['delivery_duration_hrs'] > 7) & (df['delivery_duration_hrs'] <= 8),
        (df['delivery_duration_hrs'] > 8) & (df['delivery_duration_hrs'] <= 9),
        (df['delivery_duration_hrs'] > 9) & (df['delivery_duration_hrs'] <= 10),
        (df['delivery_duration_hrs'] > 10) & (df['delivery_duration_hrs'] <= 11),
        (df['delivery_duration_hrs'] > 11) & (df['delivery_duration_hrs'] <= 12),
        df['delivery_duration_hrs'] > 12
    ]
    
    choices = [
        '0-1Hrs', '1-2Hrs', '2-3Hrs', '3-4Hrs', '4-5Hrs', '5-6Hrs',
        '6-7Hrs', '7-8Hrs', '8-9Hrs', '9-10Hrs', '10-11Hrs', '11-12Hrs', '12+Hrs'
    ]
    df['delivery_time_bucket'] = np.select(conditions, choices, default='Unknown')
    
    return df

def create_daily_summary_with_durations(df, tab_name):
    """Create daily summary with time duration analysis"""
    if not df.empty:
        # Extract date and time components
        df['Picked Date'] = df['Picked on'].dt.date
        df['Picked Hour'] = df['Picked on'].dt.hour
        
        # Generate all dates from September 20th to October 10th
        current_year = int(df['Picked on'].dt.year.max())
        september_start = pd.Timestamp(f'{current_year}-09-20')
        october_end = pd.Timestamp(f'{current_year}-10-10')
        
        all_dates = pd.date_range(start=september_start, end=october_end, freq='D')
        
        # Group by date and calculate metrics
        daily_summary = []
        
        for single_date in all_dates:
            date_str = single_date.strftime('%m-%d')
            day_data = df[df['Picked Date'] == single_date.date()]
            total = len(day_data)
            
            if total == 0:
                # Skip dates with no data
                continue
            
            # Morning shift (12AM to 11:59AM)
            morning_shift = len(day_data[
                (day_data['Picked Hour'] >= 0) & 
                (day_data['Picked Hour'] < 12)
            ])
            
            # Afternoon slot (12PM to 11:59PM)
            afternoon_slot = len(day_data[
                (day_data['Picked Hour'] >= 12)
            ])
            
            # Time duration buckets with new hourly breakdown
            time_buckets = day_data['delivery_time_bucket'].value_counts()
            hrs_0_1 = time_buckets.get('0-1Hrs', 0)
            hrs_1_2 = time_buckets.get('1-2Hrs', 0)
            hrs_2_3 = time_buckets.get('2-3Hrs', 0)
            hrs_3_4 = time_buckets.get('3-4Hrs', 0)
            hrs_4_5 = time_buckets.get('4-5Hrs', 0)
            hrs_5_6 = time_buckets.get('5-6Hrs', 0)
            hrs_6_7 = time_buckets.get('6-7Hrs', 0)
            hrs_7_8 = time_buckets.get('7-8Hrs', 0)
            hrs_8_9 = time_buckets.get('8-9Hrs', 0)
            hrs_9_10 = time_buckets.get('9-10Hrs', 0)
            hrs_10_11 = time_buckets.get('10-11Hrs', 0)
            hrs_11_12 = time_buckets.get('11-12Hrs', 0)
            hrs_12_plus = time_buckets.get('12+Hrs', 0)
            
            # Calculate average delivery time
            avg_delivery_time = day_data['delivery_duration_hrs'].mean()
            
            # Calculate percentages
            morning_pct = round((morning_shift / total * 100) if total > 0 else 0, 0)
            afternoon_pct = round((afternoon_slot / total * 100) if total > 0 else 0, 0)
            
            daily_summary.append({
                tab_name: date_str,
                'Total': total,
                'Morning shift': morning_shift,
                'Afternoon Slot': afternoon_slot,
                'Morning %': f"{int(morning_pct)}%",
                'Afternoon %': f"{int(afternoon_pct)}%",
                '0-1Hrs': hrs_0_1,
                '1-2Hrs': hrs_1_2,
                '2-3Hrs': hrs_2_3,
                '3-4Hrs': hrs_3_4,
                '4-5Hrs': hrs_4_5,
                '5-6Hrs': hrs_5_6,
                '6-7Hrs': hrs_6_7,
                '7-8Hrs': hrs_7_8,
                '8-9Hrs': hrs_8_9,
                '9-10Hrs': hrs_9_10,
                '10-11Hrs': hrs_10_11,
                '11-12Hrs': hrs_11_12,
                '12+Hrs': hrs_12_plus,
                'Avg Hrs': round(avg_delivery_time, 1) if not np.isnan(avg_delivery_time) else 0
            })
        
        # Calculate totals
        if daily_summary:
            total_orders = sum(item['Total'] for item in daily_summary)
            total_morning = sum(item['Morning shift'] for item in daily_summary)
            total_afternoon = sum(item['Afternoon Slot'] for item in daily_summary)
            
            # Calculate totals for time buckets
            total_0_1 = sum(item['0-1Hrs'] for item in daily_summary)
            total_1_2 = sum(item['1-2Hrs'] for item in daily_summary)
            total_2_3 = sum(item['2-3Hrs'] for item in daily_summary)
            total_3_4 = sum(item['3-4Hrs'] for item in daily_summary)
            total_4_5 = sum(item['4-5Hrs'] for item in daily_summary)
            total_5_6 = sum(item['5-6Hrs'] for item in daily_summary)
            total_6_7 = sum(item['6-7Hrs'] for item in daily_summary)
            total_7_8 = sum(item['7-8Hrs'] for item in daily_summary)
            total_8_9 = sum(item['8-9Hrs'] for item in daily_summary)
            total_9_10 = sum(item['9-10Hrs'] for item in daily_summary)
            total_10_11 = sum(item['10-11Hrs'] for item in daily_summary)
            total_11_12 = sum(item['11-12Hrs'] for item in daily_summary)
            total_12_plus = sum(item['12+Hrs'] for item in daily_summary)
            
            # Calculate overall average
            all_delivery_times = df['delivery_duration_hrs'].dropna()
            overall_avg = round(all_delivery_times.mean(), 1) if len(all_delivery_times) > 0 else 0
            
            total_summary = {
                tab_name: 'TOTAL',
                'Total': total_orders,
                'Morning shift': total_morning,
                'Afternoon Slot': total_afternoon,
                'Morning %': f"{int(round((total_morning / total_orders * 100) if total_orders > 0 else 0, 0))}%",
                'Afternoon %': f"{int(round((total_afternoon / total_orders * 100) if total_orders > 0 else 0, 0))}%",
                '0-1Hrs': total_0_1,
                '1-2Hrs': total_1_2,
                '2-3Hrs': total_2_3,
                '3-4Hrs': total_3_4,
                '4-5Hrs': total_4_5,
                '5-6Hrs': total_5_6,
                '6-7Hrs': total_6_7,
                '7-8Hrs': total_7_8,
                '8-9Hrs': total_8_9,
                '9-10Hrs': total_9_10,
                '10-11Hrs': total_10_11,
                '11-12Hrs': total_11_12,
                '12+Hrs': total_12_plus,
                'Avg Hrs': overall_avg
            }
            
            return daily_summary, total_summary
        else:
            return [], {}
    else:
        return [], {}

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Parse Picked on column with multiple format attempts
        df = parse_date_column(df, 'Picked on')
        
        # Create only the two tabs you want
        tab1, tab2 = st.tabs([
            "DC Analysis - WESTSIDE UNIT OF TRENT LIMITED", 
            "Store Analysis - All Pickup Hubs (Excluding WD27)"
        ])
        
        with tab1:
            # Filter for WESTSIDE UNIT OF TRENT LIMITED and WD27
            dc_df = df.copy()
            
            # Apply filters
            if 'Customer' in dc_df.columns:
                dc_df = dc_df[dc_df['Customer'] == 'WESTSIDE UNIT OF TRENT LIMITED']
            
            if 'Pickup Hub' in dc_df.columns:
                dc_df = dc_df[dc_df['Pickup Hub'] == 'WD27']
            
            # Set date range: September 20th to October 10th
            if not dc_df.empty and not dc_df['Picked on'].isna().all():
                # Filter for dates from September 20th to October 10th
                current_year = int(dc_df['Picked on'].dt.year.max())
                september_start = pd.Timestamp(f'{current_year}-09-20')
                october_end = pd.Timestamp(f'{current_year}-10-10')
                
                dc_df = dc_df[
                    (dc_df['Picked on'] >= september_start) & 
                    (dc_df['Picked on'] <= october_end + timedelta(days=1))
                ]
                
                if not dc_df.empty:
                    # Calculate time durations
                    dc_df = calculate_time_durations(dc_df)
                    
                    # Create summary with durations
                    daily_summary, total_summary = create_daily_summary_with_durations(dc_df, 'DC')
                    
                    if daily_summary:
                        # Display the Daily Summary table
                        display_df = pd.DataFrame(daily_summary + [total_summary])
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.warning("No data found for the date range!")
                    
                else:
                    st.warning("No data found after date filtering!")
            else:
                st.warning("No data found for the specified customer and hub filters!")
        
        with tab2:
            # Filter for WESTSIDE UNIT OF TRENT LIMITED and EXCLUDE WD27
            store_df = df.copy()
            
            # Apply filters
            if 'Customer' in store_df.columns:
                store_df = store_df[store_df['Customer'] == 'WESTSIDE UNIT OF TRENT LIMITED']
            
            if 'Pickup Hub' in store_df.columns:
                store_df = store_df[store_df['Pickup Hub'] != 'WD27']
            
            # Set date range: September 20th to October 10th
            if not store_df.empty and not store_df['Picked on'].isna().all():
                # Filter for dates from September 20th to October 10th
                current_year = int(store_df['Picked on'].dt.year.max())
                september_start = pd.Timestamp(f'{current_year}-09-20')
                october_end = pd.Timestamp(f'{current_year}-10-10')
                
                store_df = store_df[
                    (store_df['Picked on'] >= september_start) & 
                    (store_df['Picked on'] <= october_end + timedelta(days=1))
                ]
                
                if not store_df.empty:
                    # Calculate time durations
                    store_df = calculate_time_durations(store_df)
                    
                    # Create summary with durations
                    daily_summary, total_summary = create_daily_summary_with_durations(store_df, 'Store')
                    
                    if daily_summary:
                        # Display the Daily Summary table
                        display_df = pd.DataFrame(daily_summary + [total_summary])
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.warning("No data found for the date range!")
                    
                else:
                    st.warning("No data found after date filtering!")
            else:
                st.warning("No data found for the specified customer and hub filters!")
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    st.info("Please upload a CSV file to get started")
