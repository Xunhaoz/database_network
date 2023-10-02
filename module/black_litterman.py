import json

import pandas as pd

# from controller.confidence_controller import ConfidenceController
# from controller.stock_controller import StockController
# from controller.view_controller import ViewController

from pypfopt import black_litterman, risk_models, BlackLittermanModel
from pypfopt import EfficientFrontier, objective_functions
import numpy as np

import yfinance as yf


def check_one(user_id: str, stock_controller, view_controller):
    stock_result = stock_controller.selector(table='stock', cols=['user_id'], vals=[user_id])
    if len(stock_result) < 3:
        return {'msg': "選取的股票支數過少"}

    view_result = view_controller.selector(table='absolute_view', cols=['user_id'], vals=[user_id])[0]
    if not view_result:
        return {'msg': "尚未設定觀點矩陣-絕對"}

    prices = price_processing(stock_result)

    market_prices = yf.download("SPY", period="max")["Adj Close"]
    mcaps = {_[2]: yf.Ticker(_[2]).info["marketCap"] for _ in stock_result}

    view_result = view_result['view']
    ret_bl, S_bl = cal_black_litterman(prices=prices, market_prices=market_prices, mcaps=mcaps,
                                       absolute_views=view_result)
    res = cal_profolio_allocation(ret_bl, S_bl)

    return {'msg': "\n".join(res)}


def check_two(user_id: str, stock_controller, view_controller, confidence_controller):
    stock_result = stock_controller.selector(table='stock', cols=['user_id'], vals=[user_id])
    if len(stock_result) < 3:
        return {'msg': "選取的股票支數過少"}

    view_result = view_controller.selector(table='absolute_view', cols=['user_id'], vals=[user_id])[0]
    if not view_result:
        return {'msg': "尚未設定絕對觀點矩陣-絕對"}

    confidence_result = confidence_controller.selector(table='confidences', cols=['user_id'], vals=[user_id])[0]
    if not confidence_result:
        return {'msg': "尚未設定置信矩陣"}

    prices = price_processing(stock_result)
    view_result = view_result['view']
    confidence_result = confidence_result['confidence']

    market_prices = yf.download("SPY", period="max")["Adj Close"]
    mcaps = {_[2]: yf.Ticker(_[2]).info["marketCap"] for _ in stock_result}

    ret_bl, S_bl = cal_black_litterman(prices=prices, market_prices=market_prices, mcaps=mcaps,
                                       absolute_views=view_result, view_confidences=confidence_result)
    res = cal_profolio_allocation(ret_bl, S_bl)

    return {'msg': "\n".join(res)}


def check_three(user_id: str, stock_controller, view_controller, confidence_controller):
    stock_result = stock_controller.selector(table='stock', cols=['user_id'], vals=[user_id])
    if len(stock_result) < 3:
        return {'msg': "選取的股票支數過少"}

    view_result = view_controller.selector(table='absolute_view', cols=['user_id'], vals=[user_id])[0]
    if not view_result:
        return {'msg': "尚未設定絕對觀點矩陣-絕對"}

    confidence_result = confidence_controller.selector(table='interval', cols=['user_id'], vals=[user_id])[0]
    if not confidence_result:
        return {'msg': "尚未設定置信區間"}

    prices = price_processing(stock_result)
    view_result = view_result['view']
    confidence_result = confidence_result['confidence']

    variances = []
    for lb, ub in confidence_result['intervals']:
        sigma = (ub - lb) / 2
        variances.append(sigma ** 2)
    omega = np.diag(variances)

    market_prices = yf.download("SPY", period="max")["Adj Close"]
    mcaps = {_[2]: yf.Ticker(_[2]).info["marketCap"] for _ in stock_result}

    ret_bl, S_bl = cal_black_litterman(prices=prices, market_prices=market_prices, mcaps=mcaps,
                                       absolute_views=view_result, omega=omega)
    res = cal_profolio_allocation(ret_bl, S_bl)

    return {'msg': "\n".join(res)}


def check_four(user_id: str, stock_controller, view_controller):
    stock_result = stock_controller.selector(table='stock', cols=['user_id'], vals=[user_id])
    if len(stock_result) < 3:
        return {'msg': "選取的股票支數過少"}

    view_result = view_controller.selector(table='pq_view', cols=['user_id'], vals=[user_id])[0]
    if not view_result:
        return {'msg': "尚未設定相對觀點矩陣-相對"}

    prices = price_processing(stock_result)
    view_result = view_result['view']
    P = np.array(view_result['P'])
    Q = np.array(view_result['Q']).reshape(-1, 1)

    market_prices = yf.download("SPY", period="max")["Adj Close"]
    mcaps = {_[2]: yf.Ticker(_[2]).info["marketCap"] for _ in stock_result}

    ret_bl, S_bl = cal_black_litterman(prices=prices, market_prices=market_prices, mcaps=mcaps,
                                       P=P, Q=Q)
    res = cal_profolio_allocation(ret_bl, S_bl)

    return {'msg': "\n".join(res)}


def cal_black_litterman(prices=None, market_prices=None, mcaps=None, absolute_views=None, P=None, Q=None, omega=None,
                        view_confidences=None):
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    delta = black_litterman.market_implied_risk_aversion(market_prices)
    market_prior = black_litterman.market_implied_prior_returns(mcaps, delta, S)

    bl = BlackLittermanModel(
        S, pi=market_prior, absolute_views=absolute_views,
        Q=Q, P=P, omega=omega, view_confidences=view_confidences,
        risk_aversion=delta if type(omega) is np.ndarray else 1
    )

    ret_bl = bl.bl_returns()
    S_bl = bl.bl_cov()

    return ret_bl, S_bl


def cal_profolio_allocation(ret_bl, S_bl):
    ef = EfficientFrontier(ret_bl, S_bl)
    ef.add_objective(objective_functions.L2_reg)
    ef.max_sharpe()
    weights = ef.clean_weights()

    for weight in weights:
        weights[weight] = round(weights[weight] * 100)
    weights = [f"{key:<5}\t應配置\t{weights[key]:3d}%\t的資產" for key in weights if weights[key] > 0]

    return weights


def price_processing(stock_result: list):
    df = pd.concat([pd.read_csv(_[3], index_col='Date')["Adj Close"].rename(_[2]) for _ in stock_result], axis=1)
    df_without_na = df.dropna()
    df_without_na = df[df_without_na.index[0]: df_without_na.index[-1]]
    prices = df_without_na.ffill()
    return prices
