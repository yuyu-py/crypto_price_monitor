import requests
import sys
import time


class CryptoPriceTracker:
    def __init__(self, crypto_list=['bitcoin']):
        self.crypto_list = crypto_list if isinstance(crypto_list, list) else [crypto_list]
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "CryptoPriceTracker/1.0"
        }
        self.previous_prices = {}
        self.monitoring_active = False
        self.request_interval = 60
        self.price_history = {}

    def setup_api_params(self):
        crypto_ids = ','.join(self.crypto_list)
        params = {
            'ids': crypto_ids,
            'vs_currencies': 'jpy',
            'include_24hr_change': 'true'
        }
        return params

    def fetch_price_data(self):
        try:
            params = self.setup_api_params()
            response = requests.get(
                self.api_url, 
                params=params, 
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data
                
        except requests.exceptions.Timeout:
            print("\nエラー: API接続がタイムアウトしました")
            return None
        except requests.exceptions.ConnectionError:
            print("\nエラー: インターネット接続を確認してください")
            return None
        except requests.exceptions.HTTPError as e:
            if "429" in str(e):
                print("\nAPI制限: 次回更新まで待機中...")
            else:
                print(f"\nHTTPエラー: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\nAPI接続エラー: {e}")
            return None

    def validate_response(self, data):
        if data is None:
            return False, "データの取得に失敗しました"
        
        required_keys = ['jpy']
        for crypto_id in self.crypto_list:
            if crypto_id not in data:
                return False, f"通貨データが見つかりません: {crypto_id}"
            for key in required_keys:
                if key not in data[crypto_id]:
                    return False, f"必要なデータ項目が見つかりません: {key}"
        
        return True, "データは正常です"

    def parse_price_info(self, data):
        if not data:
            return None
        
        price_info = {
            'current_price': data.get('jpy', 0),
            'change_24h': data.get('jpy_24h_change', 0),
            'timestamp': time.time()
        }
        
        return price_info

    def format_price_display(self, price_info):
        if not price_info:
            return "価格データが利用できません"
        
        current_price = price_info['current_price']
        change_24h = price_info['change_24h']
        
        change_symbol = "+" if change_24h >= 0 else ""
        formatted_price = f"¥{current_price:,.0f}"
        formatted_change = f"({change_symbol}{change_24h:.2f}%)"
        
        return f"{formatted_price} {formatted_change}"

    def display_price(self, crypto_id, price_info):
        if price_info:
            formatted_display = self.format_price_display(price_info)
            crypto_name = crypto_id.capitalize()
            print(f"{crypto_name}: {formatted_display}")
        else:
            print("価格情報の表示に失敗しました")

    def detect_price_change(self, crypto_id, current_price_info):
        if not current_price_info:
            return False, "データが無効です"
        
        current_price = current_price_info['current_price']
        
        if crypto_id not in self.previous_prices:
            self.previous_prices[crypto_id] = current_price
            self.update_price_history(crypto_id, current_price)
            return True, "初回価格設定"
        
        if current_price != self.previous_prices[crypto_id]:
            price_diff = current_price - self.previous_prices[crypto_id]
            change_percent = (price_diff / self.previous_prices[crypto_id]) * 100
            self.previous_prices[crypto_id] = current_price
            self.update_price_history(crypto_id, current_price)
            return True, f"変動検知: {price_diff:+,.0f}円 ({change_percent:+.2f}%)"
        
        return False, "価格変動なし"

    def update_display_line(self, message, force_newline=False):
        if force_newline:
            print(f"\n{message}")
        else:
            sys.stdout.write(f"\r{message}")
            sys.stdout.flush()

    def get_color_code(self, change_value):
        if change_value > 0:
            return '\033[92m'  # 緑色（上昇）
        elif change_value < 0:
            return '\033[91m'  # 赤色（下降）
        else:
            return '\033[93m'  # 黄色（変動なし）
    
    def reset_color(self):
        return '\033[0m'  # 色をリセット

    def calculate_price_stats(self, crypto_id):
        if crypto_id not in self.price_history or len(self.price_history[crypto_id]) < 2:
            return None
        
        prices = self.price_history[crypto_id]
        current_price = prices[-1]
        start_price = prices[0]
        
        total_change = current_price - start_price
        change_percent = (total_change / start_price) * 100
        
        max_price = max(prices)
        min_price = min(prices)
        avg_price = sum(prices) / len(prices)
        
        return {
            'total_change': total_change,
            'change_percent': change_percent,
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price,
            'data_points': len(prices)
        }

    def update_price_history(self, crypto_id, price):
        if crypto_id not in self.price_history:
            self.price_history[crypto_id] = []
        
        self.price_history[crypto_id].append(price)
        
        # 履歴が100件を超えた場合、古いデータを削除
        if len(self.price_history[crypto_id]) > 100:
            self.price_history[crypto_id] = self.price_history[crypto_id][-100:]

    def format_detailed_display(self, crypto_id, price_info, stats=None):
        current_price = price_info['current_price']
        change_24h = price_info['change_24h']
        
        # 24時間変動の色設定
        color_code = self.get_color_code(change_24h)
        reset_code = self.reset_color()
        
        # 基本表示
        change_symbol = "+" if change_24h >= 0 else ""
        formatted_price = f"¥{current_price:,.0f}"
        formatted_change = f"({change_symbol}{change_24h:.2f}%)"
        
        display_line = f"{crypto_id.upper()}: {formatted_price} {color_code}{formatted_change}{reset_code}"
        
        # 統計情報の追加
        if stats:
            total_change_color = self.get_color_code(stats['total_change'])
            session_change = f"{total_change_color}総変動: {stats['total_change']:+,.0f}円 ({stats['change_percent']:+.2f}%){reset_code}"
            display_line += f" | {session_change} | データ: {stats['data_points']}件"
        
        return display_line

    def save_monitoring_data(self, filename="crypto_monitoring_log.txt"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== 仮想通貨監視ログ ===\n")
                f.write(f"監視日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"監視間隔: {self.request_interval}秒\n\n")
                
                for crypto_id in self.crypto_list:
                    f.write(f"--- {crypto_id.upper()} ---\n")
                    if crypto_id in self.previous_prices:
                        f.write(f"最終価格: ¥{self.previous_prices[crypto_id]:,.0f}\n")
                    
                    stats = self.calculate_price_stats(crypto_id)
                    if stats:
                        f.write(f"総変動: {stats['total_change']:+,.0f}円 ({stats['change_percent']:+.2f}%)\n")
                        f.write(f"最高価格: ¥{stats['max_price']:,.0f}\n")
                        f.write(f"最低価格: ¥{stats['min_price']:,.0f}\n")
                        f.write(f"平均価格: ¥{stats['avg_price']:,.0f}\n")
                        f.write(f"データ件数: {stats['data_points']}件\n")
                    f.write("\n")
            
            print(f"\n監視データを {filename} に保存しました")
            
        except IOError as e:
            print(f"\nファイル保存エラー: {e}")

    def start_monitoring(self):
        self.monitoring_active = True
        crypto_names = ', '.join([crypto.capitalize() for crypto in self.crypto_list])
        print(f"{crypto_names}の価格監視を開始します...")
        print("価格変動があった場合のみ表示されます")
        print("停止するには Ctrl+C を押してください\n")
        
        try:
            while self.monitoring_active:
                price_data = self.fetch_price_data()
                
                if price_data:
                    for crypto_id in self.crypto_list:
                        if crypto_id in price_data:
                            price_info = self.parse_price_info(price_data[crypto_id])
                            has_changed, change_message = self.detect_price_change(crypto_id, price_info)
                            
                            if has_changed:
                                stats = self.calculate_price_stats(crypto_id)
                                display_message = self.format_detailed_display(crypto_id, price_info, stats)
                                self.update_display_line(display_message, force_newline=True)
                
                time.sleep(self.request_interval)
                
        except KeyboardInterrupt:
            self.stop_monitoring()

    def stop_monitoring(self):
        self.monitoring_active = False
        self.update_display_line("\n監視を停止しました。", force_newline=True)
        print("プログラムを終了します。")

    def configure_monitoring(self, interval=60, crypto_list=None):
        if interval >= 30:
            self.request_interval = interval
            print(f"監視間隔を{interval}秒に設定しました")
        else:
            print("API制限のため、最小間隔は30秒です")
        
        if crypto_list:
            self.crypto_list = crypto_list if isinstance(crypto_list, list) else [crypto_list]
            self.previous_prices.clear()
            self.price_history.clear()
            crypto_names = ', '.join([crypto.capitalize() for crypto in self.crypto_list])
            print(f"監視対象を{crypto_names}に変更しました")

    def display_monitoring_stats(self):
        crypto_names = ', '.join([crypto.capitalize() for crypto in self.crypto_list])
        current_prices = []
        for crypto_id in self.crypto_list:
            if crypto_id in self.previous_prices:
                current_prices.append(f"¥{self.previous_prices[crypto_id]:,.0f}")
            else:
                current_prices.append("未取得")
        
        stats_info = {
            '監視対象': crypto_names,
            '更新間隔': f"{self.request_interval}秒",
            '現在価格': ', '.join(current_prices),
            '監視状態': "アクティブ" if self.monitoring_active else "停止中"
        }
        
        print("\n=== 監視システム状況 ===")
        for key, value in stats_info.items():
            print(f"{key}: {value}")
        print("=" * 25)


def main():
    # 複数通貨の監視例
    crypto_currencies = ['bitcoin', 'ethereum', 'ripple']
    tracker = CryptoPriceTracker(crypto_currencies)
    
    # 初期設定の表示
    tracker.display_monitoring_stats()
    
    # 設定のカスタマイズ
    tracker.configure_monitoring(interval=60, crypto_list=crypto_currencies)
    
    try:
        # リアルタイム監視の開始
        tracker.start_monitoring()
    except Exception as e:
        print(f"予期しないエラー: {e}")
    finally:
        # 監視データの保存
        tracker.save_monitoring_data()


if __name__ == "__main__":
    main()