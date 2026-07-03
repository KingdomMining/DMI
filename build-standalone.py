import base64, re, os, sys

os.chdir("/home/user/DMI")
html = open("index.html").read()

def to_data_uri(path):
    ext = path.rsplit(".",1)[-1].lower()
    mime = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp","svg":"image/svg+xml"}[ext]
    with open(path,"rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

missing = []
def repl_src(m):
    path = m.group(2)
    if not os.path.exists(path):
        missing.append(path)
        return m.group(0)
    return m.group(1) + to_data_uri(path) + m.group(3)

# src="images/..." and href="images/..." (favicon)
html2 = re.sub(r'(src=")(images/[^"]+)(")', repl_src, html)
html2 = re.sub(r'(href=")(images/[^"]+)(")', repl_src, html2)

# JS-referenced image paths (industry banner swap uses 'images/backgrounds/...' strings in the meta object)
js_paths = set(re.findall(r"'(images/backgrounds/[^']+)'", html2))
for p in js_paths:
    if os.path.exists(p):
        html2 = html2.replace(f"'{p}'", f"'{to_data_uri(p)}'")
    else:
        missing.append(p)

# inline three.js
three = open("js/three.min.js").read()
html2 = html2.replace('<script src="js/three.min.js"></script>',
                      '<script>\n' + three + '\n</script>')

out = "DMI-Website.html"
open(out,"w").write(html2)
print("wrote", out, f"{os.path.getsize(out)//1024} KB")
print("missing (expected placeholders only):", missing)
leftover = re.findall(r'(?:src|href)="(images/[^"]+)"', html2)
print("leftover relative refs:", leftover)
print("script src refs left:", re.findall(r'<script src="[^"]+"', html2))
