import cv2
import numpy as np
import pyautogui
import time
import keyboard
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import os
import sys

class AutoHPPotion:
    def __init__(self):
        # ตั้งค่าเริ่มต้น
        self.running = False
        self.hp_region = None
        self.hp_key = 'f1'
        self.threshold = 0.6
        self.check_interval = 0.2
        self.cooldown = 1.0  # เวลารอระหว่างการใช้ยา
        
        # โหมดการตรวจจับ HP
        self.detection_mode = 'color'  # 'color' หรือ 'position'
        
        # สีสำหรับตรวจจับ (BGR format)
        self.hp_color_lower = np.array([0, 0, 100])    # สีแดงขั้นต่ำ
        self.hp_color_upper = np.array([80, 80, 255])  # สีแดงสูงสุด
        
        # ตัวแปรสถิติ
        self.current_hp_percent = 1.0
        self.potion_used_count = 0
        
        # ความปลอดภัย
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def select_hp_bar_region(self):
        """เลือกพื้นที่หลอด HP ด้วย GUI"""
        print("=== การเลือกพื้นที่หลอด HP ===")
        print("1. กด Enter เพื่อเริ่มเลือกพื้นที่")
        print("2. คลิกและลากเพื่อเลือกพื้นที่หลอด HP")
        print("3. กด ESC หากต้องการยกเลิก")
        
        input("กด Enter เพื่อเริ่ม...")
        
        try:
            # สร้างหน้าต่างโปร่งใสสำหรับเลือกพื้นที่
            root = tk.Tk()
            root.withdraw()  # ซ่อนหน้าต่างหลัก
            
            # ให้ผู้ใช้เลือกพื้นที่
            messagebox.showinfo("การเลือกพื้นที่", 
                              "คลิกและลากเพื่อเลือกพื้นที่หลอด HP\n"
                              "จากนั้นกด Enter เพื่อยืนยัน")
            
            # รอให้ผู้ใช้คลิกจุดแรก
            print("คลิกที่มุมซ้ายบนของหลอด HP...")
            while True:
                if keyboard.is_pressed('esc'):
                    return None
                try:
                    x1, y1 = pyautogui.position()
                    if pyautogui.mouseDown(button='left'):
                        break
                except:
                    pass
                time.sleep(0.1)
            
            time.sleep(0.3)  # รอให้เมาส์ถูกปล่อย
            
            # รอให้ผู้ใช้คลิกจุดที่สอง  
            print("คลิกที่มุมขวาล่างของหลอด HP...")
            while True:
                if keyboard.is_pressed('esc'):
                    return None
                try:
                    x2, y2 = pyautogui.position()
                    if pyautogui.mouseDown(button='left'):
                        break
                except:
                    pass
                time.sleep(0.1)
            
            # คำนวณพื้นที่
            self.hp_region = (
                min(x1, x2), 
                min(y1, y2), 
                abs(x2 - x1), 
                abs(y2 - y1)
            )
            
            print(f"✓ เลือกพื้นที่หลอด HP สำเร็จ: {self.hp_region}")
            
            # ทดสอบการจับภาพ
            test_hp = self.analyze_hp_bar()
            print(f"✓ ทดสอบการอ่านค่า HP: {test_hp*100:.1f}%")
            
            root.destroy()
            return self.hp_region
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการเลือกพื้นที่: {e}")
            try:
                root.destroy()
            except:
                pass
            return None
    
    def set_detection_mode(self, mode):
        """ตั้งค่าโหมดการตรวจจับ"""
        if mode in ['color', 'position']:
            self.detection_mode = mode
            print(f"✓ ตั้งค่าโหมดการตรวจจับเป็น: {mode}")
        else:
            print("❌ โหมดไม่ถูกต้อง (ใช้ 'color' หรือ 'position')")
    
    def set_hp_key(self, key):
        """ตั้งค่าปุ่มใช้ยา HP"""
        self.hp_key = key.lower()
        print(f"✓ ตั้งค่าปุ่มใช้ยา HP เป็น: {key}")
    
    def set_threshold(self, threshold):
        """ตั้งค่าเกณฑ์การใช้ยา"""
        if 0.1 <= threshold <= 0.9:
            self.threshold = threshold
            print(f"✓ ตั้งค่าเกณฑ์การใช้ยาเป็น: {threshold*100}%")
        else:
            print("❌ เกณฑ์ต้องอยู่ระหว่าง 0.1 ถึง 0.9")
    
    def analyze_hp_bar(self):
        """วิเคราะห์หลอด HP"""
        if not self.hp_region:
            return 1.0
        
        try:
            # จับภาพหน้าจอ
            screenshot = pyautogui.screenshot(region=self.hp_region)
            screenshot = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            
            if self.detection_mode == 'color':
                return self._analyze_by_color(screenshot_bgr)
            else:
                return self._analyze_by_position(screenshot_bgr)
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์ HP: {e}")
            return 1.0
    
    def _analyze_by_color(self, image):
        """วิเคราะห์ HP โดยใช้สี"""
        # สร้างหน้ากากสำหรับสีแดง
        mask = cv2.inRange(image, self.hp_color_lower, self.hp_color_upper)
        
        # คำนวณพื้นที่สีแดง
        red_pixels = cv2.countNonZero(mask)
        total_pixels = self.hp_region[2] * self.hp_region[3]
        
        hp_percent = red_pixels / total_pixels if total_pixels > 0 else 1.0
        return min(max(hp_percent, 0.0), 1.0)  # จำกัดค่าระหว่าง 0-1
    
    def _analyze_by_position(self, image):
        """วิเคราะห์ HP โดยใช้ตำแหน่ง (สำหรับหลอด HP แบบไล่เฉด)"""
        # แปลงเป็น Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # หาความกว้างของส่วนที่มีสี (ไม่ใช่พื้นหลัง)
        height, width = gray.shape
        
        # วิเคราะห์แต่ละแถวและหาค่าเฉลี่ย
        hp_widths = []
        for y in range(height):
            row = gray[y, :]
            # หาจุดที่ค่าสีเปลี่ยนแปลงอย่างมาก (ขอบของหลอด HP)
            diff = np.abs(np.diff(row.astype(int)))
            if len(diff) > 0 and np.max(diff) > 30:
                edges = np.where(diff > 30)[0]
                if len(edges) >= 2:
                    hp_width = edges[-1] - edges[0]
                    hp_widths.append(hp_width / width)
        
        if hp_widths:
            return np.mean(hp_widths)
        else:
            return 1.0
    
    def use_hp_potion(self):
        """ใช้ยา HP"""
        try:
            print(f"🔴 HP: {self.current_hp_percent*100:.1f}% - กำลังใช้ยา HP (ปุ่ม {self.hp_key})")
            pyautogui.press(self.hp_key)
            self.potion_used_count += 1
            return True
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการใช้ยา: {e}")
            return False
    
    def monitor_loop(self):
        """ลูปการตรวจสอบหลอด HP"""
        print("🔍 เริ่มการตรวจสอบหลอด HP...")
        last_use_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                self.current_hp_percent = self.analyze_hp_bar()
                
                # แสดงสถานะ HP
                if current_time % 5 < self.check_interval:  # แสดงทุก 5 วินาที
                    status = "🟢" if self.current_hp_percent >= self.threshold else "🟡"
                    print(f"{status} HP: {self.current_hp_percent*100:.1f}% | "
                          f"ยาที่ใช้: {self.potion_used_count} ครั้ง")
                
                # ตรวจสอบว่าต้องใช้ยาหรือไม่
                if (self.current_hp_percent < self.threshold and 
                    current_time - last_use_time > self.cooldown):
                    
                    if self.use_hp_potion():
                        last_use_time = current_time
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในลูปการตรวจสอบ: {e}")
                time.sleep(1)
    
    def start(self):
        """เริ่มโปรแกรม"""
        print("🚀 เริ่มโปรแกรม Auto HP Potion")
        
        if not self.hp_region:
            print("📍 กำลังเลือกพื้นที่หลอด HP...")
            if not self.select_hp_bar_region():
                print("❌ ยกเลิกการเลือกพื้นที่")
                return
        
        # แสดงการตั้งค่า
        print(f"\n⚙️  การตั้งค่าปัจจุบัน:")
        print(f"   - ปุ่มใช้ยา: {self.hp_key}")
        print(f"   - เกณฑ์ใช้ยา: {self.threshold*100}%")
        print(f"   - โหมดตรวจจับ: {self.detection_mode}")
        print(f"   - ระยะเวลาตรวจสอบ: {self.check_interval}s")
        print(f"   - Cooldown: {self.cooldown}s")
        
        # เริ่มการตรวจสอบ
        self.running = True
        self.monitor_thread = Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"\n✅ โปรแกรมเริ่มทำงานแล้ว!")
        print("🛑 กด 'q' เพื่อหยุดโปรแกรม")
        print("🔄 กด 'r' เพื่อรีเซ็ตสถิติ")
        print("📊 กด 's' เพื่อดูสถานะ")
        
        # รอคำสั่งจากผู้ใช้
        try:
            while self.running:
                if keyboard.is_pressed('q'):
                    break
                elif keyboard.is_pressed('r'):
                    self.potion_used_count = 0
                    print("🔄 รีเซ็ตสถิติแล้ว")
                    time.sleep(0.5)
                elif keyboard.is_pressed('s'):
                    print(f"📊 สถานะ: HP {self.current_hp_percent*100:.1f}% | "
                          f"ยาที่ใช้ {self.potion_used_count} ครั้ง")
                    time.sleep(0.5)
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        self.stop()
    
    def stop(self):
        """หยุดโปรแกรม"""
        self.running = False
        print(f"\n🛑 โปรแกรมหยุดทำงานแล้ว")
        print(f"📈 สถิติ: ใช้ยา HP ทั้งหมด {self.potion_used_count} ครั้ง")

