# build_executable.py
# สคริปต์สำหรับสร้างไฟล์ .exe ที่รันได้โดยไม่ต้องติดตั้ง Python

"""
คำแนะนำการใช้งาน:

1. ติดตั้ง PyInstaller:
   pip install pyinstaller

2. ติดตั้ง library ที่จำเป็น:
   pip install opencv-python pyautogui keyboard numpy pillow

3. รันคำสั่งนี้เพื่อสร้าง .exe:
   python build_executable.py

หรือใช้คำสั่งโดยตรง:
   pyinstaller --onefile --windowed --icon=icon.ico --name="AutoHPPotion" auto-hp-potion-improved.py

ตัวเลือกสำหรับ PyInstaller:
- --onefile: รวมทุกอย่างเป็นไฟล์เดียว
- --windowed: ไม่แสดง command prompt (สำหรับ GUI)
- --console: แสดง command prompt (แนะนำสำหรับโปรแกรมนี้)
- --icon=icon.ico: ใส่ไอคอน
- --name="ชื่อโปรแกรม": ตั้งชื่อไฟล์ .exe
- --add-data: เพิ่มไฟล์เสริม
"""

import os
import subprocess
import sys

def build_executable():
    """สร้างไฟล์ .exe"""
    
    print("🔨 กำลังสร้างไฟล์ executable...")
    
    # ตรวจสอบว่ามี PyInstaller หรือไม่
    try:
        import PyInstaller
        print("✅ พบ PyInstaller")
    except ImportError:
        print("❌ ไม่พบ PyInstaller กำลังติดตั้ง...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # ตรวจสอบไฟล์ต้นฉบับ
    source_file = "auto-hp-potion-improved.py"
    if not os.path.exists(source_file):
        print(f"❌ ไม่พบไฟล์ {source_file}")
        print("กรุณาบันทึกโค้ดปรับปรุงแล้วเป็นไฟล์ชื่อ auto-hp-potion-improved.py")
        return False
    
    # คำสั่ง PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # รวมเป็นไฟล์เดียว
        "--console",                    # แสดง command prompt
        "--name=AutoHPPotion",          # ชื่อไฟล์ .exe
        "--clean",                      # ล้างไฟล์ temp
        source_file
    ]
    
    # เพิ่มตัวเลือกเสริม
    additional_options = [
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=pyautogui", 
        "--hidden-import=keyboard",
        "--hidden-import=tkinter",
        "--hidden-import=PIL"
    ]
    
    cmd.extend(additional_options)
    
    try:
        print("⚙️  รันคำสั่ง:", " ".join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ สร้างไฟล์ executable สำเร็จ!")
        print("📁 ไฟล์อยู่ที่: dist/AutoHPPotion.exe")
        
        # ตรวจสอบขนาดไฟล์
        exe_path = "dist/AutoHPPotion.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📏 ขนาดไฟล์: {size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        print("Output:", e.stdout)
        print("Error:", e.stderr)
        return False

def create_batch_file():
    """สร้างไฟล์ .bat สำหรับรัน"""
    bat_content = """@echo off
title Auto HP Potion
echo Starting Auto HP Potion...
AutoHPPotion.exe
pause
"""
    
    with open("run_auto_hp.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    print("✅ สร้างไฟล์ run_auto_hp.bat สำเร็จ")

def main():
    print("🎮 Build Script สำหรับ Auto HP Potion")
    print("=" * 50)
    
    # สร้าง executable
    if build_executable():
        create_batch_file()
        
        print("\n🎉 สำเร็จ! วิธีใช้งาน:")
        print("1. คัดลอกไฟล์ dist/AutoHPPotion.exe ไปยังเครื่องอื่น")
        print("2. รันไฟล์ .exe โดยตรง หรือใช้ run_auto_hp.bat")
        print("3. ไม่ต้องติดตั้ง Python หรือ library เพิ่มเติม")
        
        print("\n📋 ข้อกำหนดของเครื่องปลายทาง:")
        print("- Windows 7 ขึ้นไป")
        print("- RAM อย่างน้อย 2GB") 
        print("- เกมที่ต้องการใช้ Auto HP")
        
    else:
        print("\n❌ การสร้าง executable ล้มเหลว")
        print("💡 วิธีแก้ไข:")
        print("1. ตรวจสอบว่าติดตั้ง library ครบถ้วน")
        print("2. อัปเดต pip: python -m pip install --upgrade pip")
        print("3. ลองรันด้วยสิทธิ์ Administrator")

if __name__ == "__main__":
    main()