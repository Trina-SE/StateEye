import argparse
import json
import os
import threading
import time
import webbrowser
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from tkinter import (
	Tk,
	StringVar,
	IntVar,
	END,
	Listbox,
	Text,
	Scrollbar,
	Frame,
	Label,
	Entry,
	Button,
	Radiobutton,
	Canvas,
	filedialog,
	messagebox,
	font as tkfont,
)
import subprocess
import http.server
import socketserver
import functools
import re

# ── Color Palette ──────────────────────────────────────────────────────
BG_DARK = "#1e1e2e"
BG_CARD = "#2a2a3d"
BG_INPUT = "#363650"
FG_MAIN = "#e0e0f0"
FG_DIM = "#8888aa"
FG_HEADING = "#ffffff"
ACCENT_BLUE = "#5b9bd5"
ACCENT_GREEN = "#50c878"
ACCENT_RED = "#e05555"
ACCENT_ORANGE = "#f0a040"
ACCENT_PURPLE = "#b07cd8"
ACCENT_CYAN = "#40d0d0"
BORDER_COLOR = "#3a3a55"


class ElementExtractor(HTMLParser):
	def __init__(self):
		super().__init__()
		self.elements = []
		self._button_attrs = None
		self._button_text = []

	def handle_starttag(self, tag, attrs):
		attr_map = dict(attrs)
		if tag == "a" and attr_map.get("href"):
			label = self._build_label("a", attr_map, href=attr_map.get("href"))
			self.elements.append(label)
		elif tag == "button":
			self._button_attrs = attr_map
			self._button_text = []
		elif tag == "input":
			input_type = attr_map.get("type", "").lower()
			if input_type in ("button", "submit"):
				label = self._build_label("input", attr_map, input_type=input_type)
				self.elements.append(label)

	def handle_data(self, data):
		if self._button_attrs is not None:
			text = data.strip()
			if text:
				self._button_text.append(text)

	def handle_endtag(self, tag):
		if tag == "button" and self._button_attrs is not None:
			text = " ".join(self._button_text).strip()
			label = self._build_label("button", self._button_attrs, text=text)
			self.elements.append(label)
			self._button_attrs = None
			self._button_text = []

	def _build_label(self, tag, attrs, text="", href="", input_type=""):
		parts = [tag]
		if input_type:
			parts.append(f"[{input_type}]")
		if attrs.get("id"):
			parts.append(f"#{attrs.get('id')}")
		elif attrs.get("name"):
			parts.append(f"[name={attrs.get('name')}]")
		elif href:
			parts.append(f"[href={href}]")
		if text:
			parts.append(f"[text={text}]")
		return "".join(parts)


@dataclass
class ManualSession:
	url: str = ""
	untested: list = field(default_factory=list)
	tested: list = field(default_factory=list)
	edges: list = field(default_factory=list)


