import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas_datareader as web
import plotly.graph_objects as go
from PIL import Image
image = Image.open('a.jpeg')

from streamlit_efficient_frontier import *
from streamlit_var import *

returns_methods = ["mean_returns", "log_returns", "projected_prices"]
risk_methods = ["covariance"]
risk_free_rates = ["no risk free rate", "4 week treasury bill", "3 month treasury bill", "6 month treasury bill", "1 year treasury bill", "manual input"]
function_list = ['efficient frontier', 'ticker drop', 'Value at Risk (VaR) analysis']

st.image(image, caption='Ahmad Mostafavi')
st.header("مرز کارآمد")
with st.beta_expander('هدف پروژه'):
    st.write("تعیین مرزکارآمد برای بهینه‌سازی سبد سرمایه")

today = dt.date.today()

before = today - dt.timedelta(days=3653)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)

if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')                     

sidebar_function = st.sidebar.selectbox("کارکرد مورد نیاز خود را انتخاب کنید", function_list)

if sidebar_function == "efficient frontier":
                     
    tickers = st.text_input("لطفاْ تیکرهای مدنظر خود را وارد کنید")
    st.text("تیکرها باید با کاما از هم جدا شوند مثال: BTC-USD, ETH-USD, LTC-USD")
    status_radio = st.radio('برای اجرا روی run  کلیک کنید.', ('stop', 'run'))
    
    df = pd.DataFrame()
    find_frontier = False
    
    if status_radio == "run":
    
        df = yf.download(tickers, start_date, end_date)['Adj Close']
        st.dataframe(df)
        
        find_frontier = True
    
    
    if find_frontier == True:
        
        st.subheader('گزینه‌های موجود برای محاسبه')
        
        with st.beta_expander("mean returns"):
            ("this gets the daily percent change and then gets the average of that distribution")  
            
        with st.beta_expander("projected prices"):
            ("plug in projected stock prices for each stock and then optimize to those returns")
            
        with st.beta_expander("log prices"):
            ("this gets the daily log return and then gets the average of that distribution")  
    
        returns_method = st.selectbox("Select returns method", returns_methods)
        
        if returns_method == "projected_prices":
            
            tickers = tickers.split(",")
            tickers = [x.strip(' ') for x in tickers]
                
            st.write("Enter target price and years projected for each company")
            
            projected_prices = pd.DataFrame(columns = ['target', 'years', 'current_price', 'daily_returns(%)'], index = tickers)
            
            for i in tickers:
                
                projected_col1, projected_col2, projected_col3 = st.beta_columns(3)
                
                with projected_col1:
                    st.write(yf.Ticker(i).info.get("longName"))
                
                with projected_col2:
                    prices = st.number_input("%s weight" % i, min_value = 0, max_value = 1000000)
                    projected_prices['target'][str(i)] = prices
                    
                with projected_col3:
                    year_projection = st.number_input("%s projected years" % i, min_value = 1, max_value = 1000000, step = 1)
                    projected_prices['years'] [str(i)] = year_projection
                    
            projected_price_radio = st.radio("Click run once dataframe is filled", ("stop", "run"))
            
            if projected_price_radio == "run":
    
                for i in range(len(projected_prices)):
                    
                    projected_prices['current_price'][tickers[i]] = yf.Ticker(tickers[i]).info.get('ask')
                    projected_prices['daily_returns(%)'][tickers[i]] = np.round(((projected_prices['target'][tickers[i]] - projected_prices['current_price'][tickers[i]]) / projected_prices['current_price'][i]) / (projected_prices['years'][tickers[i]] * 252) * 100,8)
                    
                
                st.write(projected_prices)
                projected_returns = projected_prices['daily_returns(%)']
        
        st.subheader("گزینه‌های موجود برای محاسبه‌ی ریسک")
        with st.beta_expander("covariance"):
            ("this creates a covariance matrix of the daily percentage changes of each stock")
        
        risk_measure = st.selectbox("متد مورد نظر خود را انتخاب کنید", risk_methods)
        num_portfolios_resp = st.number_input('تعداد شبیه‌سازی‌ها را برای محاسبه‌ی حالت بهینه معین کنید (100,000 بهترین نتیجه را ارایه خواهد داد)', min_value = 0, max_value = 1000000, step = 1)
        
        rf_end = dt.datetime.today()
        rf_start = rf_end - dt.timedelta(days = 10)

        
        rf_input = st.selectbox("نرخ بدون ریسک را انتخاب کنید", risk_free_rates)
        
        if rf_input == "no risk free rate":
            rf = 0.0
        
        if rf_input == "4 week treasury bill":
            
            rf = web.DataReader('DTB4WK', 'fred', rf_start, rf_end)
            rf = rf.iloc[:, 0][len(rf) - 1]
            st.write("4 week treasury bill:", '{:,}'.format(rf),"%")
            
        if rf_input == "3 month treasury bill":
            
            rf = web.DataReader('DTB3', 'fred', rf_start, rf_end)
            rf = rf.iloc[:, 0][len(rf) - 1]
            st.write("3 month treasury bill:", '{:,}'.format(rf),"%")
            
        if rf_input == "6 month treasury bill":
            
            rf = web.DataReader('DTB6', 'fred', rf_start, rf_end)
            rf = rf.iloc[:, 0][len(rf) - 1]
            st.write("6 month treasury bill:", '{:,}'.format(rf),"%")
        
        if rf_input == "1 year treasury bill":
            
            rf = web.DataReader('DTB1YR', 'fred', rf_start, rf_end)
            rf = rf.iloc[:, 0][len(rf) - 1]
            st.write("1 year treasury bill:", '{:,}'.format(rf),"%")
            
        if rf_input == "manual input":
            
            rf = st.number_input("enter a risk free rate")
            st.write("manual input")
        
        run_col1, run_col2 = st.beta_columns(2)
        
        with run_col1:
            frontier_radio = st.radio('Please click run to simulate efficient frontier.', ('stop', 'run'))
            
        with run_col2:
            var_run = st.radio("Run with VaR analysis", ("yes", "no"))
            
        if frontier_radio == "run":
            
            if returns_method == "mean_returns":
                ef = Efficient_Frontier(df, tickers)
            
            if returns_method == "projected_prices":
                ef = Efficient_Frontier(df, tickers, projected_returns)   
                
            if returns_method == "log_returns":
                ef = Efficient_Frontier(df, tickers)
            
            results_frame = ef.simulate_random_portfolios(returns_method, risk_measure, num_portfolios_resp, rf, tickers)
            portfolios = ef.find_portfolios(results_frame)
            
            fig = plt.figure()
            plt.scatter(results_frame['stdev'], results_frame['ret'], c = results_frame.sharpe, cmap = 'RdYlBu')
            
            plt.scatter(portfolios[0][1], portfolios[0][0], marker=(5,1,0),color='r',s=500)
            plt.scatter(portfolios[1][1], portfolios[1][0], marker=(5,1,0),color='g',s=500)
            plt.xlabel("standard deviation")
            plt.ylabel("return")
            st.pyplot(fig)
            
            min_var_weights = np.array(portfolios[1].drop(labels = ['ret', 'stdev', 'sharpe']))
            max_sharpe_weights = np.array(portfolios[0].drop(labels = ['ret', 'stdev', 'sharpe']))
            
            output_col1, output_col2 = st.beta_columns(2)
            
            with output_col1:
                st.write("بهترین پورتفولیو با حداقل نوسان ممکن(سبز)", portfolios[1])
            
            with output_col2:
                st.write("بهترین پروتفولیو با حداکثر سود ممکن (قرمز)", portfolios[0])
            
            min_var_weights_pie = portfolios[1].drop(labels = ['ret', 'stdev', 'sharpe']).to_frame().reset_index()
            min_var_pie = px.pie(min_var_weights_pie, values=min_var_weights_pie.columns[1], names='index', title='مرزکارآمد برای حداقل نوسان')
            st.plotly_chart(min_var_pie)
            
            max_sharpe_weights_pie = portfolios[0].drop(labels = ['ret', 'stdev', 'sharpe']).to_frame().reset_index()
            max_sharpe_pie = px.pie(max_sharpe_weights_pie, values=max_sharpe_weights_pie.columns[1], names='index', title='مرزکارآمد برای حداکثر سود')
            st.plotly_chart(max_sharpe_pie)
            
            if var_run == "yes":

                st.write("Values are determined using a $100,000 portfolio")
                
                var = VaR(df)
                ef_var = var.ef_var(min_var_weights, max_sharpe_weights)
                
