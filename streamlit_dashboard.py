#!/usr/bin/env python3
"""
Streamlit株価ダッシュボード
yfinanceを使用してリアルタイム株価データを取得し、
インタラクティブな可視化を提供するWebアプリケーション
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import time
from typing import List, Dict, Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ページ設定
st.set_page_config(
    page_title="📈 株価ダッシュボード",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StockDashboard:
    """株価ダッシュボードクラス"""
    
    def __init__(self):
        """初期化"""
        self.default_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            '7203.T', '6758.T', '9984.T', '9432.T'
        ]
        
        # セッション状態の初期化
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        if 'stock_data' not in st.session_state:
            st.session_state.stock_data = {}
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """株式情報を取得"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'Unknown'),
                'current_price': round(latest['Close'], 2),
                'previous_close': round(latest['Open'], 2),
                'change': round(latest['Close'] - latest['Open'], 2),
                'change_percent': round(((latest['Close'] - latest['Open']) / latest['Open']) * 100, 2),
                'volume': int(latest['Volume']),
                'day_high': round(latest['High'], 2),
                'day_low': round(latest['Low'], 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0)
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """履歴データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def create_price_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """価格チャートを作成"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'{symbol} 価格推移', '取引量'),
            row_width=[0.7, 0.3]
        )
        
        # 価格チャート
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='価格'
            ),
            row=1, col=1
        )
        
        # 取引量チャート
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='取引量',
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f'{symbol} 株価・取引量チャート',
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_performance_chart(self, symbols: List[str], period: str = "1mo") -> go.Figure:
        """パフォーマンス比較チャートを作成"""
        fig = go.Figure()
        
        for symbol in symbols:
            data = self.get_historical_data(symbol, period)
            if data is not None and not data.empty:
                # 正規化（開始価格を100に設定）
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
    
    def create_sector_analysis(self, stock_data: List[Dict]) -> go.Figure:
        """セクター分析チャートを作成"""
        df = pd.DataFrame(stock_data)
        if df.empty:
            return go.Figure()
        
        sector_performance = df.groupby('sector').agg({
            'change_percent': 'mean',
            'volume': 'sum'
        }).reset_index()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('セクター別平均変動率', 'セクター別取引量'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 変動率チャート
        fig.add_trace(
            go.Bar(
                x=sector_performance['sector'],
                y=sector_performance['change_percent'],
                name='平均変動率',
                marker_color='lightgreen'
            ),
            row=1, col=1
        )
        
        # 取引量チャート
        fig.add_trace(
            go.Bar(
                x=sector_performance['sector'],
                y=sector_performance['volume'],
                name='取引量',
                marker_color='lightcoral'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title='セクター分析',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def run_dashboard(self):
        """ダッシュボードを実行"""
        # ヘッダー
        st.title("📈 リアルタイム株価ダッシュボード")
        st.markdown("---")
        
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
            
            # 自動更新設定
            st.subheader("🔄 自動更新")
            auto_refresh = st.checkbox("自動更新を有効にする", value=False)
            refresh_interval = st.slider("更新間隔（秒）", 10, 300, 60)
            
            # 更新ボタン
            if st.button("🔄 データを更新", type="primary"):
                st.session_state.last_update = datetime.datetime.now()
                st.rerun()
        
        # メインコンテンツ
        if not selected_symbols:
            st.warning("⚠️ 銘柄を選択してください")
            return
        
        # データ取得
        with st.spinner("📊 データを取得中..."):
            stock_data = []
            for symbol in selected_symbols:
                data = self.get_stock_info(symbol)
                if data:
                    stock_data.append(data)
        
        if not stock_data:
            st.error("❌ データの取得に失敗しました")
            return
        
        # データフレーム作成
        df = pd.DataFrame(stock_data)
        
        # メトリクス表示
        st.subheader("📊 現在の株価情報")
        cols = st.columns(len(stock_data))
        
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i]:
                st.metric(
                    label=f"{row['symbol']} ({row['name'][:20]}...)",
                    value=f"${row['current_price']:.2f}",
                    delta=f"{row['change']:+.2f} ({row['change_percent']:+.2f}%)"
                )
        
        # タブ表示
        tab1, tab2, tab3, tab4 = st.tabs(["📈 個別チャート", "📊 パフォーマンス比較", "🏢 セクター分析", "📋 データテーブル"])
        
        with tab1:
            st.subheader("📈 個別株価チャート")
            selected_stock = st.selectbox("表示する銘柄を選択", [d['symbol'] for d in stock_data])
            
            if selected_stock:
                hist_data = self.get_historical_data(selected_stock, period)
                if hist_data is not None and not hist_data.empty:
                    fig = self.create_price_chart(hist_data, selected_stock)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"⚠️ {selected_stock}の履歴データが取得できませんでした")
        
        with tab2:
            st.subheader("📊 パフォーマンス比較")
            fig = self.create_performance_chart(selected_symbols, period)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("🏢 セクター分析")
            fig = self.create_sector_analysis(stock_data)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.subheader("📋 詳細データ")
            # データテーブル
            display_df = df[['symbol', 'name', 'sector', 'current_price', 'change', 'change_percent', 'volume', 'market_cap', 'pe_ratio']].copy()
            display_df.columns = ['銘柄', '会社名', 'セクター', '現在価格', '変動', '変動率(%)', '取引量', '時価総額', 'P/E比']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # CSVダウンロード
            csv = display_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"stock_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # フッター
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"📊 表示銘柄数: {len(stock_data)}")
        
        with col2:
            if st.session_state.last_update:
                st.info(f"🕒 最終更新: {st.session_state.last_update.strftime('%H:%M:%S')}")
            else:
                st.info("🕒 最終更新: 未実行")
        
        with col3:
            st.info("📈 データ提供: Yahoo Finance")
        
        # 自動更新
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()

def main():
    """メイン関数"""
    dashboard = StockDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
