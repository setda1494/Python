#pip install requests pyjwt

import os
import time
import pyupbit
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from plyer import notification

# API 키 설정
access_key = 'YOUR_ACCESS_KEY'
secret_key = 'YOUR_SECRET_KEY'
upbit = pyupbit.Upbit(access_key, secret_key)

# 매매 종목 및 기본 설정
ticker = "KRW-BTC"
short_window = 5  # 단기 이동 평균 (5분)
long_window = 20  # 장기 이동 평균 (20분)
initial_balance = 100000  # 초기 자본
trade_history = []  # 거래 내역 저장

# 로그 폴더 및 파일 설정
log_folder = "CoinAutoLog"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file_name = os.path.join(log_folder, datetime.now().strftime("%Y-%m-%d") + "_trading_log.txt")

# 로그 기록 함수
def log_trade(message):
    with open(log_file_name, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    log_text.insert(tk.END, f"{message}\n")
    log_text.yview(tk.END)

# GUI 설정
root = tk.Tk()
root.title("코인 매매 시스템")

# 현재가, 단기 및 장기 이동 평균 표시
current_price_label = tk.Label(root, text="현재가: ")
current_price_label.pack()

short_ma_label = tk.Label(root, text="단기 이동 평균: ")
short_ma_label.pack()

long_ma_label = tk.Label(root, text="장기 이동 평균: ")
long_ma_label.pack()

# 로그 텍스트 박스
log_text = tk.Text(root, height=10, width=50)
log_text.pack()

# 진행 상황 표시
progress_label = tk.Label(root, text="")
progress_label.pack()

# 통계 대시보드 표시
stats_label = tk.Label(root, text="")
stats_label.pack()

def notify_user(message):
    notification.notify(
        title="거래 알림",
        message=message,
        app_name="코인 매매 시스템",
        timeout=10
    )

def buy():
    try:
        amount = initial_balance / 10  # 예시로 10% 매수
        upbit.buy_market_order(ticker, amount)
        message = f"{amount} 원어치 매수했습니다."
        log_trade(message)
        notify_user(message)
        trade_history.append((datetime.now(), 'BUY', amount))
        update_stats()  # 통계 업데이트
    except Exception as e:
        messagebox.showerror("오류", f"매수 중 오류 발생: {e}")

def sell():
    try:
        balance = upbit.get_balance(ticker)
        if balance > 0:
            upbit.sell_market_order(ticker, balance)
            message = "모든 보유량을 매도했습니다."
            log_trade(message)
            notify_user(message)
            trade_history.append((datetime.now(), 'SELL', balance))
            update_stats()  # 통계 업데이트
        else:
            messagebox.showwarning("경고", "매도할 자산이 없습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"매도 중 오류 발생: {e}")

# 매수, 매도 버튼 생성
buy_button = tk.Button(root, text="매수", command=buy)
buy_button.pack()

sell_button = tk.Button(root, text="매도", command=sell)
sell_button.pack()

entry_price = None  # 매수 가격 초기화

def update_market_data():
    global entry_price

    try:
        # 현재가 조회
        current_price = pyupbit.get_current_price(ticker)

        # 이동 평균 계산
        short_ma = get_moving_average(short_window, ticker)
        long_ma = get_moving_average(long_window, ticker)

        # GUI 업데이트
        current_price_label.config(text=f"현재가: {current_price}")
        short_ma_label.config(text=f"단기 이동 평균: {short_ma}")
        long_ma_label.config(text=f"장기 이동 평균: {long_ma}")

        # 매수 조건: 단기 이동 평균이 장기 이동 평균을 상향 돌파
        if short_ma > long_ma and entry_price is None:
            entry_price = current_price  # 매수 가격 기록
            buy()  # 자동 매수

        # 매도 조건: 단기 이동 평균이 장기 이동 평균을 하향 돌파
        elif short_ma < long_ma and entry_price is not None:
            sell()  # 자동 매도
            entry_price = None  # 매수 가격 초기화

    except Exception as e:
        print(f"오류 발생: {e}")

    # 1분 후 다시 업데이트
    root.after(60000, update_market_data)

def get_moving_average(period, ticker):
    """주어진 기간 동안의 이동 평균을 계산합니다."""
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count=long_window)
    return df['close'].rolling(window=period).mean().iloc[-1]

def update_stats():
    """통계 업데이트 함수"""
    total_trades = len(trade_history)
    wins = sum(1 for trade in trade_history if trade[1] == 'SELL')  # 매도 거래 수
    losses = total_trades - wins
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    stats = f"총 거래 수: {total_trades}, 승리 거래: {wins}, 패배 거래: {losses}, 승률: {win_rate:.2f}%"
    stats_label.config(text=stats)

def backtest():
    """백테스트 실행 함수"""
    log_trade("백테스트 시작")
    progress_label.config(text="백테스트 진행 중...")
    
    # 과거 데이터 가져오기
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count=long_window*100)  # 100배의 데이터

    # 이동 평균 계산
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    balance = initial_balance
    entry_price = None

    for index, row in df.iterrows():
        current_price = row['close']
        short_ma = row['short_ma']
        long_ma = row['long_ma']

        if short_ma > long_ma and entry_price is None:
            entry_price = current_price
            balance -= initial_balance / 10  # 매수
            log_trade(f"매수: {current_price}, 잔고: {balance}")

        elif short_ma < long_ma and entry_price is not None:
            balance += current_price  # 매도
            log_trade(f"매도: {current_price}, 잔고: {balance}")
            entry_price = None

        # 진행 상황 업데이트
        progress_label.config(text=f"진행 중... 잔고: {balance:.2f}")

    log_trade(f"백테스트 완료: 최종 잔고: {balance:.2f}")
    progress_label.config(text="백테스트 완료")
    plot_backtest_results(df)

