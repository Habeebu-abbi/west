import streamlit as st
import pandas as pd
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

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Create tabs
        tab1, tab2 = st.tabs(["DC Analysis", "Store Analysis"])
        
        with tab1:
            st.header("DC Analysis - WESTSIDE UNIT OF TRENT LIMITED")
            
            # Convert 'Picked on' column to datetime with MM-DD-YYYY format
            df['Picked on'] = pd.to_datetime(df['Picked on'], format='%m-%d-%Y %H:%M', errors='coerce')
            
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
                    # Extract date and time components
                    dc_df['Picked Date'] = dc_df['Picked on'].dt.date
                    dc_df['Picked Hour'] = dc_df['Picked on'].dt.hour
                    
                    # Generate all dates from October 1st to today
                    all_dates = pd.date_range(start=october_start, end=today, freq='D')
                    
                    # Group by date and calculate metrics
                    daily_summary = []
                    
                    for single_date in all_dates:
                        date_str = single_date.strftime('%m-%d')
                        day_data = dc_df[dc_df['Picked Date'] == single_date.date()]
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
                        
                        # Calculate percentages
                        morning_pct = round((morning_shift / total * 100) if total > 0 else 0, 0)
                        evening_pct = round((afternoon_slot / total * 100) if total > 0 else 0, 0)
                        
                        daily_summary.append({
                            'DC': date_str,
                            'Total': total,
                            'Morning shift': morning_shift,
                            'Afternoon Slot': afternoon_slot,
                            'Morning %': f"{int(morning_pct)}%",
                            'Evening %': f"{int(evening_pct)}%"
                        })
                    
                    # Calculate totals
                    total_orders = sum(item['Total'] for item in daily_summary)
                    total_morning = sum(item['Morning shift'] for item in daily_summary)
                    total_afternoon = sum(item['Afternoon Slot'] for item in daily_summary)
                    
                    total_summary = {
                        'DC': 'TOTAL',
                        'Total': total_orders,
                        'Morning shift': total_morning,
                        'Afternoon Slot': total_afternoon,
                        'Morning %': f"{int(round((total_morning / total_orders * 100) if total_orders > 0 else 0, 0))}%",
                        'Evening %': f"{int(round((total_afternoon / total_orders * 100) if total_orders > 0 else 0, 0))}%"
                    }
                    
                    # Display the Daily Summary table
                    display_df = pd.DataFrame(daily_summary + [total_summary])
                    st.dataframe(display_df, use_container_width=True)
                    
                else:
                    st.warning("No data found after date filtering!")
            else:
                st.warning("No data found for the specified customer and hub filters!")
        
        with tab2:
            st.header("Store Analysis - All Pickup Hubs (Excluding WD27)")
            
            # Convert 'Picked on' column to datetime with MM-DD-YYYY format
            df['Picked on'] = pd.to_datetime(df['Picked on'], format='%m-%d-%Y %H:%M', errors='coerce')
            
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
                    # Extract date and time components
                    store_df['Picked Date'] = store_df['Picked on'].dt.date
                    store_df['Picked Hour'] = store_df['Picked on'].dt.hour
                    
                    # Generate all dates from October 1st to today
                    all_dates = pd.date_range(start=october_start, end=today, freq='D')
                    
                    # Group by date and calculate metrics
                    daily_summary = []
                    
                    for single_date in all_dates:
                        date_str = single_date.strftime('%m-%d')
                        day_data = store_df[store_df['Picked Date'] == single_date.date()]
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
                        
                        # Calculate percentages
                        morning_pct = round((morning_shift / total * 100) if total > 0 else 0, 0)
                        evening_pct = round((afternoon_slot / total * 100) if total > 0 else 0, 0)
                        
                        daily_summary.append({
                            'Store': date_str,
                            'Total': total,
                            'Morning shift': morning_shift,
                            'Afternoon Slot': afternoon_slot,
                            'Morning %': f"{int(morning_pct)}%",
                            'Evening %': f"{int(evening_pct)}%"
                        })
                    
                    # Calculate totals
                    total_orders = sum(item['Total'] for item in daily_summary)
                    total_morning = sum(item['Morning shift'] for item in daily_summary)
                    total_afternoon = sum(item['Afternoon Slot'] for item in daily_summary)
                    
                    total_summary = {
                        'Store': 'TOTAL',
                        'Total': total_orders,
                        'Morning shift': total_morning,
                        'Afternoon Slot': total_afternoon,
                        'Morning %': f"{int(round((total_morning / total_orders * 100) if total_orders > 0 else 0, 0))}%",
                        'Evening %': f"{int(round((total_afternoon / total_orders * 100) if total_orders > 0 else 0, 0))}%"
                    }
                    
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