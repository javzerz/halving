import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import datetime, timedelta


pio.templates.default = 'seaborn'
st.set_page_config(layout="wide")

symbol = st.sidebar.text_input('Enter stock symbol:', 'BTC-USD').upper()
second_symbol = st.sidebar.text_input('Enter second stock symbol:', 'ETH-USD').upper()

covid_drop = datetime.strptime('2020-02-20', '%Y-%m-%d')
halving_2020 = datetime.strptime('2020-05-11', '%Y-%m-%d')
halving_2024 = datetime.strptime('2024-04-19', '%Y-%m-%d')

months_options = [1, 2, 3, 6, 9, 12, 24, 36]
months_delta = st.sidebar.selectbox('Months around Halving', options=months_options, index=months_options.index(24))  

# Define a fixed date range for time_period2
start_date = halving_2020 - timedelta(days=30*months_delta)
end_date = halving_2020 + timedelta(days=30*months_delta)

start_date_2024 = halving_2024 - timedelta(days=30*months_delta)
end_date_2024 = halving_2024 + timedelta(days=30*3)


if symbol and second_symbol:
    
    ticker = yf.Ticker(symbol)
    second_ticker = yf.Ticker(second_symbol)
    hist2 = ticker.history(start=start_date, end=end_date)
    hist3 = second_ticker.history(start=start_date, end=end_date)
    hist_2024_1 = ticker.history(start=start_date_2024, end=end_date_2024)
    hist_2024_2 = second_ticker.history(start=start_date_2024, end=end_date_2024)

    
    if not hist2.empty and not hist3.empty:
        # Prepare data to be displayed in charts
        hist2 = hist2.reset_index()
        hist3 = hist3.reset_index()
        hist_2024_1 = hist_2024_1.reset_index()
        hist_2024_2 = hist_2024_2.reset_index()

        for i in ['Open', 'High', 'Close', 'Low']: 
            hist2[i] = hist2[i].astype(float)
            hist3[i] = hist3[i].astype(float)
            hist_2024_1[i] = hist_2024_1[i].astype(float)
            hist_2024_2[i] = hist_2024_2[i].astype(float)

        fig2 = go.Figure()

        # Add traces for both stocks
        fig2.add_trace(go.Scatter(x=hist2['Date'], y=hist2['Close'], mode='lines', name=f'{symbol}'))
        fig2.add_trace(go.Scatter(x=hist3['Date'], y=hist3['Close'], mode='lines', name=f'{second_symbol}', yaxis='y2'))

        # Add vertical line for the halving event
        fig2.add_vline(x=halving_2020.strftime('%Y-%m-%d'), line_width=2, line_dash="dash", line_color="white", name="Halving", showlegend=True)
        fig2.add_vline(x=covid_drop.strftime('%Y-%m-%d'), line_width=2, line_dash="dash", line_color="red", name="cov_crash", showlegend=True)

        fig2.update_layout(
        	height=600,
            title='Last Halving, May 2020',
            plot_bgcolor='rgba(211, 211, 211, 0.05)',
            xaxis=dict(
                domain=[0.05, 0.95],
                type='date',
                tickformat='%b %Y',
                rangeslider_visible=True,
                range=[start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            ),
            yaxis=dict(title=f'{symbol} USD'),
            yaxis2=dict(
                title=f'{second_symbol} USD',
                showgrid=False,
                overlaying='y',
                side='right'
            )
        )



        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=hist_2024_1['Date'], y=hist_2024_1['Close'], mode='lines', name=f'{symbol}'))
        fig3.add_trace(go.Scatter(x=hist_2024_2['Date'], y=hist_2024_2['Close'], mode='lines', name=f'{second_symbol}', yaxis='y2'))
        fig3.add_vline(x=halving_2024.strftime('%Y-%m-%d'), line_width=2, line_dash="dash", line_color="white", name="Halving", showlegend=True)
        fig3.update_layout(
        		height=600,
	            title='Current Halving, April 2024',
	            plot_bgcolor='rgba(211, 211, 211, 0.05)',
	            xaxis=dict(
	                domain=[0.05, 0.95],
	                type='date',
	                tickformat='%b %Y',
	                rangeslider_visible=True,
	                range=[start_date_2024.strftime('%Y-%m-%d'), end_date_2024.strftime('%Y-%m-%d')]
	            ),
	            yaxis=dict(title=f'{symbol} USD'),
	            yaxis2=dict(
	                title=f'{second_symbol} USD',
	                showgrid=False,
	                overlaying='y',
	                side='right'
	            )
	        )


        # show charts

        fig3.update_xaxes(showgrid=True, gridwidth=1)

        # **********shown********
        st.plotly_chart(fig3, use_container_width=True)

        fig2.update_xaxes(showgrid=True, gridwidth=1)
        # **********shown********
        st.plotly_chart(fig2, use_container_width=True, use_container_height=True)


        # metrics

        # correlation for last halving 2020
        close_prices = pd.DataFrame({
            symbol: hist2['Close'],
            second_symbol: hist3['Close']
        })
        close_prices = close_prices.replace(0, pd.NA)
        close_prices = close_prices.dropna()

        correlation = close_prices.corr()
        correlation_value = correlation.loc[symbol, second_symbol]

        daily_changes = close_prices.diff()
        signs = daily_changes.apply(np.sign)
        sign_agreement = signs[symbol] == signs[second_symbol]
        sign_agreement_rate = sign_agreement.mean()


        # correlation for current halving 2024
        close_prices_2024 = pd.DataFrame({
            symbol: hist_2024_1['Close'],
            second_symbol: hist_2024_2['Close']
        })
        close_prices_2024 = close_prices_2024.replace(0, pd.NA)
        close_prices_2024 = close_prices_2024.dropna()
        
        correlation_2024 = close_prices_2024.corr()
        correlation_value_2024 = correlation_2024.loc[symbol, second_symbol]

        daily_changes_2024 = close_prices_2024.diff()
        signs_2024 = daily_changes_2024.apply(np.sign)
        sign_agreement_2024 = signs_2024[symbol] == signs_2024[second_symbol]
        sign_agreement_rate_2024 = sign_agreement_2024.mean()   

        # show stats
        # **********shown********
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("Halving 2020")
                st.write(f"{symbol} and {second_symbol} between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")
                st.metric(label=f"Correlation:", value=round(correlation_value, 2))
                st.metric(label=f"Sign Agreement Rate:", value=round(sign_agreement_rate, 2))

            with col3:
                st.write("Halving 2024")    	
                st.write(f"{symbol} and {second_symbol} between {start_date_2024.strftime('%Y-%m-%d')} and {end_date_2024.strftime('%Y-%m-%d')}")
                st.metric(label=f"Correlation: ", value=round(correlation_value_2024, 2))
                st.metric(label=f"Sign Agreement Rate:", value=round(sign_agreement_rate_2024, 2))
            

        # **********shown********
        with st.container(border=True):
            st.header("Ticker over two periods")
            selected_ticker_symbol=st.selectbox('Which Ticker', options=[symbol,second_symbol])
            selected_ticker = ticker if selected_ticker_symbol == symbol else second_ticker


            with st.expander("Change Dates"):
                col3, col4, col5 = st.columns([3,1,3])
                with col3:
                    start_2020 = st.date_input("Start Date for Period 1", datetime.strptime('2019-12-01', '%Y-%m-%d'))
                    end_2020 = st.date_input("End Date for Period 1", datetime.strptime('2020-03-01', '%Y-%m-%d'))

                with col5:
                    end_2024 = st.date_input("End Date for Period 2", datetime.strptime('2024-03-01', '%Y-%m-%d'))
                    start_2024 = st.date_input("Start Date for Period 2", datetime.strptime('2023-12-01', '%Y-%m-%d'))
                

            # (Optional) Display the selected dates to the user
            st.write("Selected dates for Period 1:", start_2020, "to", end_2020)
            st.write("Selected dates for Period 2:", start_2024, "to", end_2024)

            # Download historical data for both periods
            history_a1 = selected_ticker.history(start=start_2020, end=end_2020)
            history_a2 = selected_ticker.history(start=start_2024, end=end_2024)

            # Calculate percentage changes in closing prices for each period
            closing_2020 = history_a1['Close'].dropna()
            closing_2024 = history_a2['Close'].dropna()

            # Concatenate the percentage changes into a single DataFrame
            closings = pd.concat([closing_2020.reset_index(drop=True), closing_2024.reset_index(drop=True)], axis=1, keys=[f'{symbol}_2020', f'{symbol}_2024'])

            # Calculate the correlation matrix
            correlation_new = closings.corr()

            # Extract the correlation value between the two periods
            correlation_value_new = correlation_new.loc[f'{symbol}_2020', f'{symbol}_2024']

            st.metric(label=f"Correlation between {selected_ticker_symbol} for the two periods:",value=round(correlation_value_new,2))

    
    else:
        st.write("No data returned for this symbol.")
else:
    st.sidebar.write("Please enter a stock symbol.")

st.sidebar.markdown('[yfinance ticker lookup](https://finance.yahoo.com/lookup/)', unsafe_allow_html=True)

