# Dependencies:
# - yad (yet another dialog command line tool)

import subprocess

def warning(text) :
  subprocess.run(["yad", "--image=dialog-warning", "--title=Warning",
    "--button=Close!window-close", "--buttons-layout=center", "--text", text],
    capture_output = False)

def error(text) :
  subprocess.run(["yad", "--image=dialog-error", "--title=Error",
    "--button=Close!window-close", "--buttons-layout=center", "--text", text],
    capture_output = False)

# this one doesn't wait for the window to close, returns the popen object
# that can be used to track it instead
def longtext_bg(text, title) :
  opts = []
  if title :
    opts += ["--title", title]
  proc = popen(["yad", "--text-info"] + opts, stdin = PIPE, stdout = DEVNULL,
    stderr = DEVNULL, text = True)
  print(text, file = proc.stdin)
  return proc

def dirselect(text, title = "Select directory") :
  opts = []
  if text :
    opts += ["--text", text]
  subprocess.run(["yad", "--file", "--directory", "--title", title] + opts,
    capture_output = True, text = True)
  if result.returncode != 0 or result.stdout == "" :
    return None
  return result.stdout.splitlines()[0]  # strip trailing newline

def listselect(list, header, text, title = "Please select") :
  opts = []
  if text :
    opts += ["--text", text]
  result = subprocess.run(["yad", "--list", "--title", title,
    "--height", str(min(len(list) * 25, 600)), "--column", header,
    "--separator="] + opts + list, capture_output = True, text = True)
  if result.returncode != 0 or result.stdout == "" :
    return None
  return result.stdout.splitlines()[0]  # strip trailing newline

# 'list' must be a flat list like
# [r1c1, r1c2, ... r1cn, r2c1, r2c2, ... r2cn, ... rmc1, rmc2, ... rmcn]
# which is the way `yad` needs it
# 'headers' is the list of column headers
# 'key' is the number of the column to return
def listselect_cols(list, headers, text, title = "Please select", key = 1,
  allow_filter = True) :
  opts = []
  if text :
    opts += ["--text", text]
  if allow_filter :
    # let's keep the standard buttons as they are...
    opts += ["--button=Filter:3", "--button=gtk-cancel:1", "--button=gtk-ok:0"]
  for h in headers :
    opts += ["--column", h]
  result = subprocess.run(["yad", "--list", "--title", title, "--separator="] +
    opts + list, capture_output = True, text = True)
  if result.returncode == 0 and result.stdout != "" :
    return result.stdout.splitlines()[0]  # strip trailing newline
  if result.returncode == 3 :  # 'Filter' button pressed
    return 3
  return 1    # 'Cancel', 'Escape', or window closed

def filters_dialog() :
  result = subprocess.run(
    ["yad", "--form", "--title", "Filtering", "--text", "Select filters:",
      "--separator=\\n",
      "--field", "Type:CB", "clear!static!moving",
      "--field", "Status:CB", "clear!old!pre!stored",
      "--field", "Tribe:CB",
        "clear!world!amazons!atlanteans!barbarians!empire!frisians"],
    capture_output = True, text = True)
  if result.returncode != 0 :
    return None
  return dict(zip(["type", "status", "tribe"], result.stdout.splitlines()))

