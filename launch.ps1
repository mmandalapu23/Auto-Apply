# Quick launcher for JobApply ATS application
cd "c:\Users\Mahesh\projects\JobApply\autoapply-ats\backend"
$env:SSL_CERT_FILE=""
$env:CURL_CA_BUNDLE=""
$env:REQUESTS_CA_BUNDLE=""
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
