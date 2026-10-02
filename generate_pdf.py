import os
import subprocess

workspace_root = r"d:\Download\mv-baldal"
html_path = os.path.join(workspace_root, "PROJECT_DOCUMENTATION.html")
pdf_path = os.path.join(workspace_root, "ShopManagement_Project_Documentation.pdf")

print(f"Printing {html_path} to {pdf_path} using headless browser...")

chrome_cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=6000",
    f"--print-to-pdf={pdf_path}",
    html_path
]

res = subprocess.run(chrome_cmd, capture_output=True, text=True)
print("Chrome Return Code:", res.returncode)

if not os.path.exists(pdf_path):
    print("Trying Edge...")
    edge_cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--virtual-time-budget=6000",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    res_edge = subprocess.run(edge_cmd, capture_output=True, text=True)
    print("Edge Return Code:", res_edge.returncode)

if os.path.exists(pdf_path):
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"SUCCESS: PDF generated at: {pdf_path} (Size: {size_mb:.2f} MB)")
else:
    print("PDF generation failed.")
