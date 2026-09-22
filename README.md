# QuickShare

A local phone-to-PC and PC-to-phone file transfer tool.

## 1. Install Python

Install Python 3.10 or newer on your PC.

## 2. Start the server

Open Command Prompt inside this folder and run:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## 3. Open it on your phone

1. Connect your phone and PC to the same Wi-Fi.
2. On the PC, run `ipconfig`.
3. Find the PC's IPv4 address, for example `192.168.1.5`.
4. Open this address on your phone:

```text
http://192.168.1.5:8000
```

If Windows Firewall asks for permission, allow Python on your private network.

## Notes

- Uploaded files are stored in the `uploads` folder.
- This is intended for use on a trusted local network.
- Do not expose this server directly to the public internet.
