import requests
import hashlib
from pathlib import Path
from datetime import datetime

# Official IFCT 2017 PDF URL from NIN
urls_to_try = [
    "https://www.nin.res.in/ebooks/IFCT2017.pdf",
    "https://www.nin.res.in/downloads/IFCT2017.pdf",
    "https://www.nin.res.in/IFCT2017.pdf",
]

output_dir = Path("data/raw/nutrition/IFCT_2017")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "IFCT2017.pdf"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

downloaded = False
for url in urls_to_try:
    print(f"Trying: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content-Length: {response.headers.get('Content-Length')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type.lower() or 'octet-stream' in content_type.lower():
                total_size = 0
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                print(f"  Downloaded: {total_size} bytes")
                downloaded = True
                break
            else:
                print(f"  Not a PDF (Content-Type: {content_type})")
        else:
            print(f"  Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

if downloaded:
    # Calculate hash
    hash_md5 = hashlib.md5()
    with open(output_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    
    file_size = output_path.stat().st_size
    
    print(f"\n✅ Download successful!")
    print(f"File: {output_path}")
    print(f"Size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
    print(f"MD5: {hash_md5.hexdigest()}")
    print(f"Downloaded: {datetime.utcnow().isoformat()}Z")
    
    # Save metadata
    metadata = {
        "source_url": url,
        "download_date": datetime.utcnow().isoformat() + "Z",
        "file_name": "IFCT2017.pdf",
        "file_size_bytes": file_size,
        "md5_hash": hash_md5.hexdigest(),
        "version": "IFCT 2017",
        "source_organization": "ICMR-National Institute of Nutrition (NIN)",
        "licence": "To be determined from PDF content",
        "notes": "Official Indian Food Composition Tables 2017"
    }
    
    import json
    with open(output_dir / "download_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {output_dir / 'download_metadata.json'}")
else:
    print("\n❌ All download attempts failed.")
    print("Manual download may be required from:")
    print("  https://www.nin.res.in/ebooks/IFCT2017.pdf")
    print("  https://www.nin.res.in/downloads/index.html")