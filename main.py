from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

USERNAME = os.getenv("CUUTRUYEN_USERNAME") 
PASSWORD = os.getenv("CUUTRUYEN_PASSWORD") 
TRUYEN_FILE = "data.txt"

def login_manual(driver):
    print("\n" + "="*60)
    print("👉 Đăng nhập vào cuutruyen.net")
    print("="*60)
    driver.get("https://cuutruyen.net/")
    time.sleep(3)
    input("\n👉 Nhấn Enter sau khi đã đăng nhập...")
    return True

def search_and_click_result(driver, manga_name):
    """Tìm kiếm và click vào dropdown result"""
    print(f"\n[🔍] Tìm: {manga_name}")
    
    try:
        # Về trang chủ
        driver.get("https://cuutruyen.net/")
        time.sleep(1.5)  # Giảm từ 3s → 1.5s
        
        # Tìm input search bằng JS (đơn giản hơn)
        search_input = driver.execute_script("""
            const inputs = document.querySelectorAll('input');
            for (let input of inputs) {
                const placeholder = (input.placeholder || '').toLowerCase();
                if (placeholder.includes('tìm') || placeholder.includes('search')) {
                    return input;
                }
            }
            return null;
        """)
        
        if not search_input:
            print("[ERROR] Không tìm thấy search box")
            return False
        
        # Clear và nhập text bằng JS
        driver.execute_script("arguments[0].value = '';", search_input)
        driver.execute_script(f"arguments[0].value = '{manga_name}';", search_input)
        
        # Trigger input event
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, search_input)
        
        print("[OK] Đã nhập")
        
        # Đợi dropdown xuất hiện (2 giây thay vì 3)
        time.sleep(2)
        
        # Tìm kết quả trong dropdown
        # Dựa vào ảnh: có div chứa text "Sự Quyến Rũ Của 2.5D"
        results = driver.execute_script("""
            // Tìm tất cả link có href chứa /mangas/
            const links = document.querySelectorAll('a[href*="/mangas/"]');
            const results = [];
            
            for (let link of links) {
                // Chỉ lấy link visible
                if (link.offsetParent !== null) {
                    const rect = link.getBoundingClientRect();
                    // Chỉ lấy link ở phần trên của trang (dropdown)
                    if (rect.top < 400) {
                        results.push({
                            href: link.href,
                            text: link.textContent.trim(),
                            element: link
                        });
                    }
                }
            }
            
            return results;
        """)
        
        if not results:
            print("[ERROR] Không tìm thấy")
            return False
        
        print(f"[OK] Tìm thấy {len(results)} kết quả")
        
        # Lấy URL của kết quả đầu tiên
        first_url = results[0]['href']
        
        # Navigate đến URL
        driver.get(first_url)
        time.sleep(1.5)  # Giảm từ 3s → 1.5s
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

def follow_manga(driver):
    """Click nút THEO DÕI TRUYỆN"""
    try:
        url = driver.current_url
        
        if '/mangas/' not in url:
            return False
        
        time.sleep(1)  # Giảm từ 2s → 1s
        
        # Tìm nút theo dõi
        follow_btn = driver.execute_script("""
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = btn.textContent.toLowerCase();
                if (text.includes('theo dõi') && btn.offsetParent !== null) {
                    return btn;
                }
            }
            return null;
        """)
        
        if follow_btn:
            # Scroll và click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", follow_btn)
            time.sleep(0.3)  # Giảm từ 0.5s → 0.3s
            driver.execute_script("arguments[0].click();", follow_btn)
            
            print(f"✅")
            time.sleep(0.5)  # Giảm từ 1s → 0.5s
            return True
        else:
            print("[WARNING] Không tìm thấy nút 'THEO DÕI'")
            return False
            
    except Exception as e:
        print(f"[ERROR] Lỗi: {e}")
        return False

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    print("🚀 Khởi động Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.maximize_window()
    
    try:
        if not login_manual(driver):
            return
        
        with open(TRUYEN_FILE, "r", encoding="utf-8") as f:
            manga_list = [line.strip().replace("- ", "") for line in f if line.strip()]
        
        print(f"\n📚 Tổng: {len(manga_list)} truyện")
        confirm = input("👉 Nhập số để test hoặc 'all': ")
        
        if confirm.lower() == 'all':
            test_list = manga_list
        else:
            try:
                num = int(confirm)
                test_list = manga_list[:num]
            except:
                print("❌ Không hợp lệ")
                return
        
        success = 0
        failed = []
        
        print(f"\n🎬 Bắt đầu follow {len(test_list)} truyện...")
        print("💡 TIP: Bạn có thể Ctrl+C để dừng bất cứ lúc nào\n")
        
        for i, manga in enumerate(test_list, 1):
            print(f"[{i}/{len(test_list)}] {manga[:40]}...")
            
            if search_and_click_result(driver, manga):
                if follow_manga(driver):
                    success += 1
                    print(f"✅ {success}/{i}")
                else:
                    failed.append(manga)
                    print(f"❌")
            else:
                failed.append(manga)
                print(f"⏭️")
            
            # Delay giảm từ 2s → 1s
            time.sleep(1)
        
        # Report
        print(f"\n{'='*60}")
        print(f"🎉 HOÀN TẤT")
        print(f"{'='*60}")
        print(f"✅ Thành công: {success}/{len(test_list)}")
        print(f"❌ Thất bại: {len(failed)}")
        print(f"📊 Tỷ lệ: {success/len(test_list)*100:.1f}%")
        
        if failed and len(failed) <= 15:
            print(f"\n❌ Danh sách thất bại:")
            for m in failed:
                print(f"  - {m}")
        
        if success == len(test_list):
            print("\n🎊 PERFECT! Tất cả đều thành công!")
            print("👉 Bạn có thể chạy lại với 'all' để follow hết!")
        
    except KeyboardInterrupt:
        print(f"\n\n⏸️ Đã dừng bởi người dùng")
        print(f"✅ Đã follow: {success} truyện")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n👉 Nhấn Enter để đóng Chrome...")
        driver.quit()

if __name__ == "__main__":
    print("="*60)
    print("🎯 CUUTRUYEN AUTO FOLLOW - TURBO MODE")
    print("="*60)
    print("⚡ Tốc độ: ~3-4s/truyện (nhanh gấp đôi)")
    print("⏱️  199 truyện: ~10-12 phút")
    print("✅ Giảm delay, tối ưu output")
    print("="*60)
    
    proceed = input("\n👉 Bắt đầu? (yes/no): ")
    if proceed.lower() in ["yes", "y"]:
        main()
    else:

        print("❌ Hủy")
