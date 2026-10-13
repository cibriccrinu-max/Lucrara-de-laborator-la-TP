import requests

# Daca fisierul tau original avea deja aceste liste, le poti lasa pe acelea:
SITES = [
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://example.com",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "http://this-site-does-not-exist.invalid"
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options"
]

# Partea 1: Functii (build_url si is_https)
def build_url(host, path):
    if not path.startswith('/'):
        path = '/' + path
    return f"https://{host}{path}"

def is_https(url):
    return url.startswith("https://")


# Partea 2: Trimiterea unei cereri (show_response)
def show_response(url):
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")


# Partea 3: Un verificator reutilizabil (check_site)
def check_site(url):
    try:
        response = requests.get(url, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()

        return {
            "status": response.status_code,
            "content_type": content_type,
            "length": len(response.content),
            "server": response.headers.get("Server", "unknown")
        }
    except requests.exceptions.Timeout:
        return {"status": None, "error": "timeout"}
    except requests.exceptions.RequestException as e:
        return {"status": None, "error": str(e)}


# Partea 4: Verificarea mai multor site-uri (scan_sites)
def scan_sites():
    successful_sites = []
    failed_count = 0

    for site in SITES:
        result = check_site(site)
        if result.get("status") == 200:
            successful_sites.append((site, result))
        else:
            failed_count += 1

    successful_sites.sort(key=lambda item: item[1].get("length", 0), reverse=True)

    for site, result in successful_sites:
        print(f"{site}  -> {result['status']}, {result['length']} octeți")

    print(f"Reușite: {len(successful_sites)} | Eșuate: {failed_count}")


# Partea 5: Audit de securitate (check_headers)
def check_headers(url):
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        return {"status": None, "error": "timeout"}
    except requests.exceptions.RequestException as e:
        return {"status": None, "error": str(e)}

    present = []
    missing = []

    for header in SECURITY_HEADERS:
        if header in response.headers:
            present.append(header)
        else:
            missing.append(header)

    total = len(SECURITY_HEADERS)
    score = int((len(present) / total) * 100) if total > 0 else 0

    return {
        "present": present,
        "missing": missing,
        "score": score
    }


# Partea 6: Incercari repetate (retry_check)
def retry_check(url, attempts=3):
    last_status = None
    last_error = None
    actual_attempts = 0

    for i in range(1, attempts + 1):
        actual_attempts = i
        try:
            response = requests.get(url, timeout=5)
            last_status = response.status_code
            last_error = None

            if last_status < 500:
                return {
                    "status": last_status,
                    "attempts": actual_attempts
                }
        except requests.exceptions.RequestException as e:
            last_status = None
            last_error = str(e)

    rezultat = {
        "status": last_status,
        "attempts": actual_attempts
    }

    if last_error is not None:
        rezultat["error"] = last_error

    return rezultat