# Python Socket File-Sharing (Mini-FTP)

A tiny client/server file-sharing system built on raw TCP sockets (Python standard library only).  
It supports basic filesystem operations and binary file transfer using a per-connection EOF token.

> Files in this repo:
> - `Server.py` – multithreaded TCP server
> - `Client.py` – interactive CLI client
> - `test.py` – smoke test (see notes to align HOST/PORT & imports)

---

## Features

- 🔐 **Per-connection EOF token** handshake (10-byte sentinel like `<Ab3X9kQw>`).
- 📁 **Directory ops:** `cd`, `mkdir`, `rm`
- 📦 **File ops:** `ul` (upload), `dl` (download), `info` (size), `mv` (move/rename)
- 🧵 **Threaded** server: one thread per client
- 📝 **Auto status**: after every command the server sends back its current working directory.

---

## How it works (Protocol)

1. **Connect:** Client connects to server `HOST:PORT`.
2. **Handshake:** Server generates and sends a random **EOF token** (10 chars, `<...>`).
3. **Welcome:** Server sends a one-time snapshot of its current directory (string) **ending with the EOF token**.
4. **Commands:** Client sends `"<command and args>" + EOF`.  
   Server executes, may stream file content or a result (always **ending with EOF**).
5. **Status:** After each command, server also sends its **current working directory path** + EOF.

> **Delimiter framing:** Both sides detect end-of-message by scanning for the exact EOF token bytes at the end of a packet.

---

## Supported commands (client → server)

| Command | Syntax | What it does | Server extra behavior |
|---|---|---|---|
| Change directory | `cd <dir-or-..>` | Changes server CWD | Sends updated CWD afterwards |
| Make directory | `mkdir <name>` | Creates subdirectory in server CWD | Sends updated CWD |
| Remove | `rm <file-or-empty-dir>` | Deletes a file or **empty** directory | Sends updated CWD |
| Upload | `ul <local_filename>` | Reads local file and uploads to server CWD | Sends updated CWD |
| Download | `dl <server_filename>` | Sends server file → client writes to local CWD | Sends updated CWD |
| Size info | `info <server_filename>` | Sends file size (bytes) | Sends size (immediate), then CWD |
| Move/Rename | `mv <file> <dest>` | If `<dest>` is a dir → move; else → rename within CWD | Sends updated CWD |
| Quit | `exit` | Close loop on client | – |

---

## Quick start

### 1) Prereqs
- Python 3.8+ (no external packages)

### 2) Run the server
```bash
python Server.py
# Server listening on 127.0.0.1 : 65438
```

### 3) Run the client (interactive CLI)
```bash
python Client.py
# Connected to server at IP: 127.0.0.1  and Port: 65438
# Handshake Done. EOF is: <Ab3X9kQw>
# Current Working Directory is : Current Directory: /path/to/server/cwd:
# |-- subdir1
# -- subdir2
# -- file.txt
```

### 4) Try a session
```
Enter Your Command : mkdir test_dir
Enter Your Command : cd test_dir
Enter Your Command : ul jellyfish.jpg
Enter Your Command : info jellyfish.jpg
Enter Your Command : dl jellyfish.jpg
Enter Your Command : cd ..
Enter Your Command : rm test_dir
Enter Your Command : exit
```

> **Tip:** For `ul`, place the file next to `Client.py` (your **client** CWD).  
> For `dl`, the file is saved into the client’s current directory.

---

## Project structure

```
.
├── Client.py   # interactive client
├── Server.py   # threaded server
└── test.py     # example smoke test
```

---

## Configuration

- Default host/port are defined at the bottom of each file:
  - `Server.py`: `HOST="127.0.0.1"`, `PORT=65438`
  - `Client.py`: `HOST="127.0.0.1"`, `PORT=65438`
