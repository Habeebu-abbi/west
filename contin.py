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

def calculate_time_durations(df):
    """Calculate time durations from Picked on to Delivered on"""
    # Convert Delivered on to datetime
    df['Delivered on'] = pd.to_datetime(df['Delivered on'], format='%m-%d-%Y %H:%M', errors='coerce')
    
    # Calculate time difference in hours
    df['delivery_duration_hrs'] = (df['Delivered on'] - df['Picked on']).dt.total_seconds() / 3600
    
    # Categorize into time buckets
    conditions = [
        df['delivery_duration_hrs'] <= 2,
        (df['delivery_duration_hrs'] > 2) & (df['delivery_duration_hrs'] <= 4),
        (df['delivery_duration_hrs'] > 4) & (df['delivery_duration_hrs'] <= 6),
        (df['delivery_duration_hrs'] > 6) & (df['delivery_duration_hrs'] <= 12),
        (df['delivery_duration_hrs'] > 12) & (df['delivery_duration_hrs'] <= 24),
        (df['delivery_duration_hrs'] > 24) & (df['delivery_duration_hrs'] <= 48),
        df['delivery_duration_hrs'] > 48
    ]
    
    choices = ['0-2Hrs', '2-4Hrs', '4-6Hrs', '6-12Hrs', '12-24Hrs', '24-48Hrs', '48+Hrs']
    df['delivery_time_bucket'] = np.select(conditions, choices, default='Unknown')
    
    return df

