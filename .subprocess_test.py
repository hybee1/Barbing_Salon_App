import subprocess
import sys

print("Python:", sys.executable)
result = subprocess.run(
    [sys.executable, "-c", "import sys; print('Child:', sys.executable)"],
    check=False,
)
print("Exit code:", result.returncode)
