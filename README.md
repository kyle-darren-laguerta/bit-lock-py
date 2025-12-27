# 🔐 Bitlock PY – Terminal Password Vault

Bitlock PY is a **terminal-based password vault** written in Python using `curses` for the UI and **Fernet symmetric encryption** for secure storage. It allows you to **add, view, modify, and delete passwords** inside an encrypted vault file.

This is a simpler yet powerful replica of Bitlock, originally written in C. It removes the account system, allowing you to decrypt the encrypted string on any device as long as you know the master key.

---

## ✨ Features

- 🔒 **Strong encryption** using `cryptography.fernet`
- 🖥️ **Interactive terminal UI** (arrow-key navigation)
- 🔑 **Secret key support**
  - Generate a new key
  - Or input an existing one
- 📦 Encrypted vault stored as a single text blob
- 🗂️ Passwords organized by **platform** and **account name**

---

## 📁 Files Generated

| File | Purpose |
|------|---------|
| `secret.key` | Stores the encryption key |
| `vault_output.txt` | Encrypted password vault |

⚠️ **Do NOT lose `secret.key`** — your vault cannot be decrypted without it.

---

## 🛠️ Requirements

- Python **3.8+**
- Linux / macOS terminal (Windows WSL recommended)

### Python Dependencies

```bash
pip install cryptography
pip install windows-curses # For Windows
```

> `curses` is included by default on Linux/macOS.

---

## ▶️ How to Run

```bash
python main.py
```

(Replace `main.py` with your filename.)

---

## 🔑 Startup Flow

1. **Choose Key Option**
   - Input existing secret key  
   - OR generate a new one (saved as `secret.key`)

2. **Paste Encrypted Vault (Optional)**
   - Leave blank to create a new vault
   - Paste existing encrypted text to load old data

3. **Access Main Menu**
   - Show Password
   - Add Password
   - Modify Password
   - Delete Password
   - Exit (auto-encrypts & saves)

---

## ⚠️ Warning

Termination without exit will not saved the changes

---

---

## 🧠 Vault Data Format (Internal)

Passwords are internally stored as:

```
platform:account_name:password
```

Multiple entries are space-separated and then encrypted into one blob.

Example (before encryption):
```
github:kolps:password123 google:plok@gmail.com:secretpswd
```

---

## 🔐 Security Notes

- Uses **Fernet symmetric encryption**
- No plaintext passwords are saved to disk
- Key and encrypted vault are stored separately
- Anyone with **both the key and vault file** can decrypt the data

---

## ⚠️ Limitations

- Passwords are displayed in plaintext when viewing
- No password masking (terminal limitation)
- No password strength validation
- No clipboard support

---


