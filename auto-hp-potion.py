import cv2
import numpy as np
import pyautogui
import time
import keyboard
from threading import Thread

class AutoHPPotion:
    def __init__(self):
        # ตั้งค่าเริ่มต้นdsadddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
        self.running = False
        self.hp_region = None  # พื้นที่หลอด HP
        self.hp_key = 'f1'     # ปุ่มกดใช้ยา HP (เปลี่ยนได้)
        self.threshold = 0.6   # เกณฑ์ที่จะทำการใช้ยา (เมื่อ HP ลดลงกว่า 60%)
        self.check_interval = 0.2  # ระยะเวลาในการตรวจสอบ (วินาที)
        
        # สีที่ต้องการตรวจจับ (BGR)
        # หมายเหตุ: อาจต้องปรับค่าตามสีหลอด HP ของเกม
        self.hp_color_lower = np.array([0, 0, 100])  # สีแดงขั้นต่ำ
        self.hp_color_upper = np.array([50, 50, 255])  # สีแดงสูงสุด

    def select_hp_bar_region(self):
        """Select HP tube area"""
        print("Selecting tube area HP...")
        print("1. Click 's' to start selecting area")
        print("2. Click the top left corner of the HP tube")
        print("3. Click the bottom right corner of the HP tube")
        
        # รอให้ผู้ใช้กด 's' เพื่อเริ่ม
        keyboard.wait('s')
        
        # จับภาพจุดแรก
        print("Click the top left corner of the HP tube...")
        point1 = None
        while point1 is None:
            if pyautogui.mouseDown():
                point1 = pyautogui.position()
                time.sleep(0.3)  # รอเล็กน้อยเพื่อป้องกันการคลิกซ้ำ
        
        print(f"Point 1: {point1}")
        
        # จับภาพจุดที่สอง
        print("Click the bottom right corner of the HP tube...")
        point2 = None
        while point2 is None:
            if pyautogui.mouseDown():
                point2 = pyautogui.position()
        
        print(f"Point 2: {point2}")
        
        # คำนวณพื้นที่
        x1, y1 = point1
        x2, y2 = point2
        self.hp_region = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        print(f"HP tube area: {self.hp_region}")
        return self.hp_region
    
    def set_hp_key(self, key):
        """Set HP potion key"""
        self.hp_key = key
        print(f"Set HP potion key to: {key}")
    
    def set_threshold(self, threshold):
        """Set HP potion threshold"""
        if 0 < threshold < 1:
            self.threshold = threshold
            print(f"Set HP potion threshold to: {threshold*100}%")
        else:
            print("Threshold must be between 0 and 1")
    
    def analyze_hp_bar(self):
        """Analyze HP tube and return HP percentage"""
        if not self.hp_region:
            print("HP tube area not selected")
            return 1.0
        
        # จับภาพหน้าจอตามพื้นที่ที่กำหนด
        screenshot = pyautogui.screenshot(region=self.hp_region)
        screenshot = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        # สร้างหน้ากากสำหรับพื้นที่สีแดง (หลอด HP)
        mask = cv2.inRange(screenshot_bgr, self.hp_color_lower, self.hp_color_upper)
        
        # คำนวณพื้นที่สีแดงที่เหลือ
        red_pixels = cv2.countNonZero(mask)
        total_pixels = self.hp_region[2] * self.hp_region[3]
        
        # คำนวณเปอร์เซ็นต์ของหลอด HP ที่เหลือ
        hp_percent = red_pixels / total_pixels if total_pixels > 0 else 1.0
        
        return hp_percent
    
    def use_hp_potion(self):
        """Use HP potion"""
        print(f"HP low! Using HP potion... (Press {self.hp_key})")
        pyautogui.press(self.hp_key)
        # หน่วงเวลาเล็กน้อยเพื่อป้องกันการกดปุ่มซ้ำ
        time.sleep(1)
    
    def monitor_loop(self):
        """Monitor loop"""
        print("Start monitoring HP tube...")
        last_use_time = 0
        
        while self.running:
            current_time = time.time()
            hp_percent = self.analyze_hp_bar()
            
            # เช็คว่า HP น้อยกว่าเกณฑ์หรือไม่ และเวลาผ่านไปนานพอสำหรับการใช้ยาครั้งต่อไป
            if hp_percent < self.threshold and current_time - last_use_time > 1:
                self.use_hp_potion()
                last_use_time = current_time
            
            # หน่วงเวลาก่อนตรวจสอบครั้งต่อไป
            time.sleep(self.check_interval)
    
    def start(self):
        """Start monitoring"""
        if not self.hp_region:
            print("Please select HP tube area first")
            self.select_hp_bar_region()
        
        self.running = True
        self.monitor_thread = Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("Program started!")
        print("Press 'q' to stop")
        
        # รอจนกว่าผู้ใช้จะกด 'q' เพื่อหยุดโปรแกรม
        keyboard.wait('q')
        self.stop()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        print("Program stopped")

if __name__ == "__main__":
    print("Auto HP potion")
    print("-----------------------")
    
    auto_hp = AutoHPPotion()
    
    # Set HP potion key
    key = input("Enter HP potion key")
    auto_hp.set_hp_key(key)
    
    # ตั้งค่าเกณฑ์การใช้ยา
    try:
        threshold = float(input("Enter HP potion threshold (0.1-0.9, e.g. 0.6 means use when HP is 60%): "))
        auto_hp.set_threshold(threshold)
    except ValueError:
        print("Invalid value, using default 0.6")
    
    # เริ่มโปรแกรม
    auto_hp.start()
