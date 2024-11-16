import pandas as pd 

import numpy as np

def round_down(value, decimals):
	#https://stackoverflow.com/questions/41383787/round-down-to-2-decimal-in-python
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

def calculate_stop_loss_at_signal(df, i, column, stop_loss):
	if df['Signal'][i] == 'buy':
		df.iloc[i, df.columns.get_loc('Stop_Loss_Long')] = df[column][i] * (1-stop_loss)
	elif df['Signal'][i] == 'sell':
		df.iloc[i, df.columns.get_loc('Stop_Loss_Short')] = df[column][i] * (1+stop_loss)
	return df

def update_stop_loss_trailing_stop(df, i, column, stop_loss):
	df.iloc[i, df.columns.get_loc('Stop_Loss_Long')] = df['Stop_Loss_Long'][i-1]
	df.iloc[i, df.columns.get_loc('Stop_Loss_Short')] = df['Stop_Loss_Short'][i-1]

	if df['Trend'][i] == 'buy' and i < len(df)-1:	# needed cause last candle is retrieved with incomplete value
		if df[column][i] > df[column][i-1]:	# if price increased as expected in buy trend
			if df['Stop_Loss_Long'][i-1] is not None and df['Stop_Loss_Long'][i-1] < df[column][i] * (1-stop_loss):	# stop loss can only increase, not decrease
				df.iloc[i, df.columns.get_loc('Stop_Loss_Long')] = df[column][i] * (1-stop_loss)
	elif df['Trend'][i] == 'sell' and i < len(df)-1:	# needed cause last candle is retrieved with incomplete value
		if df[column][i] < df[column][i-1]:
			if df['Stop_Loss_Short'][i-1] is not None and df['Stop_Loss_Short'][i-1] > df[column][i] * (1+stop_loss):
				df.iloc[i, df.columns.get_loc('Stop_Loss_Short')] = df[column][i] * (1+stop_loss)

	return df

