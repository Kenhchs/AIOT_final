# called by app.py in darknet, the prediction image will be save in ./Stock/
# Import the libraries
import math
import pandas_datareader as web
import numpy as np
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import datetime as dt

company = ""
Time_Interval = ""
LONG_TERM  = "長期"
MID_TERM   = "中期"
SHORT_TERM = "短期"
plt.style.use('fivethirtyeight')

see_past_days = 90
past_days_to_predict_now = 60
nubmer_of_days_want_to_predict = 40

def SET_DAYS_OF_PREDICTIONS(interval):
	global nubmer_of_days_want_to_predict
	global see_past_days
	if interval == LONG_TERM:
		nubmer_of_days_want_to_predict = 180
		see_past_days = 1095
		return 0

	elif interval == MID_TERM:
		nubmer_of_days_want_to_predict = 30
		see_past_days = 180
		return 0

	elif interval == SHORT_TERM:
		nubmer_of_days_want_to_predict = 7
		see_past_days = 30
		return 0

	else:
		print("SET_DAYS_OF_PREDICTIONS error")
		return 1

def stock_prediction():
	global company
	return_predictions = ""
	fr = fw = open("stock_information.txt", "r")
	input = fr.read().splitlines()
	print(input)
	fr.close()
	company = input[0]
	Time_Interval = input[1]

	# Get the date 
	try:
		now = dt.datetime.now()
		start = dt.datetime(now.year - 15, 1, 1)
		end = dt.datetime(now.year, now.month, now.day)
	except:
		print("Get date error")
		return 1

	# Three modes, long term, mid term, or short term
	temp = SET_DAYS_OF_PREDICTIONS(Time_Interval)
	if temp == 1:
		return 1

	# Get the stock quote
	try:
		df = web.DataReader(company, data_source='yahoo', start=start, end=end)
	except:
		print("Get stock quote error")
		return 1

	# Show the data
	# print(df)

	# Get the number of rows and columns in the data set
	# print(df.shape)

	# Visualize the closing price price history
	'''plt.figure(figsize=(16, 8))
	plt.title('{} Close Price History'.format(company))
	plt.plot(df['Close'])
	plt.xlabel('Data', fontsize=18)
	plt.ylabel('Close Price', fontsize=18)
	plt.show()'''

	# Create a new dataframe with only the 'Close' column
	try:
		data = df.filter(['Close'])
	except:
		print("Create a new dataframe with only the 'Close' column error")
		return 1
	# print(data)

	# Convert the dataframe to a numpy array
	try:
		dataset = data.values
	except:
		print("Convert the dataframe to a numpy array error")
		return 1
	# print(dataset.shape)

	# Get the number of rows to train the model on
	try:
		training_data_len = len(dataset)
	except:
		print("Get the number of rows to train the model on error")
		return 1

	# Scale the data
	try:
		scaler = MinMaxScaler(feature_range=(0, 1))
		scaled_data = scaler.fit_transform(dataset)
	except:
		print("Scale the data")
		return 1

	# Create the training dataset and the scaled traing dataset
	try:
		train_data = scaled_data[0:training_data_len, :]
	except:
		print("Create the training dataset and the scaled traing dataset error")
		return 1

	# Split the data into x_train and y_train datasets
	try:
		x_train = []
		y_train = []
		for i in range(past_days_to_predict_now, len(train_data)):
			x_train.append(train_data[i-past_days_to_predict_now:i, 0])
			y_train.append(train_data[i, 0])
	except:
		print("Split the data into x_train and y_train datasets error")
		return 1

	# Convert the x_train and y_train to numpy arrays
	try:
		x_train, y_train = np.array(x_train), np.array(y_train)
	except:
		print("Convert the x_train and y_train to numpy arrays error")
		return 1

	# Reshape the data
	try:
		x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
	except:
		print("Reshape the data error")
		return 1

	# Build the LSTM model
	try:
		model = Sequential()
		model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
		model.add(LSTM(50, return_sequences=False))
		model.add(Dense(25))
		model.add(Dense(1))
	except:
		print("Build the LSTM model error")
		return 1

	# Complie the model
	try:
		model.compile(optimizer='adam', loss='mean_squared_error')
	except:
		print("Compile the model error")
		return 1

	# Train the model
	try:
		model.fit(x_train, y_train, batch_size=2048, epochs=30)
	except:
		print("Train the model error")
		return 1

	# Create the testing dataset
	# Create a new array containing scaled values from index 1543 to 2003
	try:
		test_data = scaled_data
	except:
		print("Create the testing dataset error")
		return 1

	# Create the datasets x_test and y_test
	try:
		x_test = []
		y_test = dataset[training_data_len:, :]
		for i in range(past_days_to_predict_now, len(test_data)):
			x_test.append(test_data[i-past_days_to_predict_now:i, 0])
	except:
		print("Create the datasets x_test and y_test error")
		return 1

	# Convert the data to a numpy array
	try:
		x_test = np.array(x_test)
	except:
		print("Convert the data to a numpy array error")
		return 1

	# Reshape the data
	try:
		x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
	except:
		print("Reshape the data error")
		return 1

	# Get the model predicted values
	try:
		predictions = model.predict(x_test)
		predictions = scaler.inverse_transform(predictions)
	except:
		print("Get the model predicted values error")
		return 1

	# Plot the data
	try:
		valid = data[past_days_to_predict_now:training_data_len]
		valid['Predictions'] = predictions
	except:
		print("Plot the data error")
		return 1

	# Get the quote
	try:
		quote = web.DataReader(company, data_source='yahoo', start=start, end=end)
		new_df = quote.filter(['Close'])
		for i in range(nubmer_of_days_want_to_predict):
			NextDay_Date = dt.datetime.today() + dt.timedelta(days=i+1)
			NextDay_Date = str(NextDay_Date)
			year = int(NextDay_Date[0:4])
			month = int(NextDay_Date[5:7])
			date = int(NextDay_Date[8:10])
			last_60_days = new_df[-60:].values
			last_60_days_scaled = scaler.transform(last_60_days)
			X_test = []
			X_test.append(last_60_days_scaled)
			X_test = np.array(X_test)
			X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
			pred_price = model.predict(X_test)
			pred_price = scaler.inverse_transform(pred_price)
			new_df.loc[pd.Timestamp(year, month, date, 0)] = [pred_price[0][0]]
	except:
		print("Get the quote error")
		return 1

	# Visualize the data
	try:
		#print(valid.shape)
		#print(training_data_len)
		predictions = new_df[training_data_len:]
		train = new_df[training_data_len - see_past_days:training_data_len]
		valid = valid[-1 *  see_past_days:]
		#print(train.shape, valid.shape)
		plt.figure(figsize=(16, 8))
		plt.xlabel('Date', fontsize=18)
		plt.ylabel('Close Price', fontsize=18)
		plt.title('{}'.format(company))
		plt.plot(train[['Close']])
		plt.plot(valid[['Predictions']])
		plt.plot(predictions[['Close']])
		plt.axvline(x=end, color='k', linestyle='--')
		plt.legend(['Real', 'Predictions', 'Unknown'], loc='lower right')
		plt.savefig('./Stock/Stock_prediction.png') # becuase it is called by app.py in darknet
	except:
		print("Visualize the data error")
		return 1

	#print(predictions)
	#print(train)
	#print(valid)

	# Print the predictions
	try:
		step_size = nubmer_of_days_want_to_predict // 6
		if nubmer_of_days_want_to_predict == 7:
			step_size = 1
		print("預測收盤價:")
		fw = open("./Stock/stock_predictions.txt", "w")
		fw.write("預測收盤價:\n")
		for i in range(0, nubmer_of_days_want_to_predict, step_size):
			temp_date = (str(predictions.index[i]))[0:10]
			temp_prediction = predictions['Close'][i]
			print('%s\t\t\t\t\t%.2f' % (temp_date, temp_prediction))
			fw.write('%s\t\t\t\t\t\t\t\t%.2f\n' % (temp_date, temp_prediction))
		fw.close()
		return 0
	except:
		print("Print the predictions error")
		return 1
	return 1

success_or_error = stock_prediction()
print("laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa = {}".format(success_or_error))
fw = open("./Stock/success_or_error.txt", "w")
fw.write(str(success_or_error))
fw.close()