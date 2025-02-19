import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def get_last_week_data(ticker):
    today = datetime.now()
    last_friday = today - timedelta(days=(today.weekday() + 3) % 7)
    last_thursday = last_friday - timedelta(days=1)
    start_date = last_friday - timedelta(days=7)
    
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=last_thursday)
    return df, stock

def get_52_week_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    return df

def get_company_info(stock):
    info = stock.info
    return {
        'Company Name': info.get('longName', 'N/A'),
        'Sector': info.get('sector', 'N/A'),
        'Industry': info.get('industry', 'N/A'),
        'Market Cap': f"${info.get('marketCap', 0):,}",
        'P/E Ratio': round(info.get('trailingPE', 0), 2),
        'Dividend Yield': f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A',
        'Average Volume': f"{info.get('averageVolume', 0):,}",
        'Beta': round(info.get('beta', 0), 2)
    }

def display_metric_small(label, value):
    """Custom function to display metrics with smaller font"""
    st.markdown(
        f"""
        <div style="padding: 5px 0px;">
            <span style="color: rgb(125, 125, 125); font-size: 0.8em;">{label}</span><br>
            <span style="color: rgb(185, 185, 185); font-size: 1em; font-weight: bold;">{value}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

def main():
    
    st.title("🔍 Stock Analysis Dashboard")  # Added analysis icon
    st.markdown("#### Darvas Box Theory")
    ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL):", "AAPL").upper()
    
    if ticker:
        try:
            weekly_data, stock = get_last_week_data(ticker)
            
            # Display company information with smaller font
            st.markdown("#### Company Information")
            company_info = get_company_info(stock)
            
            # Create two columns for company info
            col1, col2 = st.columns(2)
            
            # Distribute company info across columns with smaller font
            info_items = list(company_info.items())
            with col1:
                for key, value in info_items[:4]:
                    display_metric_small(key, value)
            with col2:
                for key, value in info_items[4:]:
                    display_metric_small(key, value)
            
            st.markdown("---")  # Add a separator
            
            # Display last week's data
            st.subheader("Last Week's Trading Data")
            
            display_df = weekly_data[['Open', 'High', 'Low', 'Close']].round(2)
            
            week_high = display_df['High'].max()
            week_low = display_df['Low'].min()
            
            def highlight_high_low(val):
                if val == week_high:
                    return 'background-color: lightgreen'
                elif val == week_low:
                    return 'background-color: lightcoral'
                return ''
            
            st.dataframe(display_df.style.applymap(highlight_high_low))
            
            # Calculate and display GTT Buy Price and Target
            gtt_buy_price = round(week_high * 1.005, 2)
            target_price = round(gtt_buy_price * 1.045, 2)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("GTT Order Buy Price", f"${gtt_buy_price}")
            with col2:
                st.metric("Target Price", f"${target_price}")
            
            # Get and display 52-week data
            yearly_data = get_52_week_data(ticker)
            
            high_52 = yearly_data['High'].max()
            low_52 = yearly_data['Low'].min()
            high_52_date = yearly_data['High'].idxmax()
            low_52_date = yearly_data['Low'].idxmin()
            
            st.subheader("52-Week Analysis")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.metric("52-Week High", f"${high_52:.2f}")
                st.caption(f"Date: {high_52_date.strftime('%Y-%m-%d')}")
            
            with col2:
                st.metric("52-Week Low", f"${low_52:.2f}")
                st.caption(f"Date: {low_52_date.strftime('%Y-%m-%d')}")
            
            with col3:
                green_signal = low_52_date > high_52_date
                signal = "🟢" if green_signal else "🔴"
                st.metric("Signal",f"{signal}")
                #st.markdown(f"### Signal\n{signal}")
                if green_signal:
                    st.caption("Low is more recent")
                else:
                    st.caption("High is more recent")
            
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            st.info("Please check if the ticker symbol is valid and try again.")

if __name__ == "__main__":
    main()