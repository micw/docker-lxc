import subprocess
import os

def run(cmd):
    try:
        subprocess.check_call(['/bin/bash','-c',cmd])
    except subprocess.CalledProcessError as e:
        print(e)
        quit(1)

def run_chroot(dir,cmd):
    try:
        subprocess.check_call(['arch-chroot',dir,'/bin/sh','-c',cmd])
    except subprocess.CalledProcessError as e:
        print(e)
        quit(1)

def writefile(dir,file,content,writemode="w"):
    if type(content) is list:
        content="\n".join(content)+"\n"
    with open(os.path.join(dir,file.lstrip('/')), writemode) as f:
        f.write(content)

def mkdirs(path):
    os.makedirs(path,exist_ok=True)
