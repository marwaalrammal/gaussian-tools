#Marwa Al Rammal 10 May 2026
import os

template_file = "197s.gjf"

with open(template_file, "r") as f:
    template = f.read()

for n in range(197, 222, 2):
    filename = f"{n}s.gjf"
    content = template.replace("197s.chk", f"{n}s.chk")
    with open(filename, "w") as f:
        f.write(content)
    print(f"Created {filename}")
