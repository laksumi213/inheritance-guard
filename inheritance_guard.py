import json
import re
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk


class InheritanceMaskerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("相続実務・AI匿名化ツール v1.3 (助詞・ノイズ除去モデル)")
        self.root.geometry("1300x850")

        self.mask_map = {}
        self.log_file = "anonymization_log.txt"

        BG_COLOR = "#F5F5F5"
        FG_COLOR = "#000000"
        ENTRY_BG = "#FFFFFF"

        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 1. 左カラム
        self.left_frame = tk.LabelFrame(self.paned, text=" 1. 原稿入力 ")
        self.txt_input = scrolledtext.ScrolledText(
            self.left_frame,
            undo=True,
            font=("MS Gothic", 12),
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            padx=10,
            pady=10,
        )
        self.txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.txt_input.insert("1.0", "ここに原稿を貼り付けてください")
        self.paned.add(self.left_frame, width=400)

        # 2. 中カラム
        self.mid_frame = tk.Frame(self.paned)
        self.paned.add(self.mid_frame, width=450)

        auto_frame = tk.LabelFrame(self.mid_frame, text=" 高度な自動検知 ")
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(
            auto_frame,
            text="一括検知を実行（氏名・続柄・住所・口座）",
            bg="#e0e0e0",
            fg="black",
            highlightbackground="#CCCCCC",
            command=self.auto_extract,
        ).pack(fill=tk.X, padx=5, pady=5)

        manual_frame = tk.LabelFrame(self.mid_frame, text=" 手動追加 ")
        manual_frame.pack(fill=tk.X, padx=5, pady=5)
        input_grid = tk.Frame(manual_frame)
        input_grid.pack(fill=tk.X, padx=5)

        tk.Label(input_grid, text="隠す文字:").grid(row=0, column=0)
        self.ent_real = tk.Entry(
            input_grid, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR
        )
        self.ent_real.grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(input_grid, text="置換名:").grid(row=1, column=0)
        self.ent_token = tk.Entry(
            input_grid, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR
        )
        self.ent_token.insert(0, "[項目1]")
        self.ent_token.grid(row=1, column=1, sticky="ew", padx=5)
        input_grid.columnconfigure(1, weight=1)

        tk.Button(
            manual_frame,
            text="リストに追加",
            bg="#e0e0e0",
            fg="black",
            command=self.add_manual_row,
        ).pack(fill=tk.X, padx=5, pady=5)

        list_frame = tk.LabelFrame(
            self.mid_frame, text=" 置換リスト（ダブルクリックで修正） "
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        file_ops = tk.Frame(list_frame)
        file_ops.pack(fill=tk.X)
        tk.Button(
            file_ops, text="保存", bg="#e0e0e0", fg="black", command=self.save_to_json
        ).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(
            file_ops, text="読込", bg="#e0e0e0", fg="black", command=self.load_from_json
        ).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("Role", "RealName", "Token"),
            show="headings",
            height=12,
        )
        self.tree.heading("Role", text="種別")
        self.tree.heading("RealName", text="実名/住所/番号")
        self.tree.heading("Token", text="トークン")
        self.tree.column("Role", width=80)
        self.tree.column("RealName", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree.bind("<Double-1>", self.on_double_click)
        tk.Button(
            list_frame,
            text="選択行を削除",
            bg="#e0e0e0",
            fg="black",
            command=self.delete_row,
        ).pack(fill=tk.X, padx=5)

        # 3. 右カラム
        self.right_frame = tk.LabelFrame(self.paned, text=" 2. AI送信用出力 ")
        self.txt_output = scrolledtext.ScrolledText(
            self.right_frame,
            font=("MS Gothic", 12),
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            padx=10,
            pady=10,
        )
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        act_frame = tk.Frame(self.mid_frame)
        act_frame.pack(fill=tk.X, pady=10)
        tk.Button(
            act_frame,
            text="匿名化 ➔ コピー ➔ 入力消去",
            bg="#A5D6A7",
            fg="black",
            font=("MS Gothic", 11, "bold"),
            height=3,
            command=self.run_full_process,
        ).pack(fill=tk.X, padx=5)

        tk.Button(
            self.right_frame,
            text="AI回答を実名に復元",
            bg="#90CAF9",
            fg="black",
            font=("MS Gothic", 10, "bold"),
            height=2,
            command=self.run_restore,
        ).pack(fill=tk.X, padx=5, pady=5)
        self.paned.add(self.right_frame, width=450)

    def on_double_click(self, event):
        items = self.tree.selection()
        if not items:
            return
        item_id = items[0]
        column = self.tree.identify_column(event.x)
        current_values = self.tree.item(item_id, "values")

        if column == "#2":
            new_val = simpledialog.askstring(
                "修正", "実名/住所を修正してください:", initialvalue=current_values[1]
            )
            if new_val:
                self.tree.item(
                    item_id, values=(current_values[0], new_val, current_values[2])
                )
        elif column == "#3":
            new_val = simpledialog.askstring(
                "修正", "トークン名を修正してください:", initialvalue=current_values[2]
            )
            if new_val:
                self.tree.item(
                    item_id, values=(current_values[0], current_values[1], new_val)
                )

    def auto_extract(self):
        text = self.txt_input.get("1.0", tk.END)
        existing = [self.tree.item(i)["values"][1] for i in self.tree.get_children()]

        # 1. 氏名・続柄の検知
        name_kws = [
            "遺言者",
            "被相続人",
            "相続人",
            "受遺者",
            "遺言執行者",
            "証人",
            "立会人",
            "長女",
            "長男",
            "二女",
            "二男",
            "三女",
            "三男",
            "養子",
            "妻",
            "夫",
        ]

        # 検知を停止・除外する文字群（「の」を追加）
        stop_chars = r"のによをとはが及、。 \s　」）」第法"

        for kw in name_kws:
            # (?<!の) は「直前に『の』がないこと」を条件にする否定後読み
            # (?!の) は「直後に『の』がないこと」を条件にする否定先読み
            p = rf"{kw}(?!の)\s*[:：]?\s*([^ {stop_chars} ]{{2,10}})"
            for m in re.finditer(p, text):
                candidate = m.group(1).strip()

                # 最初の一文字が「の」「に」「法」などの場合は除外
                if any(
                    candidate.startswith(c)
                    for c in ["の", "に", "及", "法", "第", "よ"]
                ):
                    continue

                if candidate not in existing:
                    self.tree.insert(
                        "", "end", values=(kw, candidate, f"[{kw}_{len(existing) + 1}]")
                    )
                    existing.append(candidate)

        # 2. 住所の検知
        addr_p = r"(?:東京都|北海道|京都府|大阪府|.{2,3}県)[^ \n\r]{2,40}?(?:地番|[\s　]*[0-9０-９]+(?:[ー－ｰ\-－丁目番地号]))+[0-9０-９]*"
        for addr in set(re.findall(addr_p, text)):
            clean_addr = addr.strip()
            if clean_addr not in existing:
                self.tree.insert(
                    "",
                    "end",
                    values=("住所", clean_addr, f"[住所_{len(existing) + 1}]"),
                )
                existing.append(clean_addr)

        # 3. 日付
        date_p = r"(?:(?:昭和|平成|令和)[0-9０-９元]+年|[0-9]{4}年?|(?:\d{2,4})[-/])[0-9０-９]{1,2}[-/月][0-9０-９]{1,2}日?"
        for d in set(re.findall(date_p, text)):
            if d not in existing:
                self.tree.insert(
                    "", "end", values=("日付", d, f"[日付_{len(existing) + 1}]")
                )
                existing.append(d)

        # 4. 金融機関
        acc_p = r"(?:店番号|店番)?\s?[0-9]{3}[-\s]?[0-9]{7,8}"
        for acc in set(re.findall(acc_p, text)):
            if acc not in existing:
                self.tree.insert(
                    "",
                    "end",
                    values=("金融情報", acc, f"[口座番号_{len(existing) + 1}]"),
                )
                existing.append(acc)

    def run_full_process(self):
        raw_text = self.txt_input.get("1.0", tk.END).strip()
        if not raw_text or raw_text == "ここに原稿を貼り付けてください":
            return
        self.run_masking()
        masked_text = self.txt_output.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(masked_text)
        self.write_log()
        self.txt_input.delete("1.0", tk.END)
        messagebox.showinfo("完了", "コピー完了。入力欄を消去しました。")

    def run_masking(self):
        raw_text = self.txt_input.get("1.0", tk.END)
        self.mask_map = {}
        items = self.tree.get_children()
        masked_text = raw_text
        rows = [self.tree.item(i)["values"] for i in items]
        rows.sort(key=lambda x: len(str(x[1])), reverse=True)
        for row in rows:
            _, real, token = row
            self.mask_map[str(token)] = str(real)
            masked_text = masked_text.replace(str(real), str(token))
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", masked_text)

    def run_restore(self):
        current_text = self.txt_output.get("1.0", tk.END)
        restored_text = current_text
        for token, real in self.mask_map.items():
            restored_text = restored_text.replace(str(token), str(real))
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", restored_text)

    def add_manual_row(self):
        real = self.ent_real.get().strip()
        token = self.ent_token.get().strip()
        if real and token:
            self.tree.insert("", "end", values=("手動", real, token))
            self.ent_real.delete(0, tk.END)
            self.ent_token.delete(0, tk.END)
            self.ent_token.insert(0, f"[項目{len(self.tree.get_children()) + 1}]")

    def delete_row(self):
        for s in self.tree.selection():
            self.tree.delete(s)

    def save_to_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            data = [self.tree.item(i)["values"] for i in self.tree.get_children()]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    def load_from_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                for row in json.load(f):
                    self.tree.insert("", "end", values=row)

    def write_log(self):
        with open(self.log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"--- Processed at {timestamp} ---\n")
            for item in self.tree.get_children():
                role, real, token = self.tree.item(item)["values"]
                f.write(f"[{role}] {token} -> {real}\n")
            f.write("\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = InheritanceMaskerPro(root)
    root.mainloop()