if sidebar_function == "ticker drop":
    
    #cut the tickers
    def cut_tickers(tickers_list, cut_size):
        
        cut_size = int(len(tickers_list) / cut_size)
        random_nums = sorted(np.random.randint(len(tickers_list), size = cut_size), reverse = True)
        
        for i in range(len(random_nums)):
            tickers_list.pop(random_nums[i] - 1)
            
        st.write("tickers:", len(tickers_list))
        
        return tickers_list
    
    
    #run the efficient frontier
    def run_ef(tickers_list, start, end, simulations):
        
        #make a list for the dataframes
        results = []
        
        st.write("simulations:", simulations)
    
        #the number of simulations is how many times we want to cut the tickers
        for i in range(simulations):
            
            st.write("simulation", i+1, "of", simulations)
            
            #first we want to cut the tickers
            tickers_list = cut_tickers(tickers_list, 4)
            
            st.write("downloading prices")
            
            #then we want to get the historical prices for those tickers
            prices = yf.download(tickers_list, start, end)['Adj Close']
            
            #then we want to pass through the number of securities that we want
            num_portfolios = 100000
            
            #we also want to put in the risk free rate
            rf = 0.0
            
            st.write("running efficient frontier")
            
            #then we want to instantitate the efficient frontier variable
            ef = Efficient_Frontier(prices, tickers_list)
            
            #then we want to get the results
            results_frame = ef.simulate_random_portfolios("mean_returns", "covariance", num_portfolios, rf, tickers_list)
            
            results.append(results_frame)
            
        return results
    
    ticker_list = ['S&P 500', 'Dow Jones Industrial Average', 'Nasdaq 100', 'manual add']
    ticker_method = st.selectbox("Select index", ticker_list)
    
    if ticker_method == 'S&P 500':
        
        tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        tickers.remove("BRK.B")
        tickers.remove("BF.B")
        st.write("removed BRK.B and BF.B")
        
        
    if ticker_method == "Dow Jones Industrial Average":
        tickers = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')[1]['Symbol'].tolist()
        
    if ticker_method == "Nasdaq 100":
        tickers = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[3]['Ticker'].tolist()
        
    if ticker_method == "manual add":
        tickers = st.text_input("Please enter tickers here (seperate):")
        st.text("ex for Microsoft, Apple, Amazon, Google, Facebook would be 'MSFT, AAPL, AMZN, GOOG, FB'.")
        st.text("Enter 200 tickers for best results (not necessary), first test will drop 25% of tickers")
    
    ticker_radio = st.radio('Click Run when you are ready.', ('Stop', 'Run'))
    
    if ticker_radio == "Run":
        
        scatter_plots = run_ef(tickers, start_date, end_date, 16)
        total_plots = len(scatter_plots)

        cols = 4
        rows = 4
        
        fig, axs = plt.subplots(rows,cols, figsize = (15, 15))
        plotting_spots = []
        
        for i in range(rows):
            
            for j in range(cols):
                
                tuple_spot = (i, j)
                plotting_spots.append(tuple_spot)
                
        for j in range(total_plots):
        
            df = scatter_plots[j]
            plotting_spot = plotting_spots[j]
            ticker_count = len(df.columns) - 3
            
            axs[plotting_spot[0], plotting_spot[1]].scatter(df['stdev'], df['ret'])
            axs[plotting_spot[0], plotting_spot[1]].set_title(ticker_count)
            plt.tight_layout()
            
        fig.text(0.5, 0.005, 'Standard Deviation', ha='center', fontsize = 10)
        fig.text(0.005, 0.5, 'Returns', va='center', rotation='vertical', fontsize = 10)
        
        st.write(fig)

