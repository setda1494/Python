import os
import time
import jwt
import uuid
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
import smtplib
from email.mime.text import MIMEText
import joblib  # 모델 저장 및 불러오기를 위한 라이브러리

# 업비트 API 키 및 시크릿 입력
ACCESS_KEY = 'YOUR_ACCESS_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'
SERVER_URL = 'https://api.upbit.com'
EMAIL_USER = 'YOUR_EMAIL@gmail.com'
EMAIL_PASSWORD = 'YOUR_EMAIL_PASSWORD'

# 모델 저장 폴더 설정
MODEL_DIR = "CoinAI_M"

# 폴더가 없으면 생성
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# 로깅 설정
logging.basicConfig(filename='trading_log.txt', level=logging.INFO)

# 거래 내역 저장
trade_history = []

def create_token():
    """API 인증 토큰 생성"""
    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def api_request(endpoint, method='GET', data=None):
    """API 요청 처리"""
    url = f"{SERVER_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {create_token()}"}
    if method == 'GET':
        response = requests.get(url, headers=headers, params=data)
    else:
        response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_balance():
    """잔고 조회"""
    return api_request('/v1/accounts')

def buy_coin(market, price, volume):
    """매수 주문"""
    data = {
        "market": market,
        "side": "bid",
        "price": price,
        "volume": volume,
        "ord_type": "limit"
    }
    response = api_request('/v1/orders', method='POST', data=data)
    logging.info(f"Buy Order: {data} Response: {response}")
    trade_history.append({'type': 'buy', 'price': price, 'volume': volume})
    return response

def sell_coin(market, price, volume):
    """매도 주문"""
    data = {
        "market": market,
        "side": "ask",
        "price": price,
        "volume": volume,
        "ord_type": "limit"
    }
    response = api_request('/v1/orders', method='POST', data=data)
    logging.info(f"Sell Order: {data} Response: {response}")
    trade_history.append({'type': 'sell', 'price': price, 'volume': volume})
    return response

def get_historical_data(market):
    """과거 가격 데이터 조회"""
    return pd.DataFrame(api_request('/v1/candles/days', data={"market": market, "count": "200"}))

def get_current_price(market):
    """현재 가격 조회"""
    return api_request('/v1/ticker', data={"markets": market})[0]['trade_price']

def train_linear_regression(data):
    """선형 회귀 모델 학습 및 예측"""
    data['return'] = data['trade_price'].pct_change().dropna()
    X = data[['opening_price', 'high_price', 'low_price', 'trade_volume']].dropna()
    y = data['return'].dropna()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression().fit(X_train, y_train)
    joblib.dump(model, os.path.join(MODEL_DIR, 'linear_model.pkl'))  # 모델 저장
    return model

def train_xgboost(data):
    """XGBoost 모델 학습"""
    data['return'] = data['trade_price'].pct_change().dropna()
    X = data[['opening_price', 'high_price', 'low_price', 'trade_volume']].dropna()
    y = data['return'].dropna()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(objective='reg:squarederror').fit(X_train, y_train)
    joblib.dump(model, os.path.join(MODEL_DIR, 'xgboost_model.pkl'))  # 모델 저장
    return model

def train_lstm(data):
    """LSTM 모델 학습"""
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[['trade_price']].values)

    X, y = [], []
    for i in range(60, len(scaled_data)):
        X.append(scaled_data[i-60:i])
        y.append(scaled_data[i])
    X, y = np.array(X), np.array(y)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=50, batch_size=32)
    model.save(os.path.join(MODEL_DIR, 'lstm_model.h5'))  # 모델 저장
    return model, scaler

def backtest(model, data):
    """백테스트 수행"""
    predictions = model.predict(data[['opening_price', 'high_price', 'low_price', 'trade_volume']])
    data['predictions'] = predictions

    plt.figure(figsize=(14, 7))
    plt.plot(data['candle_date_time_utc'], data['trade_price'], color='blue', label='Actual Price')
    plt.plot(data['candle_date_time_utc'], data['predictions'], color='red', label='Predicted Price')
    plt.title('Backtest Results')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

    returns = data['predictions'] - data['trade_price']
    total_return = returns.sum()
    avg_return = returns.mean()
    logging.info(f"Total Return: {total_return}, Average Return: {avg_return}")
    return total_return, avg_return

