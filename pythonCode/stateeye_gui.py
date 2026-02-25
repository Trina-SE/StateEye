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
		self._collect_tag = None
		self._collect_attrs = None
		self._collect_text = []

	def handle_starttag(self, tag, attrs):
		attr_map = dict(attrs)
		if tag == "a" and attr_map.get("href"):
			self._collect_tag = "a"
			self._collect_attrs = attr_map
			self._collect_text = []
		elif tag == "button":
			self._collect_tag = "button"
			self._collect_attrs = attr_map
			self._collect_text = []
		elif tag == "input":
			input_type = attr_map.get("type", "text").lower()
			label = self._build_label("input", attr_map, input_type=input_type)
			self.elements.append(label)
		elif tag == "select":
			label = self._build_label("select", attr_map)
			self.elements.append(label)
		elif tag == "textarea":
			label = self._build_label("textarea", attr_map)
			self.elements.append(label)

	def handle_data(self, data):
		if self._collect_tag is not None:
			text = data.strip()
			if text:
				self._collect_text.append(text)

	def handle_endtag(self, tag):
		if tag == self._collect_tag and self._collect_attrs is not None:
			text = " ".join(self._collect_text).strip()
			if self._collect_tag == "a":
				label = self._build_label("a", self._collect_attrs, href=self._collect_attrs.get("href", ""), text=text)
			else:
				label = self._build_label(self._collect_tag, self._collect_attrs, text=text)
			self.elements.append(label)
			self._collect_tag = None
			self._collect_attrs = None
			self._collect_text = []

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
	def __init__(self, directory, click_callback, elements_callback=None):
		self.directory = directory
		self.click_callback = click_callback
		self.elements_callback = elements_callback
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
		elements_callback = self.elements_callback
		directory = self.directory

		class InjectingHandler(http.server.SimpleHTTPRequestHandler):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, directory=directory, **kwargs)

			def do_POST(self):
				if self.path not in ("/stateeye_click", "/stateeye_elements"):
					self.send_response(404)
					self.end_headers()
					return
				length = int(self.headers.get("Content-Length", "0"))
				body = self.rfile.read(length) if length else b"{}"
				try:
					data = json.loads(body.decode("utf-8"))
				except Exception:
					data = {}
				if self.path == "/stateeye_click":
					label = data.get("label")
					if label:
						click_callback(label)
				elif self.path == "/stateeye_elements" and elements_callback:
					labels = data.get("labels", [])
					url = data.get("url", "")
					if labels:
						elements_callback(url, labels)
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
					"var text=(el.innerText||'').trim().replace(/\\s+/g,' ').substring(0,60);"
					"var parts=[tag];"
					"if(type){parts.push('['+type+']');}"
					"if(id){parts.push(id);}else if(name){parts.push('[name='+name+']');}"
					"else if(href){parts.push('[href='+href+']');}"
					"if(text){parts.push('[text='+text+']');}"
					"return parts.join('');}"
					"function findClickable(el){"
					"if(!el) return null;"
					"var tag=el.tagName?el.tagName.toLowerCase():'';"
					"if(tag==='a'||tag==='button'||tag==='select'||tag==='textarea') return el;"
					"if(tag==='input') return el;"
					"return el.closest('a,button,input,select,textarea,[role=button]');}"
					"document.addEventListener('click',function(e){"
					"var el=findClickable(e.target);"
					"if(!el) return;"
					"var label=buildLabel(el);"
					"fetch('/stateeye_click',{method:'POST',headers:{'Content-Type':'application/json'},"
					"body:JSON.stringify({label:label})});"
					"},true);"
					"window.addEventListener('load',function(){"
					"var els=document.querySelectorAll('a[href],button,input,select,textarea,[role=button]');"
					"var labels=[];"
					"els.forEach(function(el){labels.push(buildLabel(el));});"
					"fetch('/stateeye_elements',{method:'POST',headers:{'Content-Type':'application/json'},"
					"body:JSON.stringify({labels:labels,url:location.href})});"
					"});"
					"})();"
				)

		return InjectingHandler


