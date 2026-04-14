This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.github/
  workflows/
    build.yml
inheritance_guard.py
```

# Files

## File: inheritance_guard.py
```python
import json
import re
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk


class InheritanceMaskerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("相続実務・AI送信前 匿名化ガバナンスツール")
        self.root.geometry("1300x850")

        self.mask_map = {}
        self.log_file = "anonymization_log.txt"

        # 色の設定（Macのダークモードに負けない設定）
        BG_COLOR = "#F5F5F5"  # わずかにグレーがかった白（視認性向上）
        FG_COLOR = "#000000"  # 真っ黒
        ENTRY_BG = "#FFFFFF"  # 入力エリアは真っ白

        # --- 全体レイアウト ---
        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 1. 左カラム：原稿入力
        self.left_frame = tk.LabelFrame(self.paned, text=" 1. 原稿入力 ")
        self.txt_input = scrolledtext.ScrolledText(
            self.left_frame,
            undo=True,
            font=("MS Gothic", 12),
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,  # カーソルの色も黒
            padx=10,
            pady=10,
        )
        self.txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # テスト文字を入れておく（見えるか確認用）
        self.txt_input.insert("1.0", "ここに原稿を貼り付けてください")
        self.paned.add(self.left_frame, width=400)

        # 2. 中カラム：設定
        self.mid_frame = tk.Frame(self.paned)
        self.paned.add(self.mid_frame, width=450)

        # 自動抽出ボタン
        auto_frame = tk.LabelFrame(self.mid_frame, text=" 高度な自動検知 ")
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(
            auto_frame,
            text="氏名・住所・日付・口座を一括検知 ↓",
            bg="#e0e0e0",
            fg="black",
            highlightbackground="#CCCCCC",
            command=self.auto_extract,
        ).pack(fill=tk.X, padx=5, pady=5)

        # 手動追加
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
            highlightbackground="#CCCCCC",
            command=self.add_manual_row,
        ).pack(fill=tk.X, padx=5, pady=5)

        # 置換リスト
        list_frame = tk.LabelFrame(self.mid_frame, text=" 置換リスト（案件保存可） ")
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
            list_frame, columns=("Role", "RealName", "Token"), show="headings", height=8
        )
        self.tree.heading("Role", text="種別")
        self.tree.heading("RealName", text="実名/住所/番号")
        self.tree.heading("Token", text="トークン")
        self.tree.column("Role", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Button(
            list_frame,
            text="選択行を削除",
            bg="#e0e0e0",
            fg="black",
            command=self.delete_row,
        ).pack(fill=tk.X, padx=5)

        # 3. 右カラム：出力 ＆ 復元
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

        # メインアクションボタン
        act_frame = tk.Frame(self.mid_frame)
        act_frame.pack(fill=tk.X, pady=10)
        tk.Button(
            act_frame,
            text="匿名化 ➔ コピー ➔ 入力消去",
            bg="#A5D6A7",
            fg="black",
            highlightbackground="#A5D6A7",
            font=("MS Gothic", 11, "bold"),
            height=3,
            command=self.run_full_process,
        ).pack(fill=tk.X, padx=5)

        tk.Button(
            self.right_frame,
            text="AI回答を実名に復元",
            bg="#90CAF9",
            fg="black",
            highlightbackground="#90CAF9",
            font=("MS Gothic", 10, "bold"),
            height=2,
            command=self.run_restore,
        ).pack(fill=tk.X, padx=5, pady=5)
        self.paned.add(self.right_frame, width=450)

        # 免責事項エリア
        disclaimer = "【免責事項】本ツールは100%の匿名化を保証しません。送信前に必ず目視確認を行ってください。"
        tk.Label(root, text=disclaimer, fg="#CC0000", font=("MS Gothic", 10)).pack(
            side=tk.BOTTOM, fill=tk.X
        )

    # --- ロジック ---
    def auto_extract(self):
        text = self.txt_input.get("1.0", tk.END)
        existing = [self.tree.item(i)["values"][1] for i in self.tree.get_children()]
        name_kws = [
            "遺言者",
            "被相続人",
            "相続人",
            "受遺者",
            "遺言執行者",
            "証人",
            "立会人",
        ]
        for kw in name_kws:
            p = rf"{kw}\s*[:：]?\s*([^\s、。]{{2,15}}?)(?:\s|、|。|\n|$)"
            for m in re.finditer(p, text):
                name = m.group(1).strip()
                if name not in existing:
                    self.tree.insert(
                        "", "end", values=(kw, name, f"[{kw}_{len(existing) + 1}]")
                    )
                    existing.append(name)
        addr_p = r"(?:東京都|北海道|京都府|大阪府|.{2,3}県)[^ \n\r]{2,30}?(?:[0-9０-９]+(?:[ー－ｰ\-－丁目番地号]))+[0-9０-９]*"
        for addr in set(re.findall(addr_p, text)):
            if addr not in existing:
                self.tree.insert(
                    "", "end", values=("住所", addr, f"[住所_{len(existing) + 1}]")
                )
                existing.append(addr)
        date_p = r"(?:(?:昭和|平成|令和)[0-9０-９元]+年|[0-9]{4}年?|(?:\d{2,4})[-/])[0-9０-９]{1,2}[-/月][0-9０-９]{1,2}日?"
        for d in set(re.findall(date_p, text)):
            if d not in existing:
                self.tree.insert(
                    "", "end", values=("日付", d, f"[日付_{len(existing) + 1}]")
                )
                existing.append(d)
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
        risky_keywords = ["市", "町", "番地", "様"]
        found_risks = [k for k in risky_keywords if k in masked_text]
        if found_risks:
            if not messagebox.askyesno(
                "確認",
                f"出力内に '{found_risks[0]}' 等の文字が残っています。続行しますか？",
            ):
                return
        self.root.clipboard_clear()
        self.root.clipboard_append(masked_text)
        self.write_log()
        self.txt_input.delete("1.0", tk.END)
        messagebox.showinfo("完了", "コピー完了。入力欄を消去しました。")

    def write_log(self):
        with open(self.log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"--- Processed at {timestamp} ---\n")
            for item in self.tree.get_children():
                role, real, token = self.tree.item(item)["values"]
                f.write(f"[{role}] {token} -> {real}\n")
            f.write("\n")

    def run_masking(self):
        raw_text = self.txt_input.get("1.0", tk.END)
        self.mask_map = {}
        items = self.tree.get_children()
        masked_text = raw_text
        for item in items:
            _, real, token = self.tree.item(item)["values"]
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


if __name__ == "__main__":
    root = tk.Tk()
    app = InheritanceMaskerPro(root)
    root.mainloop()
```

## File: .github/workflows/build.yml
```yaml
cat <<EOF > .github/workflows/build.yml
name: Build Windows EXE
"on":
  push:
    branches:
      - main

jobs:
  build:
    runs-on: windows-latest

    steps:
    - name: コードを取得
      uses: actions/checkout@v4

    - name: Pythonをセットアップ
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: 必要なツールをインストール
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller

    - name: EXEを作成 (PyInstaller実行)
      run: |
        pyinstaller --onefile --noconsole --name 相続AI匿名化ツール --clean inheritance_guard.py

    - name: 成果物を保存
      uses: actions/upload-artifact@v4
      with:
        name: Windows-EXE-Package
        path: dist/相続AI匿名化ツール.exe
EOF
```
