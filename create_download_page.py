import os
import base64
import json
from datetime import datetime

zip_path = r"d:\Download\mv-baldal\mv-baldal.zip"
html_out_path = r"d:\Download\mv-baldal\index.html"
download_out_path = r"d:\Download\mv-baldal\download.html"

with open(zip_path, "rb") as f:
    zip_bytes = f.read()

zip_b64 = base64.b64encode(zip_bytes).decode("utf-8")
zip_size_mb = len(zip_bytes) / (1024 * 1024)
zip_size_kb = len(zip_bytes) / 1024
current_date = datetime.now().strftime("%d %B %Y, %I:%M %p")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download mv-baldal | Shop Management System</title>
    <!-- Google Fonts & FontAwesome -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <style>
        :root {{
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --primary-light: #eff6ff;
            --success: #10b981;
            --dark: #0f172a;
            --slate: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
            --bg: #f8fafc;
            --card-bg: #ffffff;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(180deg, #f1f5f9 0%, #f8fafc 100%);
            color: var(--dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
        }}

        /* Navbar */
        .navbar {{
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            padding: 16px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 700;
            font-size: 1.15rem;
            color: var(--dark);
            text-decoration: none;
        }}

        .brand-icon {{
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
        }}

        .nav-tag {{
            font-size: 0.8rem;
            background: #dbeafe;
            color: #1e40af;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
        }}

        /* Main Container */
        .container {{
            max-width: 960px;
            margin: 40px auto;
            padding: 0 20px;
            flex: 1;
        }}

        /* Hero Card */
        .hero-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px 36px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.05);
            text-align: center;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }}

        .hero-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, #2563eb, #3b82f6, #60a5fa);
        }}

        .badge-row {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }}

        .tech-badge {{
            background: #f1f5f9;
            color: #334155;
            font-size: 0.8rem;
            padding: 5px 12px;
            border-radius: 8px;
            font-weight: 600;
            border: 1px solid #e2e8f0;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .hero-title {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}

        .hero-subtitle {{
            font-size: 1.05rem;
            color: var(--muted);
            max-width: 640px;
            margin: 0 auto 30px auto;
        }}

        /* Download Section */
        .download-box {{
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 30px;
            margin: 25px auto;
            max-width: 650px;
        }}

        .download-btn-group {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
            justify-content: center;
        }}

        .btn-download-primary {{
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 16px 36px;
            border-radius: 12px;
            font-size: 1.15rem;
            font-weight: 700;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.45);
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
            width: 100%;
            max-width: 440px;
            justify-content: center;
        }}

        .btn-download-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 24px -4px rgba(37, 99, 235, 0.55);
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            color: white;
        }}

        .file-meta {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            margin-top: 14px;
            font-size: 0.85rem;
            color: var(--muted);
            flex-wrap: wrap;
        }}

        .file-meta-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        /* Secondary actions */
        .btn-secondary-link {{
            background: white;
            color: #334155;
            border: 1px solid var(--border);
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s ease;
            cursor: pointer;
        }}

        .btn-secondary-link:hover {{
            background: #f1f5f9;
            color: var(--dark);
            border-color: #cbd5e1;
        }}

        /* Setup Guide Grid */
        .setup-section {{
            margin-top: 40px;
        }}

        .section-header {{
            margin-bottom: 20px;
        }}

        .section-title {{
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .steps-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}

        .step-card {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            position: relative;
        }}

        .step-num {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #eff6ff;
            color: var(--primary);
            font-weight: 700;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #bfdbfe;
        }}

        .step-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--dark);
        }}

        .step-desc {{
            font-size: 0.88rem;
            color: var(--muted);
        }}

        .code-box {{
            background: #0f172a;
            color: #e2e8f0;
            padding: 12px 14px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            border: 1px solid #334155;
            position: relative;
        }}

        /* Credentials Box */
        .credentials-card {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 14px;
            padding: 18px 24px;
            margin-top: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .cred-item {{
            font-size: 0.9rem;
            color: #166534;
        }}

        .cred-item strong {{
            color: #14532d;
        }}

        .cred-code {{
            background: white;
            padding: 2px 8px;
            border-radius: 6px;
            border: 1px solid #86efac;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: #15803d;
        }}

        /* Notification toast */
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #0f172a;
            color: white;
            padding: 14px 22px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 1000;
        }}

        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* Footer */
        footer {{
            text-align: center;
            padding: 30px 20px;
            color: var(--muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            margin-top: 60px;
            background: white;
        }}
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <nav class="navbar">
        <a href="#" class="brand">
            <div class="brand-icon">
                <i class="fa-solid fa-store"></i>
            </div>
            <span>Shop Management System</span>
        </a>
        <div class="nav-tag">
            <i class="fa-solid fa-box-archive me-1"></i> mv-baldal.zip
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container">
        
        <!-- Hero & Download Card -->
        <div class="hero-card">
            <div class="badge-row">
                <span class="tech-badge"><i class="fa-brands fa-microsoft text-primary"></i> .NET 8 / 10 MVC</span>
                <span class="tech-badge"><i class="fa-solid fa-layer-group text-success"></i> 3-Tier Architecture (DAL/BAL/Web)</span>
                <span class="tech-badge"><i class="fa-solid fa-database text-warning"></i> MySQL DB</span>
                <span class="tech-badge"><i class="fa-solid fa-table-cells text-danger"></i> Kendo UI & POS Billing</span>
                <span class="tech-badge"><i class="fa-solid fa-file-pdf text-info"></i> 86-Page Guide PDF</span>
            </div>

            <h1 class="hero-title">Download Project <code style="color:#2563eb;">mv-baldal</code></h1>
            <p class="hero-subtitle">
                Complete clean source code package with database setup script, stored procedures, sample data, and complete 86-page implementation documentation.
            </p>

            <!-- Download Box -->
            <div class="download-box">
                <div class="download-btn-group">
                    <!-- Primary Download Button (Direct File Link + Embedded Fallback) -->
                    <button class="btn-download-primary" id="mainDownloadBtn" onclick="triggerDownload()">
                        <i class="fa-solid fa-download fa-lg"></i>
                        <span>Download ZIP Package</span>
                    </button>

                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">
                        Contains full solution: <strong>ShopManagement.Web</strong>, <strong>ShopManagement.Business</strong>, <strong>ShopManagement.DataAccess</strong>
                    </div>
                </div>

                <div class="file-meta">
                    <span class="file-meta-item">
                        <i class="fa-solid fa-file-zipper text-primary"></i>
                        <strong>mv-baldal.zip</strong> ({zip_size_mb:.2f} MB)
                    </span>
                    <span class="file-meta-item">
                        <i class="fa-regular fa-file-code text-success"></i>
                        120 Clean Files (No bin/obj bloat)
                    </span>
                    <span class="file-meta-item">
                        <i class="fa-regular fa-clock text-muted"></i>
                        Updated: {current_date}
                    </span>
                </div>
            </div>

            <!-- Alternative Download Options -->
            <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                <button class="btn-secondary-link" onclick="downloadViaBase64()">
                    <i class="fa-solid fa-bolt text-warning"></i>
                    Instant Embedded Download (Offline/No-Server)
                </button>
                <a href="ShopManagement_Project_Documentation.pdf" download="ShopManagement_Project_Documentation.pdf" class="btn-secondary-link">
                    <i class="fa-solid fa-file-pdf text-danger"></i>
                    Download 86-Page PDF Manual (2.3 MB)
                </a>
            </div>
        </div>

        <!-- Setup Instructions Section -->
        <div class="setup-section">
            <div class="section-header">
                <h2 class="section-title">
                    <i class="fa-solid fa-rocket text-primary"></i>
                    Setup on Your Other PC (3 Simple Steps)
                </h2>
                <p style="color: var(--muted); font-size: 0.95rem; margin-top: 4px;">
                    Follow these simple steps after downloading <code style="background:#e2e8f0;padding:2px 6px;border-radius:4px;">mv-baldal.zip</code>:
                </p>
            </div>

            <div class="steps-grid">
                <!-- Step 1 -->
                <div class="step-card">
                    <div class="step-num">1</div>
                    <div class="step-title">Unzip the Project</div>
                    <div class="step-desc">
                        Extract <code style="font-weight:600;">mv-baldal.zip</code> to any directory on your new PC (e.g. <code>C:\Projects\mv-baldal</code>).
                    </div>
                    <div class="code-box">
                        Expand-Archive mv-baldal.zip -DestinationPath .
                    </div>
                </div>

                <!-- Step 2 -->
                <div class="step-card">
                    <div class="step-num">2</div>
                    <div class="step-title">Setup MySQL Database</div>
                    <div class="step-desc">
                        Open MySQL CLI or Workbench and run the included <code>Database_Setup.sql</code> script to create tables and default admin data:
                    </div>
                    <div class="code-box">
                        mysql -u root -p &lt; Database_Setup.sql
                    </div>
                </div>

                <!-- Step 3 -->
                <div class="step-card">
                    <div class="step-num">3</div>
                    <div class="step-title">Build & Run Web App</div>
                    <div class="step-desc">
                        Open terminal in project root and execute dotnet run. The app will launch on <strong>localhost:5200</strong>:
                    </div>
                    <div class="code-box">
                        dotnet run --project ShopManagement.Web
                    </div>
                </div>
            </div>

            <!-- Default Credentials Box -->
            <div class="credentials-card">
                <div class="cred-item">
                    <i class="fa-solid fa-user-shield me-1"></i>
                    <strong>Admin Login:</strong> Username: <span class="cred-code">admin</span> | Password: <span class="cred-code">admin123</span>
                </div>
                <div class="cred-item">
                    <i class="fa-solid fa-cash-register me-1"></i>
                    <strong>Desk Cashier Login:</strong> Username: <span class="cred-code">desk1</span> | Password: <span class="cred-code">desk123</span>
                </div>
            </div>
        </div>

    </div>

    <!-- Toast Notification -->
    <div class="toast" id="toast">
        <i class="fa-solid fa-circle-check text-success fa-lg"></i>
        <span id="toastMsg">Downloading mv-baldal.zip...</span>
    </div>

    <!-- Footer -->
    <footer>
        <p>Shop Management System &bull; 3-Tier Enterprise Architecture &bull; Ready for deployment</p>
    </footer>

    <!-- Embedded Base64 Payload of mv-baldal.zip -->
    <script>
        // Full base64 payload of the 2.89 MB zip file
        const ZIP_BASE64_DATA = "{zip_b64}";

        function showToast(msg) {{
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            toast.classList.add('show');
            setTimeout(() => {{
                toast.classList.remove('show');
            }}, 3500);
        }}

        // Primary download: tries standard file link first, falls back to embedded Base64 Blob
        function triggerDownload() {{
            showToast("Starting download: mv-baldal.zip");
            
            // Try standard relative link first if file is hosted alongside index.html
            fetch('mv-baldal.zip', {{ method: 'HEAD' }})
                .then(response => {{
                    if (response.ok) {{
                        const a = document.createElement('a');
                        a.href = 'mv-baldal.zip';
                        a.download = 'mv-baldal.zip';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    }} else {{
                        // Fallback to base64
                        downloadViaBase64();
                    }}
                }})
                .catch(() => {{
                    // Fallback to base64 if fetch fails (e.g. file:// protocol or standalone HTML)
                    downloadViaBase64();
                }});
        }}

        // Embedded Base64 Blob download (works 100% offline, on GitHub Pages, single file host, etc.)
        function downloadViaBase64() {{
            showToast("Generating ZIP from embedded data...");
            try {{
                const byteCharacters = atob(ZIP_BASE64_DATA);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: 'application/zip' }});
                
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mv-baldal.zip';
                document.body.appendChild(a);
                a.click();
                
                setTimeout(() => {{
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    showToast("Downloaded mv-baldal.zip successfully!");
                }}, 500);
            }} catch (e) {{
                console.error("Error generating blob from Base64:", e);
                alert("Download error: " + e.message);
            }}
        }}
    </script>
</body>
</html>
"""

# Write index.html
with open(html_out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# Write download.html
with open(download_out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

html_size_mb = os.path.getsize(html_out_path) / (1024 * 1024)
print(f"Generated index.html: {html_size_mb:.2f} MB")
print(f"Generated download.html: {html_size_mb:.2f} MB")
print("Done!")