class PlaywrightManualSession:
	"""Manages a visible Playwright browser for manual mode on remote URLs."""

	TRACKING_JS = """(function(){
function buildLabel(el){
	var tag=el.tagName.toLowerCase();
	var id=el.id?('#'+el.id):'';
	var name=el.getAttribute('name');
	var href=el.getAttribute('href');
	var type=el.getAttribute('type');
	var text=(el.innerText||'').trim().replace(/\\s+/g,' ').substring(0,60);
	var parts=[tag];
	if(type){parts.push('['+type+']');}
	if(id){parts.push(id);}else if(name){parts.push('[name='+name+']');}
	else if(href){parts.push('[href='+href+']');}
	if(text){parts.push('[text='+text+']');}
	return parts.join('');
}
function findClickable(el){
	if(!el) return null;
	var tag=el.tagName?el.tagName.toLowerCase():'';
	if(tag==='a'||tag==='button'||tag==='select'||tag==='textarea') return el;
	if(tag==='input') return el;
	return el.closest('a,button,input,select,textarea,[role=button]');
}
document.addEventListener('click',function(e){
	var el=findClickable(e.target);
	if(!el) return;
	var label=buildLabel(el);
	window.__stateeye_click(label);
},true);
window.addEventListener('load',function(){
	var els=document.querySelectorAll('a[href],button,input,select,textarea,[role=button]');
	var labels=[];
	els.forEach(function(el){labels.push(buildLabel(el));});
	window.__stateeye_elements(JSON.stringify({labels:labels,url:location.href}));
});
document.addEventListener('DOMContentLoaded',function(){
	var els=document.querySelectorAll('a[href],button,input,select,textarea,[role=button]');
	var labels=[];
	els.forEach(function(el){labels.push(buildLabel(el));});
	window.__stateeye_elements(JSON.stringify({labels:labels,url:location.href}));
});
})();"""

	def __init__(self):
		self.playwright = None
		self.browser = None
		self.context = None
		self.page = None
		self._thread = None
		self._running = False

	def start(self, url, click_callback, elements_callback):
		self._click_cb = click_callback
		self._elements_cb = elements_callback
		self._url = url
		self._running = True
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def _run(self):
		from playwright.sync_api import sync_playwright
		self.playwright = sync_playwright().start()
		self.browser = self.playwright.chromium.launch(headless=False)
		self.context = self.browser.new_context(viewport={"width": 1400, "height": 900})
		self.context.add_init_script(self.TRACKING_JS)
		self.page = self.context.new_page()
		self.page.expose_function("__stateeye_click", self._on_click)
		self.page.expose_function("__stateeye_elements", self._on_elements)
		self.page.on("popup", self._handle_new_page)
		try:
			self.page.goto(self._url, wait_until="domcontentloaded", timeout=30000)
		except Exception:
			pass
		# Keep the browser open until stopped
		while self._running and self.browser.is_connected():
			try:
				self.page.wait_for_timeout(500)
			except Exception:
				break

	def _handle_new_page(self, new_page):
		"""Inject tracking into popup/new-tab pages."""
		try:
			new_page.expose_function("__stateeye_click", self._on_click)
			new_page.expose_function("__stateeye_elements", self._on_elements)
		except Exception:
			pass

	def _on_click(self, label):
		self._click_cb(label)

	def _on_elements(self, data_json):
		try:
			data = json.loads(data_json)
			labels = data.get("labels", [])
			url = data.get("url", "")
			if labels:
				self._elements_cb(url, labels)
		except Exception:
			pass

	def stop(self):
		self._running = False
		try:
			if self.context:
				self.context.close()
		except Exception:
			pass
		try:
			if self.browser:
				self.browser.close()
		except Exception:
			pass
		try:
			if self.playwright:
				self.playwright.stop()
		except Exception:
			pass
		self.playwright = None
		self.browser = None
		self.context = None
		self.page = None


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
		self.pw_session = None
		self.auto_proc = None
		self.run_dir = None
		self.summary_text = None
		self.last_exit_status = None
		self.hard_timeout_grace_secs = 30
		# Manual mode: page-level tracking for testing/tested logic
		self._page_elements = {}   # url -> set of labels
		self._element_page = {}    # label -> url
		self._clicked = set()      # labels clicked (testing state)

		# Stats
		self.pages_found = 0
		self.fragments_found = 0
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

		self.stat_pages = StatCard(stats_row, "States", "0", ACCENT_CYAN)
		self.stat_pages.pack(side="left", fill="x", expand=True, padx=(0, 6))
		self.stat_fragments = StatCard(stats_row, "Fragments", "0", ACCENT_BLUE)
		self.stat_fragments.pack(side="left", fill="x", expand=True, padx=(0, 6))
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

		# Summary (compact)
		sum_card = _card_frame(right_panel)
		sum_card.pack(fill="x", pady=(0, 4))
		_label(sum_card, "SUMMARY", color=ACCENT_ORANGE, size=9, bold=True).pack(anchor="w", pady=(0, 2))
		self.summary_text = Text(
			sum_card, height=3, width=36, wrap="word",
			bg="#1a1a2a", fg=FG_MAIN, font=("Consolas", 9),
			relief="flat", borderwidth=0,
			highlightbackground=BORDER_COLOR, highlightthickness=1,
		)
		self.summary_text.pack(fill="x")

		# Untested (red)
		untested_card = _card_frame(right_panel)
		untested_card.pack(fill="both", expand=True, pady=(0, 4))
		_label(untested_card, "UNTESTED ELEMENTS", color=ACCENT_RED, size=9, bold=True).pack(anchor="w", pady=(0, 2))
		self.untested_list = Listbox(
			untested_card, height=6, bg="#1a1a2a", fg=ACCENT_RED,
			font=("Consolas", 9), relief="flat", borderwidth=0,
			selectbackground=ACCENT_BLUE, selectforeground="#ffffff",
			highlightbackground=BORDER_COLOR, highlightthickness=1,
		)
		self.untested_list.pack(fill="both", expand=True)
		self.untested_list.bind("<Double-Button-1>", lambda _e: self.mark_tested())
		_btn(untested_card, "Mark Tested", self.mark_tested, color=ACCENT_GREEN).pack(pady=(4, 0))

		# Tested (green)
		tested_card = _card_frame(right_panel)
		tested_card.pack(fill="both", expand=True)
		_label(tested_card, "TESTED ELEMENTS", color=ACCENT_GREEN, size=9, bold=True).pack(anchor="w", pady=(0, 2))
		self.tested_list = Listbox(
			tested_card, height=6, bg="#1a1a2a", fg=ACCENT_GREEN,
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

		# [state] lines: page captured with fragment count
		# Format: [state] [0m 04s] Page #1: 6 states at depth 0: URL
		if line.startswith("[state]"):
			self.pages_found += 1
			self.stat_pages.set_value(self.pages_found)
			m_comp = re.search(r'(\d+)\s+states', line)
			if m_comp:
				self.fragments_found += int(m_comp.group(1))
			else:
				self.fragments_found += 1
			self.stat_fragments.set_value(self.fragments_found)
			self.log(line, "state")
			return

		# [click] lines: action performed during replay
		if line.startswith("[click]"):
			self.actions_done += 1
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
		# Finish format: [crawl] [...] Finished. 3 pages, 16 states | unique=10 ...
		if line.startswith("[crawl]"):
			if "Finished" in line:
				m = re.search(r'unique=(\d+)\s+clones=(\d+)\s+near-dup=(\d+)', line)
				if m:
					u, c, nd = m.group(1), m.group(2), m.group(3)
					self.stat_status.set_value(f"Clones: {c} | Near-Dup: {nd} | Unique: {u}")
				m_pages = re.search(r'(\d+)\s+pages', line)
				if m_pages:
					self.stat_pages.set_value(int(m_pages.group(1)))
				m_comp = re.search(r'(\d+)\s+states', line)
				if m_comp:
					self.stat_fragments.set_value(int(m_comp.group(1)))
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
		if self.pw_session:
			self.pw_session.stop()
			self.pw_session = None
			self.log("Playwright browser closed.", "info")

	# ── Automated crawl ──────────────────────────────────────────────
	def start_automated(self, target):
		self.status_badge.set("Crawling...", ACCENT_GREEN)
		self.pages_found = 0
		self.fragments_found = 0
		self.actions_done = 0
		self._live_clones = 0
		self._live_near_dup = 0
		self._live_unique = 0
		self._has_live_classify = False
		self.stat_pages.set_value(0)
		self.stat_fragments.set_value(0)
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
		is_url = target.startswith(("http://", "https://"))

		if not is_url and os.path.exists(target):
			# Local HTML file — use DemoServer
			path = Path(target).resolve()
			if path.is_dir():
				path = path / "index.html"
			if not path.exists():
				messagebox.showerror("StateEye", f"Missing HTML file: {path}")
				return
			self.server = DemoServer(str(path.parent), self.on_manual_click, self.on_page_elements)
			self.server.start()
			url = f"http://127.0.0.1:{self.server.port}/{path.name}"
		elif is_url:
			# Remote URL — use Playwright with injected tracking JS
			self.pw_session = PlaywrightManualSession()
			self.pw_session.start(url, self.on_manual_click, self.on_page_elements)
			self.log("Playwright browser launching with tracking JS...", "info")

		self.manual_session.url = url
		self.manual_session.untested = self.extract_elements(target, url)
		self.manual_session.tested = []
		self.manual_session.edges = []
		self._page_elements = {}
		self._element_page = {}
		self._clicked = set()
		self._page_elements[url] = set(self.manual_session.untested)
		for label in self.manual_session.untested:
			self._element_page[label] = url
		self.refresh_lists()
		self._update_manual_summary()
		if not is_url:
			webbrowser.open(url)
		self.log(f"Opened {url}", "info")
		self.log(f"Found {len(self.manual_session.untested)} states to test", "info")

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
			self.log("No actionable states detected.", "warn")
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
			if label in self._clicked:
				return
			self._clicked.add(label)

			# If unknown element, register it as untested on an unknown page
			if label not in self.manual_session.untested and label not in self.manual_session.tested:
				self.manual_session.untested.append(label)
				self._element_page[label] = "unknown"
				self._page_elements.setdefault("unknown", set()).add(label)

			self.log(f"[testing] {label}", "warn")

			# Check if ALL states on this element's page are now clicked
			page_url = self._element_page.get(label, "")
			if page_url and page_url in self._page_elements:
				page_labels = self._page_elements[page_url]
				if page_labels and page_labels.issubset(self._clicked):
					# All states on this page explored -> move them to tested
					for pl in list(page_labels):
						if pl in self.manual_session.untested:
							self.manual_session.untested.remove(pl)
						if pl not in self.manual_session.tested:
							self.manual_session.tested.append(pl)
					self.log(f"[tested] All states on page explored!", "success")

			self.manual_session.edges.append(
				{
					"from": f"state{max(len(self.manual_session.tested)-1,0)}",
					"action": label,
					"to": f"state{len(self.manual_session.tested)}",
				}
			)
			self.refresh_lists()
			self._update_manual_summary()
		self.root.after(0, update)

	def on_page_elements(self, url, labels):
		def update():
			all_known = set(self.manual_session.untested) | set(self.manual_session.tested)
			new_count = 0
			if url not in self._page_elements:
				self._page_elements[url] = set()
			for label in labels:
				if label not in all_known:
					self.manual_session.untested.append(label)
					all_known.add(label)
					self._page_elements[url].add(label)
					self._element_page[label] = url
					new_count += 1
			if new_count > 0:
				self.refresh_lists()
				self._update_manual_summary()
				self.log(f"[page] {url} — {new_count} new states found", "info")
		self.root.after(0, update)

	def _update_manual_summary(self):
		tested = len(self.manual_session.tested)
		untested = len(self.manual_session.untested)
		total = tested + untested
		self.summary_text.delete("1.0", END)
		self.summary_text.insert(
			END,
			f"Manual Testing\n\n"
			f"Tested:   {tested}  (green)\n"
			f"Untested: {untested}  (red)\n"
			f"Total:    {total}\n",
		)

	def mark_tested(self):
		selection = self.untested_list.curselection()
		if not selection:
			return
		idx = selection[0]
		item = self.manual_session.untested.pop(idx)
		self.manual_session.tested.append(item)
		self._clicked.add(item)
		if self.manual_session.tested:
			self.manual_session.edges.append(
				{
					"from": "state0",
					"action": item,
					"to": f"state{len(self.manual_session.tested)}",
				}
			)
		self.log(f"[tested] {item}", "success")
		self.refresh_lists()
		self._update_manual_summary()

	# ── Generate tests ───────────────────────────────────────────────
	def generate_tests(self):
		if self.mode.get() == "manual":
			run_label = time.strftime("%Y%m%d-%H%M%S")
			out_dir = Path(__file__).resolve().parents[1] / "out" / f"gui_manual_{run_label}"
			out_dir.mkdir(parents=True, exist_ok=True)
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
			messagebox.showinfo("StateEye", f"Output saved under {out_dir}")
			return

		# Auto mode: show test cases, then run them
		if not self.run_dir:
			messagebox.showerror("StateEye", "No crawl output found. Run a crawl first.")
			return
		test_file = next(Path(self.run_dir).rglob("generated_tests.py"), None)
		if not test_file:
			messagebox.showerror("StateEye", "No generated_tests.py found in the last crawl output.")
			return

		# Parse TEST_STATES from the generated file
		try:
			content = test_file.read_text(encoding="utf-8")
			match = re.search(r"TEST_STATES\s*=\s*(\[.*?\n\])", content, re.DOTALL)
			if not match:
				messagebox.showerror("StateEye", "Could not parse test data from generated_tests.py.")
				return
			raw = match.group(1).replace(': True', ': true').replace(': False', ': false').replace(': None', ': null')
			test_states = json.loads(raw)
		except Exception as e:
			messagebox.showerror("StateEye", f"Error reading test file: {e}")
			return

		# Count stats
		total = len(test_states)
		skipped = sum(1 for t in test_states if t.get("skip"))
		to_run = total - skipped

		# Phase 1: Display test cases
		self.log("=" * 55, "info")
		self.log("  Generated Regression Test Cases", "info")
		self.log(f"  {total} states | {to_run} to test | {skipped} skipped (clone/nd2)", "info")
		self.log("=" * 55, "info")
		self.log("", "dim")

		for idx, test in enumerate(test_states):
			url = test.get("url", "")
			title = test.get("title", "")
			classification = test.get("classification", "distinct")
			is_skip = test.get("skip", False)
			rep = test.get("representative_of")
			label = title.strip() if title.strip() else url

			if is_skip:
				self.log(f"Test {idx + 1}: {label}  [SKIP duplicate of #{rep}]", "dim")
			else:
				self.log(f"Test {idx + 1}: {label}  [{classification}]", "state")
				self.log(f"  URL:   {url}", "dim")

		self.log("", "dim")
		self.log("=" * 55, "info")
		self.log(f"  Test file: {test_file}", "dim")
		self.status_badge.set("Tests Generated", ACCENT_GREEN)

	def _stream_test_output(self, proc):
		"""Read test subprocess output and push to the log."""
		try:
			for line in proc.stdout:
				line = line.rstrip("\n\r")
				if line:
					self.root.after(0, lambda l=line: self._parse_test_line(l))
		except Exception:
			pass

	def _parse_test_line(self, line):
		"""Color-code test output lines."""
		if "PASS" in line:
			self.log(line, "success")
		elif "FAIL" in line:
			self.log(line, "error")
		elif line.startswith("[test]"):
			self.log(line, "state")
		elif line.startswith("Results:") or line.startswith("="):
			self.log(line, "info")
		else:
			self.log(line, "dim")

	def _wait_test_completion(self, proc):
		exit_code = proc.wait()
		def _update():
			if exit_code == 0:
				self.log("All tests passed!", "success")
				self.status_badge.set("Tests Passed", ACCENT_GREEN)
			else:
				self.log("Some tests failed.", "error")
				self.status_badge.set("Tests Failed", ACCENT_RED)
		self.root.after(0, _update)

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

	# ── State-level classification ───────────────────────────────────
	def classify_states(self, out_dir):
		"""
		Simplified state-level classification after crawl.
		Compares pages pairwise using DOM similarity and fragment overlap.

		Clone:      same DOM hash + same screenshot hash
		Nd2-data:   same template/structure, different data (DOM similarity > 0.8)
		Nd3-struct: different DOM but >50% fragments overlap
		Distinct:   completely different pages
		"""
		import sqlite3
		from difflib import SequenceMatcher
		db_path = next(Path(out_dir).rglob("stateeye.db"), None)
		if not db_path:
			return None

		conn = sqlite3.connect(str(db_path))
		conn.row_factory = sqlite3.Row

		states = conn.execute(
			"SELECT id, url, dom_hash, screenshot_hash, dom_path FROM states ORDER BY id"
		).fetchall()

		# Get fragment dom_hashes per state
		frag_hashes = {}
		for s in states:
			rows = conn.execute(
				"SELECT dom_hash FROM fragments WHERE state_id = ?", (s["id"],)
			).fetchall()
			frag_hashes[s["id"]] = set(r["dom_hash"] for r in rows if r["dom_hash"])

		# Read and normalize DOM content for similarity comparison
		dom_contents = {}
		for s in states:
			dom_file = Path(s["dom_path"]) if s["dom_path"] else None
			if dom_file and dom_file.exists():
				try:
					raw = dom_file.read_text(encoding="utf-8", errors="replace")
					# Strip tags to get structural skeleton (remove text data)
					structural = re.sub(r">([^<]+)<", "><", raw)
					structural = re.sub(r"\s+", " ", structural).strip()
					dom_contents[s["id"]] = structural
				except Exception:
					dom_contents[s["id"]] = ""
			else:
				dom_contents[s["id"]] = ""

		conn.close()

		if len(states) < 2:
			return {"clone": 0, "nd2-data": 0, "nd3-struct": 0, "distinct": len(states)}

		# Classify each state by comparing with all previous states
		classifications = {}  # state_id -> classification
		ND2_THRESHOLD = 0.9  # Very similar structure (same template, different data)
		ND3_THRESHOLD = 0.5  # Moderate structural similarity (shared components)

		for i, state in enumerate(states):
			best_cls = None
			best_sim = 0.0
			for j in range(0, i):
				other = states[j]
				# Exact DOM hash + screenshot hash → Clone
				if state["dom_hash"] and state["dom_hash"] == other["dom_hash"]:
					if state["screenshot_hash"] and state["screenshot_hash"] == other["screenshot_hash"]:
						best_cls = "clone"
						break
					else:
						best_cls = "nd2-data"
						continue

				# Compare DOM structure (tags only, text stripped)
				struct_a = dom_contents.get(state["id"], "")
				struct_b = dom_contents.get(other["id"], "")
				if struct_a and struct_b:
					sim = SequenceMatcher(None, struct_a, struct_b).ratio()
					if sim >= ND2_THRESHOLD and best_cls not in ("clone",):
						best_cls = "nd2-data"
					elif sim >= ND3_THRESHOLD and best_cls not in ("clone", "nd2-data"):
						best_cls = "nd3-struct"

			classifications[state["id"]] = best_cls or "distinct"

		counts = {"clone": 0, "nd2-data": 0, "nd3-struct": 0, "distinct": 0}
		for cls in classifications.values():
			counts[cls] += 1

		return counts

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

		# Run state-level classification
		state_cls = self.classify_states(out_dir)
		if state_cls:
			cls_text = (
				f"Clone: {state_cls['clone']} | "
				f"Nd2: {state_cls['nd2-data']} | "
				f"Nd3: {state_cls['nd3-struct']} | "
				f"Distinct: {state_cls['distinct']}"
			)
			self.stat_status.set_value(cls_text)
			self.log(f"[classify] States — {cls_text}", "classify")

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
		lines.append(f"States: {total_pages}")

		# Show fragment count from live data, fallback to page count
		if self.fragments_found > 0:
			lines.append(f"Fragments: {self.fragments_found}")
		else:
			self.stat_pages.set_value(total_pages)

		# State-level classification (already computed in on_auto_complete)
		state_cls = self.classify_states(out_dir)
		if state_cls:
			lines.append(f"Clone: {state_cls['clone']}")
			lines.append(f"Nd2-data: {state_cls['nd2-data']}")
			lines.append(f"Nd3-struct: {state_cls['nd3-struct']}")
			lines.append(f"Distinct: {state_cls['distinct']}")

		# Fragment-level classification from live crawl data
		if self._has_live_classify:
			lines.append(f"Frag Clones: {self._live_clones}")
			lines.append(f"Frag Near-dup: {self._live_near_dup}")
			lines.append(f"Frag Unique: {self._live_unique}")

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