class DemoServer:
	def __init__(self, directory, click_callback):
		self.directory = directory
		self.click_callback = click_callback
		self.httpd = None
		self.port = None
		self.thread = None

	def start(self):
		handler = self._build_handler()
		self.httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
		self.httpd.allow_reuse_address = True
		self.port = self.httpd.server_address[1]
		self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
		self.thread.start()

	def stop(self):
		if self.httpd:
			self.httpd.shutdown()
			self.httpd.server_close()
			self.httpd = None
			self.thread = None

	def _build_handler(self):
		click_callback = self.click_callback
		directory = self.directory

		class InjectingHandler(http.server.SimpleHTTPRequestHandler):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, directory=directory, **kwargs)

			def do_POST(self):
				if self.path != "/stateeye_click":
					self.send_response(404)
					self.end_headers()
					return
				length = int(self.headers.get("Content-Length", "0"))
				body = self.rfile.read(length) if length else b"{}"
				try:
					data = json.loads(body.decode("utf-8"))
				except Exception:
					data = {}
				label = data.get("label")
				if label:
					click_callback(label)
				self.send_response(204)
				self.end_headers()

			def do_GET(self):
				if self.path == "/stateeye_inject.js":
					self.send_response(200)
					self.send_header("Content-Type", "application/javascript; charset=utf-8")
					self.end_headers()
					self.wfile.write(self._inject_script().encode("utf-8"))
					return
				return super().do_GET()

			def send_head(self):
				path = self.translate_path(self.path)
				if path.lower().endswith(".html") and os.path.exists(path):
					try:
						with open(path, "r", encoding="utf-8", errors="ignore") as f:
							content = f.read()
					except Exception:
						return super().send_head()
					inject_tag = "<script src=\"/stateeye_inject.js\"></script>"
					if "</body>" in content:
						content = content.replace("</body>", inject_tag + "\n</body>")
					else:
						content = content + "\n" + inject_tag
					encoded = content.encode("utf-8", errors="ignore")
					self.send_response(200)
					self.send_header("Content-Type", "text/html; charset=utf-8")
					self.send_header("Content-Length", str(len(encoded)))
					self.end_headers()
					self.wfile.write(encoded)
					return None
				return super().send_head()

			def _inject_script(self):
				return (
					"(function(){"
					"function buildLabel(el){"
					"var tag=el.tagName.toLowerCase();"
					"var id=el.id?('#'+el.id):'';"
					"var name=el.getAttribute('name');"
					"var href=el.getAttribute('href');"
					"var type=el.getAttribute('type');"
					"var text=(el.innerText||'').trim().replace(/\\s+/g,' ');"
					"var parts=[tag];"
					"if(type){parts.push('['+type+']');}"
					"if(id){parts.push(id);}else if(name){parts.push('[name='+name+']');}"
					"else if(href){parts.push('[href='+href+']');}"
					"if(text){parts.push('[text='+text+']');}"
					"return parts.join('');}"
					"function findClickable(el){"
					"if(!el) return null;"
					"var tag=el.tagName?el.tagName.toLowerCase():'';"
					"if(tag==='a'||tag==='button') return el;"
					"if(tag==='input'){"
					"var type=(el.getAttribute('type')||'').toLowerCase();"
					"if(type==='button'||type==='submit') return el;}"
					"return el.closest('a,button,input[type=button],input[type=submit]');}"
					"document.addEventListener('click',function(e){"
					"var el=findClickable(e.target);"
					"if(!el) return;"
					"var label=buildLabel(el);"
					"fetch('/stateeye_click',{method:'POST',headers:{'Content-Type':'application/json'},"
					"body:JSON.stringify({label:label})});"
					"},true);"
					"})();"
				)

		return InjectingHandler


# ── Helper: rounded rectangle on Canvas ───────────────────────────────
def _round_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
	points = [
		x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
		x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius,
		x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
		x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius,
		x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1,
	]
	return canvas.create_polygon(points, smooth=True, **kwargs)


# ── Styled widgets ────────────────────────────────────────────────────
def _styled_frame(parent, **kw):
	kw.setdefault("bg", BG_DARK)
	return Frame(parent, **kw)


def _card_frame(parent, **kw):
	kw.setdefault("bg", BG_CARD)
	kw.setdefault("highlightbackground", BORDER_COLOR)
	kw.setdefault("highlightthickness", 1)
	kw.setdefault("padx", 12)
	kw.setdefault("pady", 10)
	return Frame(parent, **kw)


def _label(parent, text, color=FG_MAIN, size=10, bold=False, **kw):
	weight = "bold" if bold else "normal"
	kw.setdefault("bg", parent.cget("bg"))
	return Label(parent, text=text, fg=color, font=("Segoe UI", size, weight), **kw)


def _entry(parent, textvariable, width=40):
	return Entry(
		parent, textvariable=textvariable, width=width,
		bg=BG_INPUT, fg=FG_MAIN, insertbackground=FG_MAIN,
		relief="flat", font=("Consolas", 10),
		highlightbackground=BORDER_COLOR, highlightthickness=1,
	)


def _btn(parent, text, command, color=ACCENT_BLUE, wide=False):
	w = 18 if wide else 12
	return Button(
		parent, text=text, command=command,
		bg=color, fg="#ffffff", activebackground=color,
		activeforeground="#ffffff", relief="flat", cursor="hand2",
		font=("Segoe UI", 10, "bold"), width=w, pady=4,
	)


def _radio(parent, text, variable, value):
	return Radiobutton(
		parent, text=text, variable=variable, value=value,
		bg=parent.cget("bg"), fg=FG_MAIN, selectcolor=BG_INPUT,
		activebackground=parent.cget("bg"), activeforeground=ACCENT_CYAN,
		font=("Segoe UI", 10), indicatoron=True,
	)


# ── Status badge ──────────────────────────────────────────────────────
class StatusBadge(Frame):
	def __init__(self, parent, **kw):
		super().__init__(parent, bg=parent.cget("bg"), **kw)
		self.dot = Canvas(self, width=14, height=14, bg=parent.cget("bg"), highlightthickness=0)
		self.dot.pack(side="left", padx=(0, 6))
		self._oval = self.dot.create_oval(2, 2, 12, 12, fill=FG_DIM, outline="")
		self.lbl = _label(self, "Idle", color=FG_DIM, size=10, bold=True)
		self.lbl.pack(side="left")

	def set(self, text, color):
		self.dot.itemconfig(self._oval, fill=color)
		self.lbl.config(text=text, fg=color)


