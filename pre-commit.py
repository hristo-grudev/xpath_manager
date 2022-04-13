import subprocess

print("Pre-Commit Hook")
# update requirements
subprocess.run('pipreqs --force', shell=True)
subprocess.run('sort-requirements requirements.txt', shell=True)
