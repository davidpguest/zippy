#!/usr/bin/python3

import re, requests, time, urllib, tkinter as tk, tkinter.scrolledtext as tkst
from html.parser import HTMLParser

#set up browser window
win = tk.Tk()
win.title("Zippy")
img = tk.Image("photo", file="zippy.gif")
win.tk.call('wm','iconphoto',win._w,img)
win.config(background='#ffffff')
estring = tk.StringVar()
e = tk.Entry(master = win, textvariable=estring)
e.config(borderwidth=1, background='#ffffff', highlightbackground='#ffffff', selectbackground='#dddddd', highlightthickness=0, relief='flat')
e.pack(side='top', padx=40, pady=5, fill=tk.X, expand=False)
bframe = tk.Frame(master = win, width = 300, height = 200, bg = '#ffffff', borderwidth=0)
bframe.pack(fill='both', expand='yes')
w = tkst.ScrolledText(master = bframe, wrap   = tk.WORD, borderwidth = 0, padx = 40, pady = 0)
w.vbar.configure(borderwidth=0, elementborderwidth=0, activerelief='flat', relief='flat', background='#bbbbbb', activebackground='#bbbbbb', troughcolor='#ffffff', width=5)
w.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)

#global variables
homepage = "https://uk.yahoo.com"
useragent = "Mozilla/5.0 (X11; CrOS x86_64 12607.81.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.119 Safari/537.36"
page = ""
history = []
config = {'stop':0, 'links':0, 'linkstart':"", 'link_to':"", 'baseurl':"", 'history':0, 'current':0, 'histindex':0}

#html parser

