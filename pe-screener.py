""" Module for portfolio management using
    Börsdata API and Börsdata SDK
"""
from borsdata_sdk import BorsdataAPI
from borsdata_sdk import APIError

import numpy as np

#pylint: disable=C0303,W0703,C0206
class BorsdataPortfolioManager():
    """ Class for managing a portfolio
        using Börsdata API
        
        Parameters:
        ticker_portfolio : List
            -> Your portfolio in the form of a list of strings
            -> Eg: ['EVO', 'SEYE']
    """
    def __init__(self, ticker_portfolio):
        auth_key = open("authkey.txt", "r")
        self.api = BorsdataAPI(auth_key.readline())
        self.portfolio_ticker = ticker_portfolio
        self.portfolio_ins_id = self.get_portfolio_ins_ids_by_tickers()
        
    def get_ins_id_by_ticker(self,ticker):
        """ Get instrument id by ticker """
        instruments = self.api.get_instruments()
        for elem in instruments:
            if elem.ticker == ticker:
                return elem.insId
        
    def get_portfolio_ins_ids_by_tickers(self):
        """ Get insId from portfolio tickers """
        res = []
        for ticker in self.portfolio_ticker:
            res.append(self.get_ins_id_by_ticker(ticker))
        return res

    def get_last_pe_portfolio(self, report_type = 'r12'):
        """ Get last P/E of all portfolio companies 
            
            Parameters :: str
                -> 'year'|'quarter'|'r12'
        """
        portfolio_pe = {}
        for ins_id in self.portfolio_ins_id:
            price_earnings = self.get_latest_pe(ins_id, report_type)
            portfolio_pe[ins_id] = price_earnings
        return portfolio_pe
    
    def get_last_pe_portfolio_ticker(self, report_type = 'r12'): #r12 to get latest P/E
        """ Get last P/E of all portfolio companies 
            
            Parameter :: str
                -> 'year'|'quarter'|'r12'
        """
        portfolio_pe = {}
        for ticker in self.portfolio_ticker:
            price_earnings = self.get_latest_pe_ticker(ticker, report_type)
            portfolio_pe[ticker] = price_earnings
        return portfolio_pe
        
                    
    def get_reports_by_ins_id(self, ins_id, report_type):
        return self.api.get_instrument_reports(ins_id, report_type) 
    
    def get_latest_pe(self, ins_id, report_type = 'r12'):
        """ Get latest available P/E ratio """
        reports = self.get_reports_by_ins_id(ins_id, report_type)
        latest_report = reports[0]
        if report_type != 'quarter':
            eps = latest_report.earnings_per_share
        else:
            eps = latest_report.earnings_per_share * 4 # Annualize last quarter
            
        last_prices = self.api.get_instrument_stock_price_last()
        last_price_close = 0.0
        for price in last_prices:
            if price.i == ins_id:
                last_price_close = price.c
                break
        return last_price_close / eps # p/e
    
    def get_latest_pe_ticker(self, ticker, report_type):
        """ Get latest available P/E ratio by ticker
        """
        ins_id = self.get_ins_id_by_ticker(ticker.upper())
        return self.get_latest_pe(ins_id, report_type)
        
    
    def get_last_price_of_date_ins_id(self, ins_id, year, month, day):
        """ Get the last price of an instrument for a specific date """
        date = str(str(year) + '-' + str(month) + '-' + str(day))
        date1 = str(str(year) + '-' + str(month) + '-' + str(day-1))
        price = self.api.get_instrument_stock_price(ins_id, date, date1)
        print(price)
        print(date)
        if len(price) > 0:
            return price
        else:
            print("Error: Price not found")
            return self.get_last_price_of_date_ins_id(ins_id, year, month, day-1)
        
    def get_last_price_of_year_ins_id(self, ins_id, year):
        """ Get the last price of an instrument for a specific year """
        date = str(str(year) + '-12-25')
        date1 = str(str(year) + '-12-31')
        price = self.api.get_instrument_stock_price(ins_id, date, date1)
        return price[-1]
    
    def get_eps_per_year(self, ins_id):
        """ Get the EPS for each available year 
            by using annual reports 
        """
        reports = bd.get_reports_by_ins_id(ins_id, 'year')
        eps_per_year = {}
        for item in reports:
            eps_per_year[item.year] = item.earnings_per_share
        return eps_per_year
            
    def get_pe_per_year_ins_id(self, ins_id):
        eps = self.get_eps_per_year(ins_id)
        pe_per_year = {}
        for year in eps.keys():
            try:
                price_last = self.get_last_price_of_year_ins_id(ins_id, year)
            except IndexError:
                pass  
            pe_per_year[year] = price_last.c / eps[year]
        return pe_per_year
    
    def get_pe_per_year_ticker(self, ticker):
        ins_id = self.get_ins_id_by_ticker(ticker.upper())
        return self.get_pe_per_year_ins_id(ins_id)
    
    def get_mean_pe_max_by_ticker(self, ticker):
        """ Get the filtered mean P/E for the maximum
            amount of years available (max 10)
        """
        pe_per_year = self.get_pe_per_year_ticker(ticker.upper())
        num_entries = len(pe_per_year)
        mean = get_mean_from_dict_values(pe_per_year)
        median = get_median_from_dict_values(pe_per_year)
        std = get_std_from_dict_values(pe_per_year)
        return {'mean': mean, 'num_years': num_entries}
    
    def get_mean_pe_portfolio_ticker(self):
        """ Get the mean max P/E for the portfolio
        """
        portfolio_mean_pe = {}
        for ticker in self.portfolio_ticker:
            mean_pe = self.get_mean_pe_max_by_ticker(ticker)
            portfolio_mean_pe[ticker] = mean_pe
        return portfolio_mean_pe
    
    def get_pe_diff_from_mean_portfolio(self):
        """ Get P/E diff from mean for portfolio companies
            where last P/E was positive
        """
        mean_pe_portfolio = self.get_mean_pe_portfolio_ticker()
        last_pe_portfolio = self.get_last_pe_portfolio_ticker()
        difference_pe = {}
        for ticker in self.portfolio_ticker:
            if last_pe_portfolio[ticker] > 0:
                difference_pe[ticker] = last_pe_portfolio[ticker] / mean_pe_portfolio[ticker]['mean']
        return difference_pe
        
    def get_filtered_pe_diff_portfolio(self, pe_diff_dict):
        return {key:val for key, val in pe_diff_dict.items() if val > 0}

def get_mean_from_dict_values(my_dict):
    return np.mean(list(my_dict.values()))

def get_median_from_dict_values(my_dict):
    return np.median(list(my_dict.values()))

def get_std_from_dict_values(my_dict):
    return np.std(list(my_dict.values()),  ddof=1)

if __name__ == "__main__":
    # Set portfolio
    bd = BorsdataPortfolioManager(['BALD B', 'EVO', 'INVE B', 'INWI', 'NEPA', 'PACT', 'SEYE'])

    # Print portfolio companies
    print(bd.portfolio_ticker)
    print(bd.portfolio_ins_id)
    
    # Calculate diff from mean P/E 
    a = bd.get_pe_diff_from_mean_portfolio()
    print(bd.get_filtered_pe_diff_portfolio(a))