from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

USERNAME = "user"
PASSWORD = "password"
TRUYEN_FILE = "data.txt"

def login_manual(driver):
    print("\n" + "="*60)
    print("👉 Đăng nhập vào cuutruyen.net")
    print("="*60)
    driver.get("https://cuutruyen.net/")
    time.sleep(2)  
    input("\n👉 Nhấn Enter sau khi đã đăng nhập...")
    return True

def search_and_click_result(driver, manga_name):
    """Tìm kiếm và click vào dropdown result - TURBO VERSION"""
    print(f"\n[🔍] Tìm: {manga_name}")
    
    try:
        # Về trang chủ
        driver.get("https://cuutruyen.net/")
        time.sleep(1) 
        
        search_input = driver.execute_script("""
            // Tìm input có placeholder chứa từ khóa tìm kiếm
            const inputs = Array.from(document.querySelectorAll('input'));
            const searchInput = inputs.find(input => {
                const placeholder = (input.placeholder || '').toLowerCase();
                return placeholder.includes('tìm') || placeholder.includes('search');
            });
            return searchInput;
        """)
        
        if not search_input:
            print("[ERROR] Không tìm thấy search box")
            return False
        
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, search_input, manga_name)
        
        time.sleep(1.2) 
        
        success = driver.execute_script("""
            // Tìm tất cả link truyện visible
            const links = Array.from(document.querySelectorAll('a[href*="/mangas/"]'));
            const visibleLinks = links.filter(link => {
                return link.offsetParent !== null && 
                       link.getBoundingClientRect().top < 400;
            });
            
            if (visibleLinks.length > 0) {
                const firstLink = visibleLinks[0];
                firstLink.click();
                return true;
            }
            return false;
        """)
        
        if success:
            time.sleep(0.8)  # Giảm từ 1.5s → 0.8s
            return True
        else:
            print("[ERROR] Không tìm thấy kết quả phù hợp")
            return False
        
    except Exception as e:
        print(f"[ERROR] Lỗi tìm kiếm: {e}")
        return False

def follow_manga(driver):
    """Click nút THEO DÕI TRUYỆN - TURBO VERSION"""
    try:
        if '/mangas/' not in driver.current_url:
            return False
        
        result = driver.execute_script("""
            // Tìm tất cả button và filter nhanh
            const buttons = Array.from(document.querySelectorAll('button'));
            const followBtn = buttons.find(btn => {
                const text = btn.textContent.toLowerCase();
                return text.includes('theo dõi') && btn.offsetParent !== null;
            });
            
            if (followBtn) {
                followBtn.scrollIntoView({block: 'center', behavior: 'instant'});
                followBtn.click();
                return true;
            }
            return false;
        """)
        
        if result:
            print("✅")
            time.sleep(0.3)
            return True
        else:
            print("[WARNING] Không tìm thấy nút 'THEO DÕI'")
            return False
            
    except Exception as e:
        print(f"[ERROR] Lỗi follow: {e}")
        return False

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--disable-gpu')
    
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    print("🚀 Khởi động Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    driver.set_page_load_timeout(15)
    driver.set_script_timeout(15)
    
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
        print("⚡ TURBO MODE: ~2-3s/truyện\n")
        
        start_time = time.time()
        
        for i, manga in enumerate(test_list, 1):
            print(f"[{i}/{len(test_list)}] {manga[:40]}...", end=" ", flush=True)
            
            if search_and_click_result(driver, manga):
                if follow_manga(driver):
                    success += 1
                    print(f"✅")
                else:
                    failed.append(manga)
                    print(f"❌")
            else:
                failed.append(manga)
                print(f"⏭️")
            
            if i < len(test_list): 
                time.sleep(0.5) 
        
        total_time = time.time() - start_time
        avg_time = total_time / len(test_list)
        
        print(f"\n{'='*60}")
        print(f"🎉 HOÀN TẤT - TURBO MODE")
        print(f"{'='*60}")
        print(f"✅ Thành công: {success}/{len(test_list)}")
        print(f"❌ Thất bại: {len(failed)}")
        print(f"📊 Tỷ lệ: {success/len(test_list)*100:.1f}%")
        print(f"⏱️  Thời gian: {total_time:.1f}s")
        print(f"🚀 Tốc độ: {avg_time:.1f}s/truyện")
        
        if failed and len(failed) <= 20:
            print(f"\n❌ Danh sách thất bại:")
            for m in failed[:20]: 
                print(f"  - {m}")
            if len(failed) > 20:
                print(f"  ... và {len(failed) - 20} truyện khác")
        
        if success == len(test_list):
            print("\n🎊 PERFECT! Tất cả đều thành công!")
            
        if confirm.lower() != 'all':
            estimated_total = (avg_time * len(manga_list)) / 60
            print(f"\n📈 Ước tính toàn bộ {len(manga_list)} truyện: {estimated_total:.1f} phút")
        
    except KeyboardInterrupt:
        print(f"\n\n⏸️ Đã dừng bởi người dùng")
        print(f"✅ Đã follow: {success} truyện")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
    finally:
        input("\n👉 Nhấn Enter để đóng Chrome...")
        driver.quit()

if __name__ == "__main__":
    proceed = input("\n👉 Bắt đầu? (yes/no): ")
    if proceed.lower() in ["yes", "y"]:
        main()
    else:
        print("❌ Hủy")