def send_email(subject, body):
    """이메일 알림 전송"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

def automatic_trading(market, linear_model, xgboost_model, lstm_model, scaler, stop_loss_pct, take_profit_pct):
    """자동 매매 수행"""
    historical_data = get_historical_data(market)
    current_price = historical_data['trade_price'].iloc[-1]

    linear_prediction = linear_model.predict([[historical_data['opening_price'].iloc[-1],
                                               historical_data['high_price'].iloc[-1],
                                               historical_data['low_price'].iloc[-1],
                                               historical_data['trade_volume'].iloc[-1]]])

    xgboost_prediction = xgboost_model.predict([[historical_data['opening_price'].iloc[-1],
                                                  historical_data['high_price'].iloc[-1],
                                                  historical_data['low_price'].iloc[-1],
                                                  historical_data['trade_volume'].iloc[-1]]])

    scaled_last_data = scaler.transform(historical_data[['trade_price']].values[-60:])
    lstm_prediction = scaler.inverse_transform(lstm_model.predict(scaled_last_data.reshape((1, 60, 1))))

    volume = 0.001  # 매수할 수량

    if linear_prediction > 0 and xgboost_prediction > current_price and lstm_prediction > current_price:
        buy_coin(market, current_price, volume)
        send_email("Trade Alert", f"Buy Order executed at price: {current_price}")

    if linear_prediction < 0 and xgboost_prediction < current_price and lstm_prediction < current_price:
        sell_coin(market, current_price, volume)
        send_email("Trade Alert", f"Sell Order executed at price: {current_price}")

def display_trade_history():
    """거래 내역 표시"""
    history = pd.DataFrame(trade_history)
    if not history.empty:
        print(history)
    else:
        print("No trade history available.")

class TradingApp:
    def __init__(self, master):
        self.master = master
        master.title("Algorithmic Trading with LSTM, XGBoost, and Linear Regression")

        tk.Label(master, text="Algorithmic Trading Application").pack()

        tk.Button(master, text="Train Models", command=self.train_models).pack()
        tk.Button(master, text="Backtest", command=self.run_backtest).pack()
        tk.Button(master, text="Start Auto Trading", command=self.start_auto_trading).pack()
        tk.Button(master, text="Show Dashboard", command=self.show_dashboard).pack()
        tk.Button(master, text="Show Trade History", command=self.show_trade_history).pack()

        # 모델 불러오기
        self.load_models()

    def load_models(self):
        """모델 불러오기"""
        try:
            self.linear_model = joblib.load(os.path.join(MODEL_DIR, 'linear_model.pkl'))
            self.xgboost_model = joblib.load(os.path.join(MODEL_DIR, 'xgboost_model.pkl'))
            self.lstm_model = load_model(os.path.join(MODEL_DIR, 'lstm_model.h5'))
            messagebox.showinfo("Model Load", "Models have been loaded successfully!")
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            messagebox.showerror("Model Load Error", "Failed to load models.")

    def train_models(self):
        """모델 학습"""
        market = 'KRW-BTC'
        data = get_historical_data(market)

        # 모델 학습
        self.linear_model = train_linear_regression(data)
        self.xgboost_model = train_xgboost(data)
        self.lstm_model, self.scaler = train_lstm(data)

        messagebox.showinfo("Training Complete", "Models have been trained and saved successfully!")

    def run_backtest(self):
        """백테스트 실행"""
        market = 'KRW-BTC'
        data = get_historical_data(market)

        # 백테스트 수행
        total_return, avg_return = backtest(self.xgboost_model, data)
        messagebox.showinfo("Backtest Results", f"Total Return: {total_return:.2f}, Average Return: {avg_return:.2f}")

    def start_auto_trading(self):
        """자동 매매 시작"""
        market = 'KRW-BTC'
        stop_loss_pct = simpledialog.askfloat("Input", "Enter Stop Loss Percentage (e.g., 0.02 for 2%):")
        take_profit_pct = simpledialog.askfloat("Input", "Enter Take Profit Percentage (e.g., 0.05 for 5%):")

        while True:
            historical_data = get_historical_data(market)
            automatic_trading(market, self.linear_model, self.xgboost_model, self.lstm_model, self.scaler, stop_loss_pct, take_profit_pct)
            time.sleep(60)  # 1분 대기

    def show_dashboard(self):
        """대시보드 표시"""
        balance = get_balance()
        messagebox.showinfo("Current Balance", f"Your current balance is: {balance}")

    def show_trade_history(self):
        """거래 내역 표시"""
        history = pd.DataFrame(trade_history)
        if not history.empty:
            messagebox.showinfo("Trade History", history.to_string())
        else:
            messagebox.showinfo("Trade History", "No trade history available.")

# 메인 루프
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()
