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
	END,
	Listbox,
	Text,
	Scrollbar,
	Frame,
	Label,
	Entry,
	Button,
	Radiobutton,
	filedialog,
	messagebox,
)
import subprocess
import http.server
import socketserver
import functools
import re


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


class StateEyeGUI:
	def __init__(self, root):
		self.root = root
		self.root.title("StateEye Desktop")
		self.mode = StringVar(value="auto")
		self.target = StringVar()
		self.runtime_mins = StringVar(value="1")
		self.max_depth = StringVar(value="5")
		self.max_states = StringVar(value="50")
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
		self.build_ui()

	def build_ui(self):
		row = Frame(self.root)
		row.pack(fill="x", padx=8, pady=6)
		Label(row, text="URL or local HTML path:").pack(side="left")
		Entry(row, textvariable=self.target, width=60).pack(side="left", padx=6)
		Button(row, text="Browse", command=self.browse_file).pack(side="left")

		mode_row = Frame(self.root)
		mode_row.pack(fill="x", padx=8, pady=6)
		Label(mode_row, text="Mode:").pack(side="left")
		Radiobutton(mode_row, text="Automated Testing", variable=self.mode, value="auto").pack(side="left")
		Radiobutton(mode_row, text="Manual Assisted Testing", variable=self.mode, value="manual").pack(side="left")

		opt_row = Frame(self.root)
		opt_row.pack(fill="x", padx=8, pady=6)
		Label(opt_row, text="Runtime (mins)").pack(side="left")
		Entry(opt_row, textvariable=self.runtime_mins, width=6).pack(side="left", padx=4)
		Label(opt_row, text="Max depth").pack(side="left", padx=8)
		Entry(opt_row, textvariable=self.max_depth, width=6).pack(side="left", padx=4)
		Label(opt_row, text="Max states").pack(side="left", padx=8)
		Entry(opt_row, textvariable=self.max_states, width=6).pack(side="left", padx=4)

		action_row = Frame(self.root)
		action_row.pack(fill="x", padx=8, pady=6)
		Button(action_row, text="Start", command=self.start).pack(side="left")
		Button(action_row, text="Stop", command=self.stop).pack(side="left", padx=6)
		Button(action_row, text="Generate Tests", command=self.generate_tests).pack(side="left")

		log_row = Frame(self.root)
		log_row.pack(fill="both", expand=True, padx=8, pady=6)
		Label(log_row, text="Log").pack(anchor="w")
		self.log_text = Text(log_row, height=10)
		scroll = Scrollbar(log_row, command=self.log_text.yview)
		self.log_text.configure(yscrollcommand=scroll.set)
		self.log_text.pack(side="left", fill="both", expand=True)
		scroll.pack(side="left", fill="y")

		summary_row = Frame(self.root)
		summary_row.pack(fill="both", expand=True, padx=8, pady=6)
		Label(summary_row, text="Summary").pack(anchor="w")
		self.summary_text = Text(summary_row, height=8)
		self.summary_text.pack(fill="both", expand=True)

		list_row = Frame(self.root)
		list_row.pack(fill="both", expand=True, padx=8, pady=6)
		left = Frame(list_row)
		right = Frame(list_row)
		left.pack(side="left", fill="both", expand=True, padx=4)
		right.pack(side="left", fill="both", expand=True, padx=4)

		Label(left, text="Untested elements").pack(anchor="w")
		self.untested_list = Listbox(left, height=8)
		self.untested_list.pack(fill="both", expand=True)
		self.untested_list.bind("<Double-Button-1>", lambda _e: self.mark_tested())
		Button(left, text="Mark Tested", command=self.mark_tested).pack(pady=4)

		Label(right, text="Tested elements").pack(anchor="w")
		self.tested_list = Listbox(right, height=8)
		self.tested_list.pack(fill="both", expand=True)

	def log(self, message):
		self.log_text.insert(END, message + "\n")
		self.log_text.see(END)

	def browse_file(self):
		path = filedialog.askopenfilename(
			title="Select HTML file",
			filetypes=[("HTML files", "*.html;*.htm"), ("All files", "*.*")],
		)
		if path:
			self.target.set(path)

	def start(self):
		target = self.target.get().strip()
		if not target:
			messagebox.showerror("StateEye", "Please enter a URL or HTML file path.")
			return
		self.log(f"Selected mode: {self.mode.get()}")
		if self.mode.get() == "auto":
			self.start_automated(target)
		else:
			self.start_manual(target)

	def stop(self):
		if self.auto_proc and self.auto_proc.poll() is None:
			self.auto_proc.terminate()
			self.log("Stopped automated crawl.")
		if self.server:
			self.server.stop()
			self.server = None

	def start_automated(self, target):
		self.log("Automated mode: starting crawl and test generation.")
		run_label = time.strftime("%Y%m%d-%H%M%S")
		out_dir = Path(__file__).resolve().parents[1] / "out" / f"gui_{run_label}"
		out_dir.mkdir(parents=True, exist_ok=True)
		self.run_dir = out_dir
		mode = self.resolve_auto_mode()
		self.log(f"Automated crawl mode: {mode}")

		args = [
			"python",
			str(Path(__file__).resolve().parent / "run_demo_crawl.py"),
			"--mode",
			mode,
			"--target",
			target,
			"--runtime-mins",
			self.runtime_mins.get(),
			"--max-depth",
			self.max_depth.get(),
			"--max-states",
			self.max_states.get(),
			"--output-dir",
			str(out_dir),
		]
		args.extend(["--host", "localhost"])
		self.log("Running: " + " ".join(args))
		self.auto_proc = subprocess.Popen(args)
		timeout_secs = self.get_runtime_secs() + self.hard_timeout_grace_secs
		threading.Thread(
			target=self.enforce_hard_timeout, args=(self.auto_proc, timeout_secs), daemon=True
		).start()
		threading.Thread(
			target=self.wait_for_auto_completion, args=(self.auto_proc, out_dir), daemon=True
		).start()

	def start_manual(self, target):
		self.log("Manual mode: parsing page and launching browser.")
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
		self.summary_text.insert(
			END,
			"Manual mode: click in the browser or double-click in the list.\n",
		)
		webbrowser.open(url)
		self.log(f"Opened {url}")

	def extract_elements(self, target, url):
		try:
			if os.path.exists(target):
				content = Path(target).read_text(encoding="utf-8", errors="ignore")
			else:
				self.log("Manual mode uses local HTML for element guidance.")
				content = ""
		except Exception as exc:
			self.log(f"Failed to parse HTML: {exc}")
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
			self.log("No actionable elements detected.")
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
			self.log(f"Manual test plan saved to {out_file}")
			self.summary_text.delete("1.0", END)
			self.summary_text.insert(
				END,
				f"Manual summary:\nTested: {len(self.manual_session.tested)}\n"
				f"Untested: {len(self.manual_session.untested)}\n"
				f"Plan: {out_file}",
			)
		else:
			self.log("Automated mode: tests are generated in the crawl output directory.")
		messagebox.showinfo("StateEye", f"Output saved under {out_dir}")

	def wait_for_auto_completion(self, proc, out_dir):
		exit_code = proc.wait()
		self.root.after(0, lambda: self.on_auto_complete(exit_code, out_dir))

	def enforce_hard_timeout(self, proc, timeout_secs):
		start = time.time()
		while proc.poll() is None:
			if time.time() - start > timeout_secs:
				proc.terminate()
				self.root.after(
					0,
					lambda: self.log(
						f"Hard timeout reached ({timeout_secs}s). Process terminated."
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
		return "dom"

	def on_auto_complete(self, exit_code, out_dir):
		if exit_code == 0:
			self.log("Automated crawl completed.")
		else:
			self.log(f"Automated crawl exited with code {exit_code}.")
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
		test_path = next(out_dir.rglob("GeneratedTests.java"), None)
		lines = []
		lines.append(f"Output folder: {out_dir}")
		if not out_dir.exists():
			lines.append("Output folder: not found")
		if result_path is None:
			lines.append("result.json: not found")
			candidates = list(out_dir.rglob("crawl*/result.json"))
			if candidates:
				candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
				result_path = candidates[0]
				lines.append(f"Using fallback result.json: {result_path}")
			else:
				global_candidates = []
				if out_dir.parent.exists():
					global_candidates = list(out_dir.parent.rglob("result.json"))
				if global_candidates:
					global_candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
					result_path = global_candidates[0]
					lines.append(f"Using latest result.json: {result_path}")
				else:
					lines.append("No crawl result was produced. Check console logs for errors.")
					return "\n".join(lines)
		try:
			data = json.loads(result_path.read_text(encoding="utf-8", errors="ignore"))
		except Exception as exc:
			lines.append(f"result.json parse error: {exc}")
			return "\n".join(lines)

		states = data.get("states", {})
		stats = data.get("statistics", {}).get("stateStats", {})
		total_states = stats.get("totalNumberOfStates", len(states))
		edges = data.get("edges", [])
		exit_status = data.get("exitStatus", "unknown")
		self.last_exit_status = exit_status
		lines.append(f"Mode: {self.resolve_auto_mode()}")
		lines.append(f"Exit status: {exit_status}")
		lines.append(f"Unique states: {total_states}")
		lines.append(f"Edges: {len(edges)}")
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
				lines.append(f"Fraggen analysis failed: {exc}")
		if fraggen_report.exists():
			try:
				report = json.loads(
					fraggen_report.read_text(encoding="utf-8", errors="ignore")
				)
				summary = report.get("summary", {})
				lines.append(f"Clones: {summary.get('clone', 0)}")
				lines.append(f"Near-duplicates: {summary.get('near_duplicates', 0)}")
				lines.append(f"Nd2-data: {summary.get('nd2', 0)}")
				lines.append(f"Nd3-struct: {summary.get('nd3', 0)}")
				lines.append(f"Distinct: {summary.get('distinct', 0)}")
			except Exception as exc:
				lines.append(f"Fraggen summary error: {exc}")
		else:
			near_dup_states = [
				name for name, info in states.items() if info.get("hasNearDuplicate") is True
			]
			lines.append(f"Near-duplicates: {len(near_dup_states)}")
			if near_dup_states:
				lines.append("Near-duplicate state IDs: " + ", ".join(near_dup_states))

		if test_path is None:
			lines.append("Generated tests: not found")
			return "\n".join(lines)

		methods = []
		for line in test_path.read_text(encoding="utf-8", errors="ignore").splitlines():
			match = re.search(r"public void (\w+)\(", line)
			if match and match.group(1).startswith("method_"):
				methods.append(match.group(1))
		if methods:
			lines.append("Test cases:")
			lines.extend([f"- {name}" for name in methods])
		else:
			lines.append("Test cases: none detected")
		return "\n".join(lines)


def main():
	root = Tk()
	app = StateEyeGUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()