def plot_backtest_results(df):
    """백테스트 결과를 시각화합니다."""
    plt.figure(figsize=(12, 6))
    plt.plot(df['close'], label='가격', color='blue')
    plt.plot(df['short_ma'], label='단기 이동 평균', color='orange')
    plt.plot(df['long_ma'], label='장기 이동 평균', color='red')
    plt.title(f"{ticker} 백테스트 결과")
    plt.xlabel("시간")
    plt.ylabel("가격")
    plt.legend()
    plt.show()

def export_trade_history():
    """거래 내역을 CSV 파일로 내보내기"""
    if trade_history:
        df = pd.DataFrame(trade_history, columns=["시간", "종류", "금액"])
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("CSV 파일", "*.csv")])
        if file_path:
            df.to_csv(file_path, index=False)
            log_trade("거래 내역이 CSV 파일로 저장되었습니다.")
    else:
        messagebox.showwarning("경고", "거래 내역이 없습니다.")

# 거래 내역 내보내기 버튼 생성
export_button = tk.Button(root, text="거래 내역 내보내기", command=export_trade_history)
export_button.pack()

def simulate():
    """시뮬레이션 모드 실행"""
    log_trade("시뮬레이션 시작")
    progress_label.config(text="시뮬레이션 진행 중...")
    
    # 과거 데이터 가져오기
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count=long_window*100)

    # 이동 평균 계산
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    balance = initial_balance
    entry_price = None
    results = []

    for index, row in df.iterrows():
        current_price = row['close']
        short_ma = row['short_ma']
        long_ma = row['long_ma']

        # 매수 조건: 단기 이동 평균이 장기 이동 평균을 상향 돌파
        if short_ma > long_ma and entry_price is None:
            entry_price = current_price
            balance -= initial_balance / 10  # 매수
            results.append((datetime.now(), 'BUY', current_price, balance))
            log_trade(f"매수: {current_price}, 잔고: {balance}")

        # 매도 조건: 단기 이동 평균이 장기 이동 평균을 하향 돌파
        elif short_ma < long_ma and entry_price is not None:
            balance += current_price  # 매도
            results.append((datetime.now(), 'SELL', current_price, balance))
            log_trade(f"매도: {current_price}, 잔고: {balance}")
            entry_price = None

    log_trade(f"시뮬레이션 완료: 최종 잔고: {balance:.2f}")
    progress_label.config(text="시뮬레이션 완료")
    
    # 시뮬레이션 결과 시각화
    plot_simulation_results(results)

def plot_simulation_results(results):
    """시뮬레이션 결과를 시각화합니다."""
    dates = [result[0] for result in results]
    prices = [result[2] for result in results]
    balances = [result[3] for result in results]

    plt.figure(figsize=(12, 6))
    plt.plot(dates, balances, label='잔고', color='green')
    plt.title(f"{ticker} 시뮬레이션 결과")
    plt.xlabel("시간")
    plt.ylabel("잔고")
    plt.legend()
    plt.show()

# 시뮬레이션 모드 버튼 생성
simulate_button = tk.Button(root, text="시뮬레이션 실행", command=simulate)
simulate_button.pack()
