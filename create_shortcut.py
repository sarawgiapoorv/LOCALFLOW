import os
import subprocess

vbs_path = r"c:\Users\jai shree shyam\OneDrive\Desktop\LocalFlow\Launch_LocalFlow.vbs"
project_dir = r"c:\Users\jai shree shyam\OneDrive\Desktop\LocalFlow"
user_profile = os.environ.get("USERPROFILE", r"C:\Users\jai shree shyam")

desktops = [
    os.path.join(user_profile, "OneDrive", "Desktop"),
    os.path.join(user_profile, "Desktop")
]

for d in desktops:
    if os.path.exists(d):
        lnk = os.path.join(d, "LocalFlow.lnk")
        ps = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{lnk}')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '"{vbs_path}"'
$s.WorkingDirectory = '{project_dir}'
$s.Description = 'LocalFlow - Speech to Mind Voice Dictation'
$s.Save()
"""
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        print(f"Shortcut created at: {lnk} (exists: {os.path.exists(lnk)})")

