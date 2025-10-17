#!/usr/bin/env python3
"""
高度なStreamlit株価ダッシュボード
より詳細な分析機能とインタラクティブな可視化を提供
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import time
from typing import List, Dict, Optional
import logging
from streamlit_option_menu import option_menu

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ページ設定
st.set_page_config(
    page_title="📈 高度な株価分析ダッシュボード",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AdvancedStockDashboard:
    """高度な株価ダッシュボードクラス"""
    
    def __init__(self):
        """初期化"""
        self.default_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            '7203.T', '6758.T', '9984.T', '9432.T'
        ]
        
        # セッション状態の初期化
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {}
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標を計算"""
        df = data.copy()
        
        # 移動平均
        df['MA_5'] = df['Close'].rolling(window=5).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ボリンジャーバンド
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def create_advanced_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """高度なチャートを作成"""
        df = self.calculate_technical_indicators(data)
        
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'{symbol} 価格チャート（移動平均・ボリンジャーバンド）',
                'RSI',
                'MACD',
                '取引量'
            ),
            row_heights=[0.4, 0.2, 0.2, 0.2]
        )
        
        # 価格チャート
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='価格'
            ),
            row=1, col=1
        )
        
        # 移動平均
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_5'], name='MA5', line=dict(color='orange', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_20'], name='MA20', line=dict(color='blue', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_50'], name='MA50', line=dict(color='red', width=1)),
            row=1, col=1
        )
        
        # ボリンジャーバンド
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='red')),
            row=3, col=1
        )
        fig.add_trace(
            go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram', marker_color='gray'),
            row=3, col=1
        )
        
        # 取引量
        colors = ['green' if close >= open else 'red' for close, open in zip(df['Close'], df['Open'])]
        fig.add_trace(
            go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors),
            row=4, col=1
        )
        
        fig.update_layout(
            title=f'{symbol} 高度なテクニカル分析',
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def create_correlation_matrix(self, symbols: List[str], period: str = "1mo") -> go.Figure:
        """相関マトリックスを作成"""
        returns_data = {}
        
        for symbol in symbols:
            data = yf.download(symbol, period=period, progress=False)
            if not data.empty:
                returns_data[symbol] = data['Close'].pct_change().dropna()
        
        if not returns_data:
            return go.Figure()
        
        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='株式間相関マトリックス',
            height=500
        )
        
        return fig
    
    def create_risk_return_scatter(self, symbols: List[str], period: str = "1mo") -> go.Figure:
        """リスク・リターンスキャッタープロットを作成"""
        risk_return_data = []
        
        for symbol in symbols:
            data = yf.download(symbol, period=period, progress=False)
            if not data.empty:
                returns = data['Close'].pct_change().dropna()
                annual_return = returns.mean() * 252
                annual_volatility = returns.std() * np.sqrt(252)
                
                risk_return_data.append({
                    'symbol': symbol,
                    'return': annual_return * 100,
                    'volatility': annual_volatility * 100
                })
        
        if not risk_return_data:
            return go.Figure()
        
        df = pd.DataFrame(risk_return_data)
        
        fig = px.scatter(
            df, x='volatility', y='return',
            text='symbol',
            title='リスク・リターン分析',
            labels={'volatility': 'ボラティリティ（%）', 'return': '年率リターン（%）'}
        )
        
        fig.update_traces(textposition="top center")
        fig.update_layout(height=500)
        
        return fig
    
    def create_portfolio_analysis(self, portfolio: Dict[str, float]) -> go.Figure:
        """ポートフォリオ分析を作成"""
        if not portfolio:
            return go.Figure()
        
        # ポートフォリオの構成
        fig = px.pie(
            values=list(portfolio.values()),
            names=list(portfolio.keys()),
            title='ポートフォリオ構成'
        )
        
        return fig
    
    def run_dashboard(self):
        """ダッシュボードを実行"""
        # ヘッダー
        st.title("📈 高度な株価分析ダッシュボード")
        st.markdown("---")
        
        # ナビゲーションメニュー
        selected = option_menu(
            menu_title=None,
            options=["📊 ダッシュボード", "🔍 テクニカル分析", "📈 相関分析", "💼 ポートフォリオ", "⚙️ 設定"],
            icons=["bar-chart", "search", "graph-up", "briefcase", "gear"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
        
        # サイドバー
        with st.sidebar:
            st.header("⚙️ 設定")
            
            # 銘柄選択
            st.subheader("📊 銘柄選択")
            selected_symbols = st.multiselect(
                "監視する銘柄を選択",
                self.default_symbols,
                default=self.default_symbols[:6]
            )
            
            # 期間選択
            st.subheader("📅 期間設定")
            period = st.selectbox(
                "データ期間",
                ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
                index=2
            )
            
            # ウォッチリスト
            st.subheader("👀 ウォッチリスト")
            new_symbol = st.text_input("銘柄を追加", placeholder="例: AAPL")
            if st.button("追加") and new_symbol:
                if new_symbol not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_symbol)
                    st.success(f"{new_symbol}をウォッチリストに追加しました")
                    st.rerun()
            
            if st.session_state.watchlist:
                for symbol in st.session_state.watchlist:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(symbol)
                    with col2:
                        if st.button("×", key=f"remove_{symbol}"):
                            st.session_state.watchlist.remove(symbol)
                            st.rerun()
        
        # メインコンテンツ
        if not selected_symbols:
            st.warning("⚠️ 銘柄を選択してください")
            return
        
        if selected == "📊 ダッシュボード":
            self.show_dashboard(selected_symbols, period)
        elif selected == "🔍 テクニカル分析":
            self.show_technical_analysis(selected_symbols, period)
        elif selected == "📈 相関分析":
            self.show_correlation_analysis(selected_symbols, period)
        elif selected == "💼 ポートフォリオ":
            self.show_portfolio_analysis(selected_symbols)
        elif selected == "⚙️ 設定":
            self.show_settings()
    
    def show_dashboard(self, symbols: List[str], period: str):
        """ダッシュボード表示"""
        st.subheader("📊 リアルタイム株価ダッシュボード")
        
        # データ取得
        with st.spinner("📊 データを取得中..."):
            stock_data = []
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d", interval="1m")
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    stock_data.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'price': round(latest['Close'], 2),
                        'change': round(latest['Close'] - latest['Open'], 2),
                        'change_percent': round(((latest['Close'] - latest['Open']) / latest['Open']) * 100, 2),
                        'volume': int(latest['Volume'])
                    })
        
        if not stock_data:
            st.error("❌ データの取得に失敗しました")
            return
        
        # メトリクス表示
        cols = st.columns(len(stock_data))
        for i, data in enumerate(stock_data):
            with cols[i]:
                st.metric(
                    label=data['symbol'],
                    value=f"${data['price']:.2f}",
                    delta=f"{data['change']:+.2f} ({data['change_percent']:+.2f}%)"
                )
        
        # パフォーマンス比較チャート
        st.subheader("📈 パフォーマンス比較")
        fig = self.create_performance_chart(symbols, period)
        st.plotly_chart(fig, use_container_width=True)
    
    def show_technical_analysis(self, symbols: List[str], period: str):
        """テクニカル分析表示"""
        st.subheader("🔍 テクニカル分析")
        
        selected_stock = st.selectbox("分析する銘柄を選択", symbols)
        
        if selected_stock:
            data = yf.download(selected_stock, period=period, progress=False)
            if not data.empty:
                fig = self.create_advanced_chart(data, selected_stock)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ {selected_stock}のデータが取得できませんでした")
    
    def show_correlation_analysis(self, symbols: List[str], period: str):
        """相関分析表示"""
        st.subheader("📈 相関分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("相関マトリックス")
            fig1 = self.create_correlation_matrix(symbols, period)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("リスク・リターン分析")
            fig2 = self.create_risk_return_scatter(symbols, period)
            st.plotly_chart(fig2, use_container_width=True)
    
    def show_portfolio_analysis(self, symbols: List[str]):
        """ポートフォリオ分析表示"""
        st.subheader("💼 ポートフォリオ分析")
        
        # ポートフォリオ設定
        st.subheader("ポートフォリオ設定")
        portfolio = {}
        
        for symbol in symbols:
            weight = st.slider(f"{symbol} の配分（%）", 0, 100, 0, key=f"weight_{symbol}")
            if weight > 0:
                portfolio[symbol] = weight
        
        if portfolio:
            # 合計が100%になるように調整
            total_weight = sum(portfolio.values())
            if total_weight != 100:
                st.warning(f"⚠️ 配分の合計が{total_weight}%です。100%になるように調整してください。")
            else:
                st.success("✅ ポートフォリオ設定完了")
                
                # ポートフォリオ構成チャート
                fig = self.create_portfolio_analysis(portfolio)
                st.plotly_chart(fig, use_container_width=True)
                
                # ポートフォリオ保存
                if st.button("ポートフォリオを保存"):
                    st.session_state.portfolio = portfolio
                    st.success("ポートフォリオを保存しました")
    
    def show_settings(self):
        """設定表示"""
        st.subheader("⚙️ 設定")
        
        st.subheader("データソース設定")
        st.info("📊 データソース: Yahoo Finance")
        
        st.subheader("更新設定")
        auto_refresh = st.checkbox("自動更新を有効にする")
        if auto_refresh:
            refresh_interval = st.slider("更新間隔（秒）", 10, 300, 60)
        
        st.subheader("表示設定")
        chart_theme = st.selectbox("チャートテーマ", ["plotly", "plotly_white", "plotly_dark"])
        
        st.subheader("エクスポート設定")
        if st.button("設定をエクスポート"):
            settings = {
                "auto_refresh": auto_refresh,
                "refresh_interval": refresh_interval if auto_refresh else 60,
                "chart_theme": chart_theme
            }
            st.download_button(
                label="設定ファイルをダウンロード",
                data=str(settings),
                file_name="dashboard_settings.json",
                mime="application/json"
            )
    
    def create_performance_chart(self, symbols: List[str], period: str) -> go.Figure:
        """パフォーマンス比較チャートを作成"""
        fig = go.Figure()
        
        for symbol in symbols:
            data = yf.download(symbol, period=period, progress=False)
            if not data.empty:
                normalized_data = (data['Close'] / data['Close'].iloc[0]) * 100
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=normalized_data,
                        mode='lines',
                        name=symbol,
                        line=dict(width=2)
                    )
                )
        
        fig.update_layout(
            title='パフォーマンス比較（正規化）',
            xaxis_title='日付',
            yaxis_title='パフォーマンス（%）',
            height=500,
            hovermode='x unified'
        )
        
        return fig

def main():
    """メイン関数"""
    dashboard = AdvancedStockDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
