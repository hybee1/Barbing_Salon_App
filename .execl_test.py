import os
import sys

print("Before:", sys.executable, flush=True)
os.execl(sys.executable, sys.executable, "-c", "print(123)")