def main():
    print("🎮 โปรแกรมใช้ยา HP อัตโนมัติ v2.0")
    print("=" * 40)
    
    auto_hp = AutoHPPotion()
    
    # ตั้งค่าโหมดการตรวจจับ
    print("\n🔧 เลือกโหมดการตรวจจับ HP:")
    print("1. color - ใช้สีเป็นหลัก (แนะนำสำหรับหลอด HP สีแดง)")
    print("2. position - ใช้ตำแหน่งเป็นหลัก (สำหรับหลอด HP ไล่เฉด)")
    
    mode_choice = input("เลือกโหมด (1/2, default=1): ").strip()
    if mode_choice == '2':
        auto_hp.set_detection_mode('position')
    else:
        auto_hp.set_detection_mode('color')
    
    # ตั้งค่าปุ่มใช้ยา
    key = input("\n🎯 ใส่ปุ่มใช้ยา HP (เช่น f1, 1, q, default=f1): ").strip()
    if key:
        auto_hp.set_hp_key(key)
    
    # ตั้งค่าเกณฑ์การใช้ยา
    try:
        threshold_input = input("⚡ ใส่เกณฑ์การใช้ยา (0.1-0.9, default=0.6): ").strip()
        if threshold_input:
            threshold = float(threshold_input)
            auto_hp.set_threshold(threshold)
    except ValueError:
        print("❌ ค่าไม่ถูกต้อง ใช้ค่าเริ่มต้น 0.6")
    
    # เริ่มโปรแกรม
    try:
        auto_hp.start()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    except KeyboardInterrupt:
        print("\n🛑 โปรแกรมถูกหยุดโดยผู้ใช้")

if __name__ == "__main__":
    main()