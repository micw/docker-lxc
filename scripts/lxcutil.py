import subprocess
import os

def run(cmd):
    try:
        subprocess.check_call(['/bin/bash','-c',cmd])
    except subprocess.CalledProcessError as e:
        print(e)
        quit(1)

def writefile(dir,file,content):
    if type(content) is list:
        content="\n".join(content)+"\n"
    with open(os.path.join(dir,file.lstrip('/')), "w") as f:
        f.write(content)
