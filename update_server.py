import os
import stat
import subprocess
import shutil
from pathlib import Path
SERVER_DIR = "/home/fishgills/.steam/steam/steamapps/common/Arma 3 Server/"
WORKSHOP_DIR = "/home/fishgills/.steam/steam/steamapps/workshop/content/107410/"
MOD_DIR = os.path.join(os.getcwd(), "mods")

SERVER_ID = 233780
ARMA_ID = 107410
STARTUP = "./arma3server_x64 -ip=0.0.0.0 -enableHT -profiles=./serverprofile -bepath=./ -cfg=basic.cfg -config=server.cfg -mod=\"%s\""
#mod_ids = [2794721649,2791403093,2257686620,450814997,2886141254,861133494,1804716719,1808723766,925018569]
mod_ids = []

def listModDir():
    mod_dir = os.listdir(WORKSHOP_DIR)
    mod_dir = [int(f) for f in mod_dir if os.path.isdir(WORKSHOP_DIR+'/'+f)]
    return mod_dir

def runSteamCmds(cmds):
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, universal_newlines=True)

    for line in process.stdout:
        print(line, end='')

    # Wait for the process to finish
    process.wait()

    # Get the exit status of the process
    exit_code = process.returncode

def ModsLowercase(directory):
    print(f"Making lower case in {directory}")

    # renames all subforders of dir, not including dir itself
    def rename_all( root, items):
        for name in items:
            try:
                os.rename( os.path.join(root, name), 
                                    os.path.join(root, name.lower()))
            except OSError:
                pass # can't rename it, so what

    # starts from the bottom so paths further up remain valid after renaming
    for root, dirs, files in os.walk( directory, topdown=False ):
        rename_all( root, dirs )
        rename_all( root, files)

def clearKeys(keys_dir: str):
    for filename in os.listdir(keys_dir):
        if filename.endswith(".bikey") and filename != "a3.bikey":
            file_path = os.path.join(keys_dir, filename)
            os.remove(file_path)

def clearSymLinks(server_dir: str):
    for path in Path(server_dir).rglob("@*"):
        print(str(path))
        os.unlink(str(path))

def copyKeys(mod_dir: str):
    for path in Path(mod_dir).rglob("*.bikey"):
        # print(mod_dir+path.)
        # print(path)
        shutil.copy(path, SERVER_DIR+"keys")

to_delete = list(set(listModDir()) - set(mod_ids))

for mod_to_delete in to_delete:
    print(f"Deleting {mod_to_delete}.")
    shutil.rmtree(WORKSHOP_DIR+"/"+str(mod_to_delete))

clearKeys(SERVER_DIR+"keys")
clearSymLinks(SERVER_DIR)

base_cmds = ["login junk@fishgills.net", f"app_update {SERVER_ID} validate"]
steam_cmds = ["steamcmd"]

for mod in mod_ids:
    base_cmds.append(f"workshop_download_item {ARMA_ID} {mod} validate")

steam_cmds.extend(["+" + cmd for cmd in base_cmds])
steam_cmds.append("+quit")
print(" ".join(steam_cmds))

runSteamCmds(steam_cmds)

installed_mods = listModDir()
startup_mods = []

for mod in installed_mods:
    mod_dir = WORKSHOP_DIR+str(mod)
    ModsLowercase(mod_dir)
    copyKeys(mod_dir)
    os.symlink(mod_dir, SERVER_DIR+"@"+str(mod))
    startup_mods.append("@"+str(mod))

print("Mods installed: ", installed_mods)

startup_command = STARTUP % (";".join(startup_mods))

with open(SERVER_DIR+"/start.sh", 'w') as file:
    file.write("#!/bin/bash\n")
    file.write(startup_command+"\n")

st = os.stat(SERVER_DIR+"/start.sh")
os.chmod(SERVER_DIR+"/start.sh", st.st_mode | stat.S_IEXEC)
shutil.copy("./basic.cfg", SERVER_DIR+"/basic.cfg")
shutil.copy("./server.cfg", SERVER_DIR+"/server.cfg")
shutil.copy("./Player.Arma3Profile", SERVER_DIR+"serverprofile/home/Player/Player.Arma3Profile")