if sidebar_function == "ارزش در معرض خطر (VaR) تحلیل":
    
    weights_options = ['randomly generated', 'manual input']
    
    tickers = st.text_input("Please enter tickers here (seperate):")
    st.text("ex for Microsoft, Apple, Amazon, Google, Facebook would be: MSFT, AAPL, AMZN, GOOG, FB")
    status_radio = st.radio('Please click run when you are ready.', ('stop', 'run'))
    
    df = pd.DataFrame()
    find_frontier = False
    
    if status_radio == "run":
    
        df = yf.download(tickers, start_date, end_date)['Adj Close']
        st.dataframe(df)
        
        find_frontier = True
        
    if find_frontier == True:
        
        st.subheader('Options for gettings portfolio weights')
        weights_method = st.selectbox("Select method for inputting weights", weights_options)
        
        if weights_method == "randomly generated":
            
            tickers = tickers.split(",")
            tickers = [x.strip(' ') for x in tickers]
            
            weights = np.random.random(len(tickers))
            weights /= np.sum(weights)
            
            var = VaR(df)
            output = var.standard_var(weights)
        
        if weights_method == "manual input":
            
            tickers = tickers.split(",")
            tickers = [x.strip(' ') for x in tickers]
                
            st.write("Enter target price and years projected for each company")
            
            weights = pd.Series(index = tickers)
            
            for i in tickers:
                
                projected_col1, projected_col2 = st.beta_columns(2)
                
                with projected_col1:
                    st.write(yf.Ticker(i).info.get("longName"))
                
                with projected_col2:
                    weight_input = st.number_input("%s weight" % i, min_value = 0.00, max_value = 100.00)
                    weights[str(i)] = (weight_input / 100)
                    
            
            var_manual = st.radio("Click run once weights are filled", ("stop", "run"))
            
            if var_manual == "run":
                
                total_weights = 0
                
                for i in weights:
                    total_weights = total_weights + i
                    
                if total_weights < 1.0: 
                    
                    st.write("Weights do not equal up to 100 please recheck weights")
                    st.write("weights: {}".format(total_weights * 100))
                    var_run = False
                    
                if total_weights == 1.0:
                    var_run = True
                    
                if total_weights > 1.0:
                    
                    st.write("Using leverage, weights greater than 100%")
                    var_run = True
                
                if var_run == True:
                    
                    st.write("ready to run")
                    
                    run = st.radio("Click run to start VaR analysis", ("stop", "run"))
                    
                    if run == "run":
                        
                        weights = np.array(weights)
                        var = VaR(df)
                        output = var.standard_var(weights)
                    

st.write('سید احمد مصطفوی')
st.write("[GitHub](https://github.com/verethraghnah) |",
         "[LinkedIn](https://www.linkedin.com/in/ahmad-mostafavi/) |",
         "[site](https://www.dadehkav.tech/)")
