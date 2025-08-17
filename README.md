To trigger the WOL
---------------------------------
1. Create a file exp. "wake.bat"

2. Paste this in:
@echo off
curl -X POST http://192.168.1.100:5000/wake -H "Content-Type: application/json" -d "{\"password\": \"yourpasswordhere\", \"mac\": \"AA:BB:CC:DD:EE:FF\"}"
pause

3. use a wrapper like Bat To Exe Converter (free)
