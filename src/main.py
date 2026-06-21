import customtkinter as ctk
import datetime
import json
import sys
from pathlib import Path
from dataclasses import dataclass

# 💡 pathlibを使って、exe化しても安全にファイルの保存場所を特定する関数
def get_base_path() -> Path:
    if getattr(sys, 'frozen', False):
        # pyinstallerなどでexe化されて実行されている場合
        return Path(sys.executable).parent
    else:
        # 通常のPythonスクリプトとして実行されている場合
        return Path(__file__).resolve().parent

@dataclass
class Task:
    name: str
    start_time: datetime.time
    end_time: datetime.time
    completed: bool = False
    span: int = 1 
    description: str = "" 

class DailyTaskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Daily Task Manager")
        self.geometry("350x700")
        
        # --- 配色の定義 ---
        self.bg_color = "#101d2e"          
        self.static_color = "#20344d"      
        self.active_color = "#3db2ff"      
        self.completed_color = "#39526b" 
        self.empty_border_color = "#2b4566"
        self.focus_border_color = "#ffffff" 
        self.grab_border_color = "#f1c40f" 

        self.configure(fg_color=self.bg_color)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 

        # データ管理用
        self.tasks = {}    
        self.entries = []  
        self.grabbed_slot = None 
        
        # 💡 今日の日付を保持し、それを元に保存先ファイル名を決定する
        self.current_date = datetime.date.today()
        filename = f"{self.current_date.strftime('%Y-%m-%d')}.json"
        self.save_file = get_base_path() / filename

        self.start_hour = 6
        self.end_hour = 22 
        self.slots_per_hour = 6 
        
        self.total_hours = self.end_hour - self.start_hour + 1
        self.total_slots = self.total_hours * self.slots_per_hour

        self.setup_date_area()
        self.setup_timeline_area()
        self.update_progress()
        
        # 💡 アプリ起動時に「今日」のデータを読み込む
        self.load_data()
        
        if self.entries:
            self.entries[0].focus()

    # ==========================================
    # 💡 データの保存と読み込み (JSON)
    # ==========================================
    def save_data(self):
        """現在のタスクデータをJSONファイルに保存する"""
        data_to_save = {}
        for slot, task in self.tasks.items():
            data_to_save[str(slot)] = {
                "name": task.name,
                "start_time": task.start_time.strftime("%H:%M"), # JSONに保存できるように文字列にする
                "end_time": task.end_time.strftime("%H:%M"),
                "completed": task.completed,
                "span": task.span,
                "description": task.description
            }
            
        try:
            # pathlibのPathオブジェクトはそのままopen()に渡せます
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Failed to save tasks: {e}")

    def load_data(self):
        """JSONファイルからタスクデータを読み込んで画面に復元する"""
        # pathlibのメソッドでファイルの存在確認
        if not self.save_file.exists():
            return 
            
        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                data_loaded = json.load(f)
                
            for str_slot, task_dict in data_loaded.items():
                slot = int(str_slot)
                
                # 文字列から時間を復元
                start_t = datetime.datetime.strptime(task_dict["start_time"], "%H:%M").time()
                end_t = datetime.datetime.strptime(task_dict["end_time"], "%H:%M").time()
                
                # Taskオブジェクトを生成
                task = Task(
                    name=task_dict["name"],
                    start_time=start_t,
                    end_time=end_t,
                    completed=task_dict.get("completed", False),
                    span=task_dict.get("span", 1),
                    description=task_dict.get("description", "")
                )
                self.tasks[slot] = task
                
                # 画面の表示を復元
                entry = self.entries[slot]
                entry.delete(0, "end")
                entry.insert(0, task.name)
                
                # 複数スパンのタスクの場合、下のマスを隠して結合状態を復元する
                if task.span > 1:
                    entry.grid(row=slot, column=2, rowspan=task.span, sticky="nsew", pady=1)
                    for i in range(1, task.span):
                        idx = slot + i
                        if idx < len(self.entries):
                            self.entries[idx].grid_remove()
                            
                self.update_task_appearance(slot)
                
        except Exception as e:
            print(f"Failed to load tasks: {e}")

    # ==========================================
    # エリア構築メソッド群
    # ==========================================
    def setup_date_area(self):
        self.date_frame = ctk.CTkFrame(self, fg_color=self.static_color, corner_radius=6)
        self.date_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 10))
        
        # 💡 保持している self.current_date を使って表示を生成 (ISOフォーマットに変更)
        today_str = self.current_date.strftime("%Y-%m-%d")
        ctk.CTkLabel(self.date_frame, text=today_str, text_color="white", font=("Arial", 20, "bold")).pack(pady=10)

    def setup_timeline_area(self):
        self.timeline_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.timeline_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.timeline_frame.grid_columnconfigure(0, weight=0) 
        self.timeline_frame.grid_columnconfigure(1, weight=0) 
        self.timeline_frame.grid_columnconfigure(2, weight=1)

        self.progress_bg = ctk.CTkFrame(self.timeline_frame, width=10, fg_color=self.empty_border_color, corner_radius=5)
        self.progress_bg.grid(row=0, column=0, rowspan=self.total_slots, sticky="nsew", padx=(0, 10), pady=1)
        
        self.progress_fill = ctk.CTkFrame(self.progress_bg, fg_color=self.active_color, corner_radius=5)
        self.progress_fill.place(relx=0, rely=0, relwidth=1.0, relheight=0.0)

        for i, hour in enumerate(range(self.start_hour, self.end_hour + 1)):
            start_row = i * self.slots_per_hour

            time_slot = ctk.CTkFrame(self.timeline_frame, width=50, fg_color=self.static_color, corner_radius=6)
            time_slot.grid(row=start_row, column=1, rowspan=self.slots_per_hour, sticky="nsew", padx=(0, 10), pady=1)
            time_slot.grid_propagate(False)
            ctk.CTkLabel(time_slot, text=f"{hour}", text_color="white", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")

            for j in range(self.slots_per_hour):
                current_slot_index = start_row + j
                
                self.timeline_frame.grid_rowconfigure(current_slot_index, minsize=30, weight=0)

                skeleton = ctk.CTkFrame(self.timeline_frame, height=28, fg_color="transparent", corner_radius=6)
                skeleton.grid(row=current_slot_index, column=2, sticky="nsew", pady=1)
                skeleton.lower() 

                task_entry = ctk.CTkEntry(
                    self.timeline_frame, 
                    height=28, 
                    placeholder_text="", # 💡 プレースホルダーを削除してスッキリさせる
                    placeholder_text_color="#6380a1",
                    fg_color=self.bg_color, 
                    border_color=self.empty_border_color, 
                    border_width=1,
                    text_color="white",
                    corner_radius=6 # 💡 四角を少し丸めてモダンに
                )
                task_entry.grid(row=current_slot_index, column=2, sticky="nsew", pady=1)
                self.entries.append(task_entry)

                task_entry.bind("<Return>", lambda event, idx=current_slot_index: self.on_task_enter(idx))
                task_entry.bind("<Button-3>", lambda event, idx=current_slot_index: self.toggle_completed(idx, event))
                task_entry.bind("<FocusIn>", lambda event, idx=current_slot_index: self.on_focus(idx, True))
                task_entry.bind("<FocusOut>", lambda event, idx=current_slot_index: self.on_focus(idx, False))
                
                task_entry.bind("<Control-Return>", lambda event, idx=current_slot_index: self.toggle_completed(idx, event))
                task_entry.bind("<Command-Return>", lambda event, idx=current_slot_index: self.toggle_completed(idx, event))
                
                task_entry.bind("<Escape>", lambda event, idx=current_slot_index: self.on_escape(idx, event))
                
                task_entry.bind("<Double-Button-1>", lambda event, idx=current_slot_index: self.open_task_details(idx, event))
                task_entry.bind("<Control-d>", lambda event, idx=current_slot_index: self.open_task_details(idx, event))
                task_entry.bind("<Command-d>", lambda event, idx=current_slot_index: self.open_task_details(idx, event))
                
                task_entry.bind("<Up>", lambda event, idx=current_slot_index: self.on_up(event, idx))
                task_entry.bind("<Down>", lambda event, idx=current_slot_index: self.on_down(event, idx))
                task_entry.bind("<Shift-Up>", lambda event, idx=current_slot_index: self.on_shift_up(event, idx))
                task_entry.bind("<Shift-Down>", lambda event, idx=current_slot_index: self.on_shift_down(event, idx))

    # ==========================================
    # オートスクロール(Auto-Scroll) ヘルパー
    # ==========================================
    def ensure_visible(self, slot_index, span=1):
        canvas = self.timeline_frame._parent_canvas
        try:
            top_frac, bottom_frac = canvas.yview()
        except Exception:
            return

        viewport_size = bottom_frac - top_frac
        if viewport_size >= 1.0:
            return 

        slot_top_frac = slot_index / self.total_slots
        slot_bottom_frac = (slot_index + span) / self.total_slots
        margin = 0.02 

        if slot_top_frac < top_frac:
            canvas.yview_moveto(max(0.0, slot_top_frac - margin))
        elif slot_bottom_frac > bottom_frac:
            canvas.yview_moveto(min(1.0, slot_bottom_frac - viewport_size + margin))

    # ==========================================
    # 判定・モード管理ヘルパーメソッド
    # ==========================================
    def get_time_from_slot(self, slot_index):
        minutes_per_slot = 60 // self.slots_per_hour
        total_minutes = self.start_hour * 60 + slot_index * minutes_per_slot
        hour = total_minutes // 60
        minute = total_minutes % 60
        return datetime.time(hour, minute)

    def can_place_task(self, start_idx, span, ignore_idx=None):
        if start_idx < 0 or start_idx + span > len(self.entries):
            return False
        for t_start, t_task in self.tasks.items():
            if t_start == ignore_idx:
                continue
            if max(start_idx, t_start) < min(start_idx + span, t_start + t_task.span):
                return False
        return True

    def set_grab(self, slot_index):
        old_grab = self.grabbed_slot
        self.grabbed_slot = slot_index
        if old_grab is not None and old_grab != slot_index:
            self.update_task_appearance(old_grab)
        self.update_task_appearance(slot_index)

    def release_grab(self):
        if self.grabbed_slot is not None:
            old_grab = self.grabbed_slot
            self.grabbed_slot = None
            self.update_task_appearance(old_grab)

    def update_task_appearance(self, slot_index, is_focused=False):
        entry = self.entries[slot_index]
        is_grabbed = (self.grabbed_slot == slot_index)
        
        if slot_index in self.tasks:
            task = self.tasks[slot_index]
            if task.completed:
                bg = self.completed_color
                txt = "#8da3b8"
                fnt = ("Arial", 12, "overstrike")
            else:
                bg = self.active_color
                txt = "black"
                fnt = ("Arial", 12, "bold")
                
            if is_grabbed:
                border_w = 2
                border_c = self.grab_border_color 
            elif is_focused:
                border_w = 1
                border_c = self.focus_border_color 
            else:
                border_w = 0
                border_c = bg
                
            entry.configure(fg_color=bg, text_color=txt, font=fnt, border_width=border_w, border_color=border_c)
            entry.lift() 
        else:
            border_w = 1
            border_c = self.focus_border_color if is_focused else self.empty_border_color
            entry.configure(fg_color=self.bg_color, text_color="white", font=("Arial", 12, "normal"), border_width=border_w, border_color=border_c)

    # ==========================================
    # キーボードイベントハンドラ
    # ==========================================
    def on_escape(self, slot_index, event):
        self.release_grab()
        return "break"

    def on_up(self, event, slot_index):
        if self.grabbed_slot == slot_index:
            self.move_task(slot_index, -1)
        else:
            target = slot_index - 1
            while target >= 0:
                is_hidden_slot = False
                for t_start, t_task in self.tasks.items():
                    if t_start < target < t_start + t_task.span:
                        is_hidden_slot = True
                        target = t_start 
                        break
                
                if not is_hidden_slot:
                    break 

            if target >= 0:
                self.entries[target].focus()
        return "break"

    def on_down(self, event, slot_index):
        if self.grabbed_slot == slot_index:
            self.move_task(slot_index, 1)
        else:
            target = slot_index + 1
            
            if slot_index in self.tasks:
                target = slot_index + self.tasks[slot_index].span

            while target < len(self.entries):
                is_hidden_slot = False
                for t_start, t_task in self.tasks.items():
                    if t_start < target < t_start + t_task.span:
                        is_hidden_slot = True
                        target = t_start + t_task.span 
                        break
                
                if not is_hidden_slot:
                    break 

            if target < len(self.entries):
                self.entries[target].focus()
        return "break"

    def on_shift_up(self, event, slot_index):
        if self.grabbed_slot == slot_index:
            self.resize_task(slot_index, -1)
        return "break"

    def on_shift_down(self, event, slot_index):
        if self.grabbed_slot == slot_index:
            self.resize_task(slot_index, 1)
        return "break"

    def on_focus(self, slot_index, is_focused):
        if is_focused:
            if self.grabbed_slot is not None and self.grabbed_slot != slot_index:
                self.release_grab()
            
            span = self.tasks[slot_index].span if slot_index in self.tasks else 1
            self.ensure_visible(slot_index, span)
            
        self.update_task_appearance(slot_index, is_focused)

    def on_task_enter(self, slot_index):
        entry = self.entries[slot_index]
        text = entry.get().strip()
        
        if text:
            if slot_index in self.tasks:
                if self.tasks[slot_index].name == text:
                    if self.grabbed_slot == slot_index:
                        self.release_grab()
                    else:
                        self.set_grab(slot_index)
                else:
                    self.tasks[slot_index].name = text
                    self.set_grab(slot_index)
            else:
                if not self.can_place_task(slot_index, 1):
                    entry.delete(0, "end")
                    entry.focus()
                    return
                    
                start_t = self.get_time_from_slot(slot_index)
                end_t = self.get_time_from_slot(slot_index + 1)
                self.tasks[slot_index] = Task(name=text, start_time=start_t, end_time=end_t)
                self.set_grab(slot_index)
            
            entry.focus() 
        else:
            if slot_index in self.tasks:
                task = self.tasks[slot_index]
                span = task.span
                del self.tasks[slot_index]
                
                if self.grabbed_slot == slot_index:
                    self.grabbed_slot = None
                
                self.entries[slot_index].grid(row=slot_index, column=2, rowspan=1, sticky="nsew", pady=1)
                for i in range(1, span):
                    idx = slot_index + i
                    self.entries[idx].grid(row=idx, column=2, rowspan=1, sticky="nsew", pady=1)
                    self.entries[idx].delete(0, "end")
                    self.update_task_appearance(idx)
                    
            entry.delete(0, "end") 
            entry.focus()
            
        self.update_task_appearance(slot_index)
        self.save_data()

    def toggle_completed(self, slot_index, event=None):
        if slot_index in self.tasks:
            self.tasks[slot_index].completed = not self.tasks[slot_index].completed
            self.update_task_appearance(slot_index)
            self.save_data() 
        return "break"

    def open_task_details(self, slot_index, event=None):
        if slot_index not in self.tasks:
            return "break"
            
        task = self.tasks[slot_index]
        
        detail_window = ctk.CTkToplevel(self)
        detail_window.title("タスク詳細")
        detail_window.geometry("300x400")
        detail_window.attributes("-topmost", True) 
        detail_window.focus()
        
        ctk.CTkLabel(detail_window, text="タスク名", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        name_entry = ctk.CTkEntry(detail_window)
        name_entry.pack(fill="x", padx=15)
        name_entry.insert(0, task.name)
        
        ctk.CTkLabel(detail_window, text="詳細 (Description)", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        desc_box = ctk.CTkTextbox(detail_window, height=150)
        desc_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        desc_box.insert("0.0", task.description)
        
        def save_details():
            new_name = name_entry.get().strip()
            new_desc = desc_box.get("0.0", "end").strip()
            
            if new_name:
                task.name = new_name
                task.description = new_desc
                
                entry = self.entries[slot_index]
                entry.delete(0, "end")
                entry.insert(0, task.name)
                self.update_task_appearance(slot_index)
                self.save_data() 
                
            detail_window.destroy()
            
        save_btn = ctk.CTkButton(detail_window, text="保存", command=save_details, fg_color=self.active_color, text_color="black")
        save_btn.pack(pady=15)
        
        return "break"

    # ==========================================
    # コア機能: タスクの伸縮と移動
    # ==========================================
    def resize_task(self, slot_index, delta):
        if slot_index not in self.tasks:
            return
            
        task = self.tasks[slot_index]
        
        if delta == 1: 
            target_idx = slot_index + task.span
            if not self.can_place_task(target_idx, 1):
                return 
                
            self.entries[target_idx].grid_remove() 
            task.span += 1
            task.end_time = self.get_time_from_slot(slot_index + task.span)
            
            self.entries[slot_index].grid(row=slot_index, column=2, rowspan=task.span, sticky="nsew", pady=1)
            self.entries[slot_index].lift() 
            
        elif delta == -1: 
            if task.span <= 1:
                return 
                
            task.span -= 1
            task.end_time = self.get_time_from_slot(slot_index + task.span)
            self.entries[slot_index].grid(row=slot_index, column=2, rowspan=task.span, sticky="nsew", pady=1)
            
            revealed_idx = slot_index + task.span
            self.entries[revealed_idx].grid(row=revealed_idx, column=2, sticky="nsew", pady=1)
            self.entries[revealed_idx].delete(0, "end")
            self.update_task_appearance(revealed_idx)

        self.ensure_visible(slot_index, task.span)
        self.save_data() 

    def move_task(self, slot_index, direction):
        if slot_index not in self.tasks:
            return
            
        task = self.tasks[slot_index]
        target_start = slot_index + direction
        
        while 0 <= target_start <= len(self.entries) - task.span:
            if self.can_place_task(target_start, task.span, ignore_idx=slot_index):
                break
            target_start += direction
            
        if target_start < 0 or target_start > len(self.entries) - task.span:
            return 
            
        if target_start == slot_index:
            return
            
        was_grabbed = (self.grabbed_slot == slot_index)
        if was_grabbed:
            self.grabbed_slot = target_start
            
        self.entries[slot_index].grid(row=slot_index, column=2, rowspan=1, sticky="nsew", pady=1)
        for i in range(1, task.span):
            idx = slot_index + i
            self.entries[idx].grid(row=idx, column=2, rowspan=1, sticky="nsew", pady=1)
            self.entries[idx].delete(0, "end")
            self.update_task_appearance(idx)
            
        del self.tasks[slot_index]
        
        task.start_time = self.get_time_from_slot(target_start)
        task.end_time = self.get_time_from_slot(target_start + task.span)
        self.tasks[target_start] = task
        
        self.entries[target_start].grid(row=target_start, column=2, rowspan=task.span, sticky="nsew", pady=1)
        for i in range(1, task.span):
            idx = target_start + i
            self.entries[idx].grid_remove() 
            
        old_entry = self.entries[slot_index]
        old_entry.delete(0, "end")
        self.update_task_appearance(slot_index)
        
        new_entry = self.entries[target_start]
        new_entry.delete(0, "end")
        new_entry.insert(0, task.name)
        self.update_task_appearance(target_start)
        
        new_entry.focus()
        self.save_data() 

    def update_progress(self):
        now = datetime.datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        total_minutes = (self.end_hour - self.start_hour + 1) * 60 
        elapsed_minutes = (current_hour - self.start_hour) * 60 + current_minute

        if elapsed_minutes < 0:
            progress = 0.0 
        elif elapsed_minutes > total_minutes:
            progress = 1.0 
        else:
            progress = elapsed_minutes / total_minutes

        self.progress_fill.place_configure(relheight=progress)
        self.after(60000, self.update_progress)

if __name__ == "__main__":
    app = DailyTaskApp()
    app.mainloop()