class zippy_parse(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global page 
		if tag == "a":
			for attr in attrs:
				if attr[0] == "href":
					blink = basify(attr[1])
					page += "[" + blink + "]"
		elif tag == "p":
			page += "\n"
	def handle_startendtag(self, tag, attrs):
		global page
		if tag == "br":
			page += "\n"
	def handle_endtag(self, tag):
		global page
		if tag == "p":
			page += "\n"
		elif tag == "li":
			page += " "
		elif tag == "a":
			page += "[closelink]"
		else:
			page += " "
	def handle_data(self, data):
		global page 
		page += data

#application functions
def set_config(setting, value):
	global config
	config[setting] = value

def get_config(setting):
	global config
	return config[setting]

def set_history(url):
	global history
	currindex = get_config('histindex')
	if currindex < len(history)-1:
		del history[currindex+1:]
	history.append(url)
	currindex = len(history)-1
	if currindex > 0:
		set_config('histindex', currindex)

def go_back():
	global history
	stop_load()
	time.sleep(0.2)
	currindex = get_config('histindex')
	if currindex > 0:
		lasturl = history[currindex-1]
		set_config('histindex', currindex-1)
		get_page(lasturl, False)

def wipe():
	w.config(state='normal')
	w.delete(1.0,'end')
	w.config(state='disabled')
	w.update()
	win.update_idletasks()
	global page
	page = ""

def stop_load():
	global page
	set_config('stop', 1)
	page = ""

def look_up(event):
	global e
	inputstring = e.get()
	if inputstring[0:4] == "http":
		get_page(inputstring)
	else:
		query = urllib.parse.quote(inputstring)
		query = "https://google.com/search?q=" + query
		get_page(query)

def inject_text(page_text):	
	i = 0	
	while i < len(page_text):
		o = ord(page_text[i]);
		if o > 65535:
			page_text[i]=""
		i += 1
	w.config(state='normal')
	w.insert('end', page_text)
	w.config(state='disabled')
	w.update()
	win.update_idletasks()

def open_link(link_addr):
	pos = w.index(tk.INSERT)
	linkstart = get_config('linkstart')
	if linkstart != "":
		close_link()
	set_config('linkstart', pos)
	set_config('link_to', link_addr)

def close_link():
	linkstart = get_config('linkstart')
	link_to = get_config('link_to')
	linkend = w.index(tk.INSERT)
	link_addr = link_to
	if linkstart != "" and link_to != "":
		links = get_config('links') + 1
		set_config('links', links)
		linkname = "link" + str(links)
		w.tag_add(linkname, linkstart, linkend)
		w.tag_config(linkname, foreground="blue", underline=1)
		w.tag_bind(linkname, "<Enter>", lambda *a, **k: w.config(cursor="hand2"))
		w.tag_bind(linkname, "<Leave>", lambda *a, **k: w.config(cursor="arrow"))
		w.tag_bind(linkname, "<Button-1>", lambda e: get_page(link_addr))
	set_config('linkstart', '')
	set_config('linkto', '')
	w.update()

def open_action():
	pos = w.index(tk.INSERT)
	return pos

def close_action(pos, linkname):
	linkstart = pos
	linkend = w.index(tk.INSERT)
	w.tag_add(linkname, linkstart, linkend)
	w.tag_config(linkname, foreground="blue", underline=1)
	w.tag_bind(linkname, "<Enter>", lambda *a, **k: w.config(cursor="hand2"))
	w.tag_bind(linkname, "<Leave>", lambda *a, **k: w.config(cursor="arrow"))
	if linkname == "stop":
		w.tag_bind(linkname, "<Button-1>", lambda e: stop_load())
	elif linkname == "back":
		w.tag_bind(linkname, "<Button-1>", lambda e: go_back())
	w.update()

def render_header(url):
	inject_text("\n")
	open_link(homepage)
	inject_text("Home")
	close_link()
	inject_text(" ")
	lpos = open_action()
	inject_text("Stop")
	close_action(lpos, "stop")
	inject_text(" ")
	lpos = open_action()
	inject_text("Back")
	histindex = get_config('histindex')
	if histindex > 0:
		close_action(lpos, "back")
	inject_text("\n\n")
	w.update()

def basify(linkattr):
	baseurl = get_config('baseurl')
	if linkattr[0:4] != "http":
		if linkattr[0:2] == "//":
			linkattr = "http:" + linkattr
		else:
			linkattr = baseurl + "/" + linkattr.strip("/ ")
	return linkattr
	
def process_page(data):
	strfind = ["<!--", "<script", "<style", "<title"]
	strswap = ["-->", "</script>", "</style>", "</title>"]
	for i in range(len(strfind)):
		bits = data.split(strfind[i])
		data = bits[0]
		for bit in bits:
			nbits = bit.split(strswap[i])
			if len(nbits) > 1:
				data += nbits[1]
	data = data.replace("\n", "")
	data = data.replace("\r", "")
	data = data.replace("\t", "")
	data = data.replace("[", "(")
	data = data.replace("]", ")")
	data = re.sub(r'<br*?>', '\n', data)
	#data = data.replace('"', "'")
	#bits = re.findall("'(.*?)'", data)
	#for b in bits:
	#	n = b.replace(">", "")
	#	data = data.replace(b, n)
	parser = zippy_parse()
	parser.feed(data)
	global page
	data = page
	data = re.sub(' +', ' ', data)
	data = data.replace('\n ', '\n')
	data = data.replace("[closelink] ", "[closelink]--")
	data = data.replace('] ', ']')
	data = data.replace("[closelink]--", "[closelink] ")
	data = data.replace(" [closelink]", "[closelink]")
	data = data.strip()
	render_page(data)

def render_page(data):
	sections = data.split("[closelink]")
	global config
	for section in sections:
		if get_config('stop') == 1:
			break
		else:
			if section.find("[") > -1:
				linkparts = section.split("[")
				inject_text(linkparts[0])
				linkbounds = linkparts[1].split("]")
				link_addr = linkbounds[0]
				if link_addr == "":
					inject_text(" ")
				else:
					open_link(link_addr)
					inject_text(linkbounds[1])
					close_link()
			else:
				inject_text(section)
	inject_text("\n\n")
	stop_load()

def get_page(url, updatehist=True):
	global config, estring, useragent
	wipe()
	estring.set(url)
	set_config('stop', 0)
	if updatehist:
		set_history(url)
	render_header(url)
	baseurlb = url.replace("://","-:-")
	baseurlbits = baseurlb.split("/")
	baseurl = baseurlbits[0].replace("-:-", "://")
	set_config('baseurl', baseurl)
	req = urllib.request.Request(url)
	req.add_header('User-Agent', useragent)
	with urllib.request.urlopen(req) as r:
		page = r.read().decode('utf-8')
		process_page(page)

win.bind('<Return>', look_up)
get_page(homepage)
win.mainloop()
