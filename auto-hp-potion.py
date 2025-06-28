import cv2
import numpy as np
import pyautogui
import time
import keyboard
from threading import Thread

class AutoHPPotion:
    def __init__(self):
        # ตั้งค่าเริ่มต้น
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
        """เลือกพื้นที่หลอด HP"""
        print("กำลังเลือกพื้นที่หลอด HP...")
        print("1. กด 's' เพื่อเริ่มเลือกพื้นที่")
        print("2. คลิกที่มุมซ้ายบนของหลอด HP")
        print("3. คลิกที่มุมขวาล่างของหลอด HP")
        
        # รอให้ผู้ใช้กด 's' เพื่อเริ่ม
        keyboard.wait('s')
        
        # จับภาพจุดแรก
        print("คลิกที่มุมซ้ายบนของหลอด HP...")
        point1 = None
        while point1 is None:
            if pyautogui.mouseDown():
                point1 = pyautogui.position()
                time.sleep(0.3)  # รอเล็กน้อยเพื่อป้องกันการคลิกซ้ำ
        
        print(f"จุดที่ 1: {point1}")
        
        # จับภาพจุดที่สอง
        print("คลิกที่มุมขวาล่างของหลอด HP...")
        point2 = None
        while point2 is None:
            if pyautogui.mouseDown():
                point2 = pyautogui.position()
        
        print(f"จุดที่ 2: {point2}")
        
        # คำนวณพื้นที่
        x1, y1 = point1
        x2, y2 = point2
        self.hp_region = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        print(f"พื้นที่หลอด HP: {self.hp_region}")
        return self.hp_region
    
    def set_hp_key(self, key):
        """ตั้งค่าปุ่มใช้ยา HP"""
        self.hp_key = key
        print(f"ตั้งค่าปุ่มใช้ยา HP เป็น: {key}")
    
    def set_threshold(self, threshold):
        """ตั้งค่าเกณฑ์การใช้ยา"""
        if 0 < threshold < 1:
            self.threshold = threshold
            print(f"ตั้งค่าเกณฑ์การใช้ยาเป็น: {threshold*100}%")
        else:
            print("เกณฑ์ต้องอยู่ระหว่าง 0 ถึง 1")
    
    def analyze_hp_bar(self):
        """วิเคราะห์หลอด HP และคืนค่าเปอร์เซ็นต์ของหลอด HP ที่เหลือ"""
        if not self.hp_region:
            print("ยังไม่ได้เลือกพื้นที่หลอด HP")
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
        """กดปุ่มใช้ยา HP"""
        print(f"HP ต่ำ! กำลังใช้ยา HP... (กดปุ่ม {self.hp_key})")
        pyautogui.press(self.hp_key)
        # หน่วงเวลาเล็กน้อยเพื่อป้องกันการกดปุ่มซ้ำ
        time.sleep(1)
    
    def monitor_loop(self):
        """ลูปการตรวจสอบหลอด HP"""
        print("เริ่มการตรวจสอบหลอด HP...")
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
        """เริ่มการตรวจสอบ"""
        if not self.hp_region:
            print("กรุณาเลือกพื้นที่หลอด HP ก่อน")
            self.select_hp_bar_region()
        
        self.running = True
        self.monitor_thread = Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("โปรแกรมเริ่มทำงานแล้ว!")
        print("กด 'q' เพื่อหยุดโปรแกรม")
        
        # รอจนกว่าผู้ใช้จะกด 'q' เพื่อหยุดโปรแกรม
        keyboard.wait('q')
        self.stop()
    
    def stop(self):
        """หยุดการตรวจสอบ"""
        self.running = False
        print("โปรแกรมหยุดทำงานแล้ว")

if __name__ == "__main__":
    print("โปรแกรมใช้ยา HP อัตโนมัติ")
    print("-----------------------")
    
    auto_hp = AutoHPPotion()
    
    # ตั้งค่าปุ่มใช้ยา
    key = input("ใส่ปุ่มใช้ยา HP (เช่น f1, 1, q): ")
    auto_hp.set_hp_key(key)
    
    # ตั้งค่าเกณฑ์การใช้ยา
    try:
        threshold = float(input("ใส่เกณฑ์การใช้ยา (0.1-0.9, เช่น 0.6 หมายถึงใช้ยาเมื่อ HP เหลือ 60%): "))
        auto_hp.set_threshold(threshold)
    except ValueError:
        print("ใส่ค่าไม่ถูกต้อง ใช้ค่าเริ่มต้น 0.6")
    
    # เริ่มโปรแกรม
    auto_hp.start()