# ── Stats card ────────────────────────────────────────────────────────
class StatCard(Frame):
	def __init__(self, parent, title, value="0", color=ACCENT_BLUE, font_size=22, **kw):
		super().__init__(parent, bg=BG_CARD, highlightbackground=color,
						 highlightthickness=2, padx=14, pady=8, **kw)
		_label(self, title, color=FG_DIM, size=9).pack(anchor="w")
		self.val_lbl = _label(self, value, color=color, size=font_size, bold=True)
		self.val_lbl.pack(anchor="w")

	def set_value(self, value):
		self.val_lbl.config(text=str(value))


# ── Main GUI ──────────────────────────────────────────────────────────
class StateEyeGUI:
	def __init__(self, root):
		self.root = root
		self.root.title("StateEye")
		self.root.configure(bg=BG_DARK)
		self.root.minsize(900, 700)

		# Try to make it reasonably large
		self.root.geometry("1060x780")

		self.mode = StringVar(value="auto")
		self.target = StringVar()
		self.runtime_mins = StringVar(value="1")
		self.max_depth = StringVar(value="5")
		self.max_states = StringVar(value="50")
		self.credentials_path = StringVar()
		self.log_text = None
		self.untested_list = None
		self.tested_list = None
		self.manual_session = ManualSession()
		self.server = None
		self.auto_proc = None
		self.run_dir = None
		self.summary_text = None
		self.last_exit_status = None
		self.hard_timeout_grace_secs = 30

		# Stats
		self.states_found = 0
		self.actions_done = 0
		self.crawl_start_time = None
		# Live classification tracking (from [classify] lines)
		self._live_clones = 0
		self._live_near_dup = 0
		self._live_unique = 0
		self._has_live_classify = False

		self.build_ui()

	# ── UI Construction ───────────────────────────────────────────────
	def build_ui(self):
		# ── Title bar ─────────────────────────────────────────────────
		title_bar = _styled_frame(self.root)
		title_bar.pack(fill="x", padx=16, pady=(14, 4))

		eye_icon = _label(title_bar, "\u25c9", color=ACCENT_CYAN, size=20, bold=True)
		eye_icon.pack(side="left", padx=(0, 8))
		_label(title_bar, "StateEye", color=FG_HEADING, size=18, bold=True).pack(side="left")
		_label(title_bar, "Fragment-Based Web Regression Testing", color=FG_DIM, size=10).pack(side="left", padx=(12, 0))

		self.status_badge = StatusBadge(title_bar)
		self.status_badge.pack(side="right")

		# ── Separator ─────────────────────────────────────────────────
		sep = Frame(self.root, bg=BORDER_COLOR, height=1)
		sep.pack(fill="x", padx=16, pady=(6, 10))

		# ── Target input card ─────────────────────────────────────────
		target_card = _card_frame(self.root)
		target_card.pack(fill="x", padx=16, pady=(0, 8))

		_label(target_card, "TARGET", color=ACCENT_BLUE, size=9, bold=True).pack(anchor="w")
		input_row = _styled_frame(target_card)
		input_row.configure(bg=BG_CARD)
		input_row.pack(fill="x", pady=(4, 0))
		_label(input_row, "URL or HTML path:", color=FG_DIM, size=10).pack(side="left")
		_entry(input_row, self.target, width=55).pack(side="left", padx=8)
		_btn(input_row, "Browse", self.browse_file, color=BG_INPUT).pack(side="left")

		# ── Config row ────────────────────────────────────────────────
		config_card = _card_frame(self.root)
		config_card.pack(fill="x", padx=16, pady=(0, 8))

		top_cfg = _styled_frame(config_card)
		top_cfg.configure(bg=BG_CARD)
		top_cfg.pack(fill="x")

		# Mode
		mode_frame = _styled_frame(top_cfg)
		mode_frame.configure(bg=BG_CARD)
		mode_frame.pack(side="left")
		_label(mode_frame, "MODE", color=ACCENT_PURPLE, size=9, bold=True).pack(anchor="w")
		_radio(mode_frame, "Automated", self.mode, "auto").pack(side="left")
		_radio(mode_frame, "Manual", self.mode, "manual").pack(side="left", padx=(8, 0))

		# Params
		param_frame = _styled_frame(top_cfg)
		param_frame.configure(bg=BG_CARD)
		param_frame.pack(side="right")

		for lbl_text, var, clr in [
			("Runtime (min)", self.runtime_mins, ACCENT_ORANGE),
			("Max depth", self.max_depth, ACCENT_CYAN),
			("Max states", self.max_states, ACCENT_GREEN),
		]:
			f = _styled_frame(param_frame)
			f.configure(bg=BG_CARD)
			f.pack(side="left", padx=(16, 0))
			_label(f, lbl_text, color=clr, size=9, bold=True).pack(anchor="w")
			_entry(f, var, width=6).pack()

		# Credentials file
		cred_frame = _styled_frame(config_card)
		cred_frame.configure(bg=BG_CARD)
		cred_frame.pack(fill="x", pady=(6, 0))
		_label(cred_frame, "CREDENTIALS FILE", color=ACCENT_ORANGE, size=9, bold=True).pack(side="left")
		_entry(cred_frame, self.credentials_path, width=36).pack(side="left", padx=8)
		_btn(cred_frame, "Browse", self.browse_credentials, color=BG_INPUT).pack(side="left")
		_label(cred_frame, "(optional - for login/signup)", color=FG_DIM, size=9).pack(side="left", padx=8)

		# ── Action buttons ────────────────────────────────────────────
		btn_row = _styled_frame(self.root)
		btn_row.pack(fill="x", padx=16, pady=(0, 8))

		_btn(btn_row, "\u25b6  Start", self.start, color=ACCENT_GREEN, wide=True).pack(side="left")
		_btn(btn_row, "\u25a0  Stop", self.stop, color=ACCENT_RED).pack(side="left", padx=8)
		_btn(btn_row, "Generate Tests", self.generate_tests, color=ACCENT_PURPLE, wide=True).pack(side="left")

		# ── Stats row ─────────────────────────────────────────────────
		stats_row = _styled_frame(self.root)
		stats_row.pack(fill="x", padx=16, pady=(0, 8))

		self.stat_states = StatCard(stats_row, "States Found", "0", ACCENT_BLUE)
		self.stat_states.pack(side="left", fill="x", expand=True, padx=(0, 6))
		self.stat_actions = StatCard(stats_row, "Actions Performed", "0", ACCENT_GREEN)
		self.stat_actions.pack(side="left", fill="x", expand=True, padx=(0, 6))
		self.stat_elapsed = StatCard(stats_row, "Elapsed", "0s", ACCENT_ORANGE)
		self.stat_elapsed.pack(side="left", fill="x", expand=True, padx=(0, 6))
		self.stat_status = StatCard(stats_row, "Classification", "--", ACCENT_PURPLE, font_size=12)
		self.stat_status.pack(side="left", fill="x", expand=True)

		# ── Main content area (log + side panels) ─────────────────────
		content = _styled_frame(self.root)
		content.pack(fill="both", expand=True, padx=16, pady=(0, 8))

		# Left: live log
		log_card = _card_frame(content)
		log_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

		_label(log_card, "LIVE CRAWL OUTPUT", color=ACCENT_CYAN, size=9, bold=True).pack(anchor="w", pady=(0, 4))
		log_inner = _styled_frame(log_card)
		log_inner.configure(bg=BG_CARD)
		log_inner.pack(fill="both", expand=True)

		self.log_text = Text(
			log_inner, height=14, wrap="word",
			bg="#1a1a2a", fg=ACCENT_GREEN, insertbackground=ACCENT_GREEN,
			font=("Consolas", 9), relief="flat", borderwidth=0,
			highlightbackground=BORDER_COLOR, highlightthickness=1,
		)
		scroll = Scrollbar(log_inner, command=self.log_text.yview, bg=BG_CARD, troughcolor=BG_DARK)
		self.log_text.configure(yscrollcommand=scroll.set)
		self.log_text.pack(side="left", fill="both", expand=True)
		scroll.pack(side="left", fill="y")

		# Configure log text tags for colored output
		self.log_text.tag_config("info", foreground=ACCENT_CYAN)
		self.log_text.tag_config("success", foreground=ACCENT_GREEN)
		self.log_text.tag_config("warn", foreground=ACCENT_ORANGE)
		self.log_text.tag_config("error", foreground=ACCENT_RED)
		self.log_text.tag_config("state", foreground=ACCENT_BLUE)
		self.log_text.tag_config("dim", foreground=FG_DIM)
		self.log_text.tag_config("classify", foreground=ACCENT_PURPLE)

		# Right: summary + element lists
		right_panel = _styled_frame(content)
		right_panel.pack(side="left", fill="both", expand=False)

		# Summary
		sum_card = _card_frame(right_panel)
		sum_card.pack(fill="x", pady=(0, 8))
		_label(sum_card, "SUMMARY", color=ACCENT_ORANGE, size=9, bold=True).pack(anchor="w", pady=(0, 4))
		self.summary_text = Text(
			sum_card, height=7, width=36, wrap="word",
			bg="#1a1a2a", fg=FG_MAIN, font=("Consolas", 9),
			relief="flat", borderwidth=0,
			highlightbackground=BORDER_COLOR, highlightthickness=1,
		)
		self.summary_text.pack(fill="x")

		# Untested
		untested_card = _card_frame(right_panel)
		untested_card.pack(fill="both", expand=True, pady=(0, 8))
		_label(untested_card, "UNTESTED ELEMENTS", color=ACCENT_RED, size=9, bold=True).pack(anchor="w", pady=(0, 4))
		self.untested_list = Listbox(
			untested_card, height=5, bg="#1a1a2a", fg=ACCENT_ORANGE,
			font=("Consolas", 9), relief="flat", borderwidth=0,
			selectbackground=ACCENT_BLUE, selectforeground="#ffffff",
			highlightbackground=BORDER_COLOR, highlightthickness=1,
		)
		self.untested_list.pack(fill="both", expand=True)
		self.untested_list.bind("<Double-Button-1>", lambda _e: self.mark_tested())
		_btn(untested_card, "Mark Tested", self.mark_tested, color=ACCENT_GREEN).pack(pady=(6, 0))

		# Tested
		tested_card = _card_frame(right_panel)
		tested_card.pack(fill="both", expand=True)
		_label(tested_card, "TESTED ELEMENTS", color=ACCENT_GREEN, size=9, bold=True).pack(anchor="w", pady=(0, 4))
		self.tested_list = Listbox(
			tested_card, height=5, bg="#1a1a2a", fg=ACCENT_GREEN,
			font=("Consolas", 9), relief="flat", borderwidth=0,
			selectbackground=ACCENT_BLUE, selectforeground="#ffffff",
			highlightbackground=BORDER_COLOR, highlightthickness=1,
		)
		self.tested_list.pack(fill="both", expand=True)

	# ── Logging ───────────────────────────────────────────────────────
	def log(self, message, tag=None):
		timestamp = time.strftime("%H:%M:%S")
		self.log_text.insert(END, f"[{timestamp}] ", "dim")
		self.log_text.insert(END, message + "\n", tag)
		self.log_text.see(END)

	def _parse_and_log_line(self, line):
		"""Parse structured crawl output lines by prefix and update stat cards."""
		# [classify] lines: update classification stats in real-time
		if line.startswith("[classify]"):
			m = re.search(r'unique=(\d+)\s+clones=(\d+)\s+near-dup=(\d+)', line)
			if m:
				self._live_unique = int(m.group(1))
				self._live_clones = int(m.group(2))
				self._live_near_dup = int(m.group(3))
				self._has_live_classify = True
				self.stat_status.set_value(
					f"Clones: {self._live_clones} | Near-Dup: {self._live_near_dup} | Unique: {self._live_unique}"
				)
			self.log(line, "classify")
			return

		# [state] lines: page captured with component count
		# Format: [state] [0m 04s] Page #1: 6 components at depth 0: URL
		if line.startswith("[state]"):
			m_comp = re.search(r'(\d+)\s+components', line)
			if m_comp:
				self.states_found += int(m_comp.group(1))
			else:
				self.states_found += 1
			self.stat_states.set_value(self.states_found)
			self.log(line, "state")
			return

		# [click] lines: action performed during replay
		if line.startswith("[click]"):
			self.actions_done += 1
			self.stat_actions.set_value(self.actions_done)
			self.log(line, "success")
			return

		# [action] lines: actionable elements found/enqueued
		if line.startswith("[action]"):
			self.log(line, "success")
			return

		# [visit] lines: page navigation
		if line.startswith("[visit]"):
			self.log(line, "info")
			return

		# [warn] lines: loop prevention, timeouts, etc.
		if line.startswith("[warn]"):
			self.log(line, "warn")
			return

		# [crawl] lines: start/finish and config
		# Finish format: [crawl] [...] Finished. 3 pages, 16 components | unique=10 ...
		if line.startswith("[crawl]"):
			if "Finished" in line:
				m = re.search(r'unique=(\d+)\s+clones=(\d+)\s+near-dup=(\d+)', line)
				if m:
					u, c, nd = m.group(1), m.group(2), m.group(3)
					self.stat_status.set_value(f"Clones: {c} | Near-Dup: {nd} | Unique: {u}")
				m_comp = re.search(r'(\d+)\s+components', line)
				if m_comp:
					self.stat_states.set_value(int(m_comp.group(1)))
			self.log(line, "info")
			return

		# Fallback for unstructured output
		lower = line.lower()
		if "error" in lower or "traceback" in lower or "failed" in lower:
			self.log(line, "error")
		else:
			self.log(line)

	# ── File browse ───────────────────────────────────────────────────
	def browse_file(self):
		path = filedialog.askopenfilename(
			title="Select HTML file",
			filetypes=[("HTML files", "*.html;*.htm"), ("All files", "*.*")],
		)
		if path:
			self.target.set(path)

	def browse_credentials(self):
		path = filedialog.askopenfilename(
			title="Select credentials file",
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
		)
		if path:
			self.credentials_path.set(path)

	# ── Start / Stop ─────────────────────────────────────────────────
	def start(self):
		target = self.target.get().strip()
		if not target:
			messagebox.showerror("StateEye", "Please enter a URL or HTML file path.")
			return
		self.log(f"Mode: {self.mode.get()}", "info")
		if self.mode.get() == "auto":
			self.start_automated(target)
		else:
			self.start_manual(target)

	def stop(self):
		if self.auto_proc and self.auto_proc.poll() is None:
			self.auto_proc.terminate()
			self.log("Crawl stopped by user.", "warn")
			self.status_badge.set("Stopped", ACCENT_ORANGE)
		if self.server:
			self.server.stop()
			self.server = None

	# ── Automated crawl ──────────────────────────────────────────────
	def start_automated(self, target):
		self.status_badge.set("Crawling...", ACCENT_GREEN)
		self.states_found = 0
		self.actions_done = 0
		self._live_clones = 0
		self._live_near_dup = 0
		self._live_unique = 0
		self._has_live_classify = False
		self.stat_states.set_value(0)
		self.stat_actions.set_value(0)
		self.stat_elapsed.set_value("0s")
		self.stat_status.set_value("--")
		self.crawl_start_time = time.time()
		self._tick_elapsed()

		self.log("Starting automated crawl...", "info")
		run_label = time.strftime("%Y%m%d-%H%M%S")
		out_dir = Path(__file__).resolve().parents[1] / "out" / f"gui_{run_label}"
		out_dir.mkdir(parents=True, exist_ok=True)
		self.run_dir = out_dir
		mode = self.resolve_auto_mode()
		self.log(f"Crawl mode: {mode}", "info")

		args = [
			"python", "-u",
			str(Path(__file__).resolve().parent / "run_demo_crawl.py"),
			"--mode", mode,
			"--target", target,
			"--runtime-mins", self.runtime_mins.get(),
			"--max-depth", self.max_depth.get(),
			"--max-states", self.max_states.get(),
			"--output-dir", str(out_dir),
		]
		args.extend(["--host", "localhost"])
		cred = self.credentials_path.get().strip()
		if cred:
			args.extend(["--credentials", cred])
			self.log(f"Using credentials: {cred}", "info")
		self.log("Command: " + " ".join(args), "dim")

		self.auto_proc = subprocess.Popen(
			args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
			text=True, bufsize=1,
		)
		timeout_secs = self.get_runtime_secs() + self.hard_timeout_grace_secs

		# Stream output in a background thread
		threading.Thread(target=self._stream_output, args=(self.auto_proc,), daemon=True).start()
		threading.Thread(target=self.enforce_hard_timeout, args=(self.auto_proc, timeout_secs), daemon=True).start()
		threading.Thread(target=self.wait_for_auto_completion, args=(self.auto_proc, out_dir), daemon=True).start()

	def _stream_output(self, proc):
		"""Read subprocess stdout line by line and push to the log."""
		try:
			for line in proc.stdout:
				line = line.rstrip("\n\r")
				if line:
					self.root.after(0, lambda l=line: self._parse_and_log_line(l))
		except Exception:
			pass

	def _tick_elapsed(self):
		"""Update the elapsed timer every second while crawling."""
		if self.crawl_start_time and self.auto_proc and self.auto_proc.poll() is None:
			elapsed = int(time.time() - self.crawl_start_time)
			mins, secs = divmod(elapsed, 60)
			self.stat_elapsed.set_value(f"{mins}m {secs}s" if mins else f"{secs}s")
			self.root.after(1000, self._tick_elapsed)

	# ── Manual mode ──────────────────────────────────────────────────
	def start_manual(self, target):
		self.status_badge.set("Manual Testing", ACCENT_PURPLE)
		self.log("Manual mode: parsing page and launching browser.", "info")
		self.manual_session = ManualSession()

		url = target
		if os.path.exists(target):
			path = Path(target).resolve()
			if path.is_dir():
				path = path / "index.html"
			if not path.exists():
				messagebox.showerror("StateEye", f"Missing HTML file: {path}")
				return
			self.server = DemoServer(str(path.parent), self.on_manual_click)
			self.server.start()
			url = f"http://127.0.0.1:{self.server.port}/{path.name}"

		self.manual_session.url = url
		self.manual_session.untested = self.extract_elements(target, url)
		self.manual_session.tested = []
		self.manual_session.edges = []
		self.refresh_lists()
		self.summary_text.delete("1.0", END)
		self.summary_text.insert(END, "Manual mode active.\nClick elements in the browser.\n")
		webbrowser.open(url)
		self.log(f"Opened {url}", "info")

	def extract_elements(self, target, url):
		try:
			if os.path.exists(target):
				content = Path(target).read_text(encoding="utf-8", errors="ignore")
			else:
				self.log("Manual mode uses local HTML for element guidance.", "dim")
				content = ""
		except Exception as exc:
			self.log(f"Failed to parse HTML: {exc}", "error")
			content = ""
		parser = ElementExtractor()
		parser.feed(content)
		seen = set()
		deduped = []
		for item in parser.elements:
			if item not in seen:
				seen.add(item)
				deduped.append(item)
		if not deduped:
			self.log("No actionable elements detected.", "warn")
		return deduped

	def refresh_lists(self):
		self.untested_list.delete(0, END)
		for item in self.manual_session.untested:
			self.untested_list.insert(END, item)
		self.tested_list.delete(0, END)
		for item in self.manual_session.tested:
			self.tested_list.insert(END, item)

	def on_manual_click(self, label):
		def update():
			if label in self.manual_session.untested:
				self.manual_session.untested.remove(label)
				self.manual_session.tested.append(label)
			elif label not in self.manual_session.tested:
				self.manual_session.tested.append(label)
			self.manual_session.edges.append(
				{
					"from": f"state{max(len(self.manual_session.tested)-1,0)}",
					"action": label,
					"to": f"state{len(self.manual_session.tested)}",
				}
			)
			self.refresh_lists()
			self.summary_text.delete("1.0", END)
			self.summary_text.insert(
				END,
				f"Manual summary:\nTested: {len(self.manual_session.tested)}\n"
				f"Untested: {len(self.manual_session.untested)}\n",
			)
		self.root.after(0, update)

	def mark_tested(self):
		selection = self.untested_list.curselection()
		if not selection:
			return
		idx = selection[0]
		item = self.manual_session.untested.pop(idx)
		self.manual_session.tested.append(item)
		if self.manual_session.tested:
			self.manual_session.edges.append(
				{
					"from": "state0",
					"action": item,
					"to": f"state{len(self.manual_session.tested)}",
				}
			)
		self.refresh_lists()

	# ── Generate tests ───────────────────────────────────────────────
	def generate_tests(self):
		run_label = time.strftime("%Y%m%d-%H%M%S")
		out_dir = Path(__file__).resolve().parents[1] / "out" / f"gui_manual_{run_label}"
		out_dir.mkdir(parents=True, exist_ok=True)
		if self.mode.get() == "manual":
			data = {
				"url": self.manual_session.url,
				"tested_actions": self.manual_session.tested,
				"edges": self.manual_session.edges,
			}
			out_file = out_dir / "manual_test_plan.json"
			out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
			self.log(f"Manual test plan saved to {out_file}", "success")
			self.summary_text.delete("1.0", END)
			self.summary_text.insert(
				END,
				f"Manual summary:\nTested: {len(self.manual_session.tested)}\n"
				f"Untested: {len(self.manual_session.untested)}\n"
				f"Plan: {out_file}",
			)
		else:
			self.log("Automated mode: tests are in the crawl output directory.", "info")
		messagebox.showinfo("StateEye", f"Output saved under {out_dir}")

	# ── Auto completion handling ─────────────────────────────────────
	def wait_for_auto_completion(self, proc, out_dir):
		exit_code = proc.wait()
		# Don't clear crawl_start_time here — let on_auto_complete do it
		# so the final elapsed update works correctly.
		self.root.after(0, lambda: self.on_auto_complete(exit_code, out_dir))

	def enforce_hard_timeout(self, proc, timeout_secs):
		start = time.time()
		while proc.poll() is None:
			if time.time() - start > timeout_secs:
				proc.terminate()
				self.root.after(
					0,
					lambda: self.log(
						f"Hard timeout reached ({timeout_secs}s). Process terminated.",
						"error",
					),
				)
				return
			time.sleep(1)

	def get_runtime_secs(self):
		try:
			return int(self.runtime_mins.get()) * 60
		except Exception:
			return 60

	def resolve_auto_mode(self):
		return "hybrid"

	def on_auto_complete(self, exit_code, out_dir):
		if exit_code == 0:
			self.log("Crawl completed successfully!", "success")
			self.status_badge.set("Complete", ACCENT_GREEN)
		else:
			self.log(f"Crawl exited with code {exit_code}.", "error")
			self.status_badge.set("Error", ACCENT_RED)

		# Update elapsed one last time, then clear the timer
		if self.crawl_start_time:
			elapsed = int(time.time() - self.crawl_start_time)
			mins, secs = divmod(elapsed, 60)
			self.stat_elapsed.set_value(f"{mins}m {secs}s" if mins else f"{secs}s")
		self.crawl_start_time = None

		summary = self.build_summary(out_dir)
		self.summary_text.delete("1.0", END)
		self.summary_text.insert(END, summary)
		if self.last_exit_status == "EXHAUSTED":
			message = "Testing finished: successfully explored available actions."
		else:
			message = "Testing finished. Summary updated."
		messagebox.showinfo("StateEye", message)

	def build_summary(self, out_dir):
		out_dir = Path(out_dir)
		result_path = next(out_dir.rglob("result.json"), None)
		test_path = next(out_dir.rglob("generated_tests.py"), None)
		lines = []
		lines.append(f"Output: {out_dir}")
		if not out_dir.exists():
			lines.append("Output folder: not found")
		if result_path is None:
			lines.append("result.json: not found")
			# Only search within the current output directory, not parent dirs
			candidates = list(out_dir.rglob("result.json"))
			if candidates:
				candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
				result_path = candidates[0]
				lines.append(f"Found: {result_path}")
			else:
				lines.append("No crawl result produced.")
				return "\n".join(lines)
		try:
			data = json.loads(result_path.read_text(encoding="utf-8", errors="ignore"))
		except Exception as exc:
			lines.append(f"Parse error: {exc}")
			return "\n".join(lines)

		states = data.get("states", {})
		stats = data.get("statistics", {}).get("stateStats", {})
		total_pages = stats.get("totalNumberOfStates", len(states))
		exit_status = data.get("exitStatus", "unknown")
		self.last_exit_status = exit_status
		lines.append(f"Exit: {exit_status}")
		lines.append(f"Pages: {total_pages}")

		# Show component count from live data, fallback to page count
		if self.states_found > 0:
			lines.append(f"Components: {self.states_found}")
		else:
			self.stat_states.set_value(total_pages)

		# Use live classification from the crawler (consistent with stat card)
		if self._has_live_classify:
			lines.append(f"Clones: {self._live_clones}")
			lines.append(f"Near-dups: {self._live_near_dup}")
			lines.append(f"Unique: {self._live_unique}")
		else:
			# Fallback: run post-crawl analysis
			fraggen_report = result_path.parent / "fraggen_classification.json"
			if not fraggen_report.exists():
				try:
					script = Path(__file__).resolve().parent / "fraggen_analysis.py"
					subprocess.run(
						["python", str(script), "--crawl-dir", str(result_path.parent)],
						check=True,
						capture_output=True,
						text=True,
					)
				except Exception as exc:
					lines.append(f"Analysis failed: {exc}")
			if fraggen_report.exists():
				try:
					report = json.loads(
						fraggen_report.read_text(encoding="utf-8", errors="ignore")
					)
					frag_summary = report.get("summary", {})
					clones = frag_summary.get("clone", 0)
					nds = frag_summary.get("near_duplicates", 0)
					distinct = frag_summary.get("distinct", 0)
					lines.append(f"Clones: {clones}")
					lines.append(f"Near-dups: {nds}")
					lines.append(f"Unique: {distinct}")
					self.stat_status.set_value(f"Clones: {clones} | Near-Dup: {nds} | Unique: {distinct}")
				except Exception as exc:
					lines.append(f"Summary error: {exc}")

		if test_path is None:
			lines.append("Tests: not found")
			return "\n".join(lines)

		methods = []
		for line in test_path.read_text(encoding="utf-8", errors="ignore").splitlines():
			match = re.search(r"def (test_\w+)\(", line)
			if match:
				methods.append(match.group(1))
		if methods:
			lines.append("Tests:")
			lines.extend([f"  - {name}" for name in methods])
		else:
			lines.append("Tests: none detected")
		return "\n".join(lines)


def main():
	root = Tk()
	app = StateEyeGUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()
