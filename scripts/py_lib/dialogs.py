# Dependencies:
# - yad (yet another dialog command line tool)

import subprocess

def listselect(list, header, text, title = "Please select") :
  opts = []
  if text :
    opts += ["--text", text]
  result = subprocess.run(["yad", "--list", "--title", title,
    "--height", str(min(len(list) * 20, 600)), "--column", header,
    "--separator="] + opts + list, capture_output = True, text = True)
  if result.returncode != 0 or result.stdout == "" :
    return None
  return result.stdout.splitlines()[0]

def warning(text) :
  subprocess.run(["yad", "--image=dialog-warning", "--title=Warning",
    "--button=Close!window-close", "--buttons-layout=center", "--text", text],
    capture_output = False)

def error(text) :
  subprocess.run(["yad", "--image=dialog-error", "--title=Error",
    "--button=Close!window-close", "--buttons-layout=center", "--text", text],
    capture_output = False)