def create_daily_summary_with_durations(df, tab_name):
    """Create daily summary with time duration analysis"""
    if not df.empty:
        # Extract date and time components
        df['Picked Date'] = df['Picked on'].dt.date
        df['Picked Hour'] = df['Picked on'].dt.hour
        
        # Generate all dates from October 1st to today
        current_year = df['Picked on'].dt.year.max()
        october_start = pd.Timestamp(f'{current_year}-10-01')
        today = pd.Timestamp(date.today())
        
        # If today is before October, adjust the year
        if today.month < 10:
            october_start = pd.Timestamp(f'{current_year-1}-10-01')
        
        all_dates = pd.date_range(start=october_start, end=today, freq='D')
        
        # Group by date and calculate metrics
        daily_summary = []
        
        for single_date in all_dates:
            date_str = single_date.strftime('%m-%d')
            day_data = df[df['Picked Date'] == single_date.date()]
            total = len(day_data)
            
            # Morning shift (12AM to 11:59AM)
            morning_shift = len(day_data[
                (day_data['Picked Hour'] >= 0) & 
                (day_data['Picked Hour'] < 12)
            ])
            
            # Afternoon slot (12PM to 11:59PM)
            afternoon_slot = len(day_data[
                (day_data['Picked Hour'] >= 12)
            ])
            
            # Time duration buckets
            time_buckets = day_data['delivery_time_bucket'].value_counts()
            hrs_0_2 = time_buckets.get('0-2Hrs', 0)
            hrs_2_4 = time_buckets.get('2-4Hrs', 0)
            hrs_4_6 = time_buckets.get('4-6Hrs', 0)
            hrs_6_12 = time_buckets.get('6-12Hrs', 0)
            hrs_12_24 = time_buckets.get('12-24Hrs', 0)
            hrs_24_48 = time_buckets.get('24-48Hrs', 0)
            hrs_48_plus = time_buckets.get('48+Hrs', 0)
            
            # Calculate average delivery time
            avg_delivery_time = day_data['delivery_duration_hrs'].mean()
            
            # Calculate percentages
            morning_pct = round((morning_shift / total * 100) if total > 0 else 0, 0)
            evening_pct = round((afternoon_slot / total * 100) if total > 0 else 0, 0)
            
            daily_summary.append({
                tab_name: date_str,
                'Total': total,
                'Morning shift': morning_shift,
                'Afternoon Slot': afternoon_slot,
                'Morning %': f"{int(morning_pct)}%",
                'Evening %': f"{int(evening_pct)}%",
                '0-2Hrs': hrs_0_2,
                '2-4Hrs': hrs_2_4,
                '4-6Hrs': hrs_4_6,
                '6-12Hrs': hrs_6_12,
                '12-24Hrs': hrs_12_24,
                '24-48Hrs': hrs_24_48,
                '48+Hrs': hrs_48_plus,
                'Avg Hrs': round(avg_delivery_time, 1) if not np.isnan(avg_delivery_time) else 0
            })
        
        # Calculate totals
        total_orders = sum(item['Total'] for item in daily_summary)
        total_morning = sum(item['Morning shift'] for item in daily_summary)
        total_afternoon = sum(item['Afternoon Slot'] for item in daily_summary)
        
        # Calculate totals for time buckets
        total_0_2 = sum(item['0-2Hrs'] for item in daily_summary)
        total_2_4 = sum(item['2-4Hrs'] for item in daily_summary)
        total_4_6 = sum(item['4-6Hrs'] for item in daily_summary)
        total_6_12 = sum(item['6-12Hrs'] for item in daily_summary)
        total_12_24 = sum(item['12-24Hrs'] for item in daily_summary)
        total_24_48 = sum(item['24-48Hrs'] for item in daily_summary)
        total_48_plus = sum(item['48+Hrs'] for item in daily_summary)
        
        # Calculate overall average
        all_delivery_times = df['delivery_duration_hrs'].dropna()
        overall_avg = round(all_delivery_times.mean(), 1) if len(all_delivery_times) > 0 else 0
        
        total_summary = {
            tab_name: 'TOTAL',
            'Total': total_orders,
            'Morning shift': total_morning,
            'Afternoon Slot': total_afternoon,
            'Morning %': f"{int(round((total_morning / total_orders * 100) if total_orders > 0 else 0, 0))}%",
            'Evening %': f"{int(round((total_afternoon / total_orders * 100) if total_orders > 0 else 0, 0))}%",
            '0-2Hrs': total_0_2,
            '2-4Hrs': total_2_4,
            '4-6Hrs': total_4_6,
            '6-12Hrs': total_6_12,
            '12-24Hrs': total_12_24,
            '24-48Hrs': total_24_48,
            '48+Hrs': total_48_plus,
            'Avg Hrs': overall_avg
        }
        
        return daily_summary, total_summary
    else:
        return [], {}

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Convert 'Picked on' column to datetime with MM-DD-YYYY format
        df['Picked on'] = pd.to_datetime(df['Picked on'], format='%m-%d-%Y %H:%M', errors='coerce')
        
        # Create tabs
        tab1, tab2 = st.tabs(["DC Analysis", "Store Analysis"])
        
        with tab1:
            st.header("DC Analysis - WESTSIDE UNIT OF TRENT LIMITED")
            
            # Filter for WESTSIDE UNIT OF TRENT LIMITED and WD27
            dc_df = df.copy()
            
            # Apply filters
            if 'Customer' in dc_df.columns:
                dc_df = dc_df[dc_df['Customer'].str.contains('WESTSIDE', na=False)]
            
            if 'Pickup Hub' in dc_df.columns:
                dc_df = dc_df[dc_df['Pickup Hub'] == 'WD27']
            
            # Set date range: October 1st to today
            if not dc_df.empty:
                current_year = dc_df['Picked on'].dt.year.max()
                october_start = pd.Timestamp(f'{current_year}-10-01')
                today = pd.Timestamp(date.today())
                
                # If today is before October, adjust the year
                if today.month < 10:
                    october_start = pd.Timestamp(f'{current_year-1}-10-01')
                
                # Filter for dates from October 1st to today
                dc_df = dc_df[
                    (dc_df['Picked on'] >= october_start) & 
                    (dc_df['Picked on'] <= today + timedelta(days=1))
                ]
                
                if not dc_df.empty:
                    # Calculate time durations
                    dc_df = calculate_time_durations(dc_df)
                    
                    # Create summary with durations
                    daily_summary, total_summary = create_daily_summary_with_durations(dc_df, 'DC')
                    
                    # Display the Daily Summary table
                    display_df = pd.DataFrame(daily_summary + [total_summary])
                    st.dataframe(display_df, use_container_width=True)
                    
                else:
                    st.warning("No data found after date filtering!")
            else:
                st.warning("No data found for the specified customer and hub filters!")
        
        with tab2:
            st.header("Store Analysis - All Pickup Hubs (Excluding WD27)")
            
            # Filter for WESTSIDE UNIT OF TRENT LIMITED and EXCLUDE WD27
            store_df = df.copy()
            
            # Apply filters
            if 'Customer' in store_df.columns:
                store_df = store_df[store_df['Customer'].str.contains('WESTSIDE', na=False)]
            
            if 'Pickup Hub' in store_df.columns:
                store_df = store_df[store_df['Pickup Hub'] != 'WD27']
            
            # Set date range: October 1st to today
            if not store_df.empty:
                current_year = store_df['Picked on'].dt.year.max()
                october_start = pd.Timestamp(f'{current_year}-10-01')
                today = pd.Timestamp(date.today())
                
                # If today is before October, adjust the year
                if today.month < 10:
                    october_start = pd.Timestamp(f'{current_year-1}-10-01')
                
                # Filter for dates from October 1st to today
                store_df = store_df[
                    (store_df['Picked on'] >= october_start) & 
                    (store_df['Picked on'] <= today + timedelta(days=1))
                ]
                
                if not store_df.empty:
                    # Calculate time durations
                    store_df = calculate_time_durations(store_df)
                    
                    # Create summary with durations
                    daily_summary, total_summary = create_daily_summary_with_durations(store_df, 'Store')
                    
                    # Display the Daily Summary table
                    display_df = pd.DataFrame(daily_summary + [total_summary])
                    st.dataframe(display_df, use_container_width=True)
                    
                else:
                    st.warning("No data found after date filtering!")
            else:
                st.warning("No data found for the specified customer and hub filters!")
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    st.info("Please upload a CSV file to get started")
