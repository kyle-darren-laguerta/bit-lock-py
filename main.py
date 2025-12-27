import curses
import json
import os
from cryptography.fernet import Fernet

class VaultManager:
    def __init__(self):
        self.key = None
        self.cipher = None
        self.data = [] # List of {"platform": str, "acc_name": str, "password": str}

    def set_key(self, key_bytes):
        self.key = key_bytes
        self.cipher = Fernet(self.key)

    # Decrypt the text and parse in JSON 
    def parse_raw_text(self, encrypted_text):
        try:
            decrypted = self.cipher.decrypt(encrypted_text.encode()).decode()
            entries = decrypted.strip().split(" ")
            self.data = []
            for entry in entries:
                if entry.count(":") == 2:
                    p, a, pw = entry.split(":")
                    self.data.append({"platform": p, "acc_name": a, "password": pw})
            return True
        except:
            return False

    # Convert the array in a encryption-ready string and encrypt it
    def get_encrypted_blob(self):
        raw_string = " ".join([f"{i['platform']}:{i['acc_name']}:{i['password']}" for i in self.data])
        return self.cipher.encrypt(raw_string.encode()).decode()

def get_input(stdscr, prompt):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, prompt, curses.A_BOLD)
    stdscr.addstr(4, 2, "> ")
    input_str = stdscr.getstr(4, 4).decode('utf-8')
    curses.noecho()
    return input_str

def select_from_list(stdscr, title, items):
    """Generic arrow-key selection menu"""
    idx = 0
    if not items: return None
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, f"--- {title} ---", curses.A_BOLD)
        for i, item in enumerate(items):
            style = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(3 + i, 4, str(item), style)
        
        key = stdscr.getch()
        if key == curses.KEY_UP and idx > 0: idx -= 1
        elif key == curses.KEY_DOWN and idx < len(items)-1: idx += 1
        elif key in [10, 13]: return items[idx]
        elif key == 27: return None # ESC key

def main_menu(stdscr, vault):
    options = ["Show Password", "Add Password", "Modify Password", "Delete Password", "Exit"]
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "=== VAULT MASTER MENU ===", curses.A_BOLD)
        for i, opt in enumerate(options):
            style = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(3 + i, 4, f"{i+1}. {opt}", style)
        
        key = stdscr.getch()
        if key == curses.KEY_UP and idx > 0: idx -= 1
        elif key == curses.KEY_DOWN and idx < len(options)-1: idx += 1
        elif key in [10, 13]:
            if idx == 4: break 
            
            # 1. ADD PASSWORD (Direct Input)
            if idx == 1:
                p = get_input(stdscr, "Enter Platform:")
                a = get_input(stdscr, "Enter Account Name:")
                pw = get_input(stdscr, "Enter Password:")
                vault.data.append({"platform": p, "acc_name": a, "password": pw})
                continue

            # 2. SELECTION FLOW (Show, Modify, Delete)
            platforms = sorted(list(set(item['platform'] for item in vault.data)))
            selected_p = select_from_list(stdscr, "SELECT PLATFORM", platforms)
            
            if selected_p:
                accs = [item for item in vault.data if item['platform'] == selected_p]
                acc_labels = [item['acc_name'] for item in accs]
                selected_a_name = select_from_list(stdscr, f"ACCOUNTS FOR {selected_p}", acc_labels)
                
                if selected_a_name:
                    # Find exact reference in vault.data
                    target = next(item for item in vault.data if item['platform'] == selected_p and item['acc_name'] == selected_a_name)
                    
                    if idx == 0: # Show
                        stdscr.clear()
                        stdscr.addstr(2, 2, f"Platform: {target['platform']}")
                        stdscr.addstr(3, 2, f"Account:  {target['acc_name']}")
                        stdscr.addstr(4, 2, f"Password: {target['password']}", curses.A_BOLD)
                        stdscr.addstr(6, 2, "Press any key to return...")
                        stdscr.getch()
                    
                    elif idx == 2: # Modify
                        target['password'] = get_input(stdscr, f"New Password for {selected_a_name}:")
                    
                    elif idx == 3: # Delete
                        vault.data.remove(target)
                        stdscr.addstr(10, 2, "Deleted. Press any key.")
                        stdscr.getch()

    # Final Save and Encryption
    final_blob = vault.get_encrypted_blob()
    with open("vault_output.txt", "w") as f:
        f.write(final_blob)
    
    stdscr.clear()
    stdscr.addstr(2, 2, "VAULT UPDATED AND ENCRYPTED", curses.A_BOLD)
    stdscr.addstr(4, 2, f"Secret Key: [Stored in secret.key]")
    stdscr.addstr(5, 2, f"Encrypted Text saved to: vault_output.txt")
    stdscr.addstr(7, 2, "Press any key to close system.")
    stdscr.getch()

def entry_screen(stdscr):
    vault = VaultManager()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
    
    # Step 1: Key Management
    choice = select_from_list(stdscr, "Bitlock PY", ["1. Input Secret Key", "2. Generate New Secret Key"])
    
    if choice == "1. Input Secret Key":
        key_str = get_input(stdscr, "Paste Secret Key:")
        vault.set_key(key_str.encode())
    else:
        new_key = Fernet.generate_key()
        with open("secret.key", "wb") as f: f.write(new_key)
        vault.set_key(new_key)
        stdscr.addstr(5, 2, "Key saved to 'secret.key'. Press any key...")
        stdscr.getch()

    # Step 2: Paste Encrypted Text
    enc_text = get_input(stdscr, "Paste Encrypted Blob (Leave blank for new vault):")
    if enc_text.strip():
        if not vault.parse_raw_text(enc_text):
            stdscr.addstr(10, 2, "ERROR: Invalid Key or Corrupt Data.", curses.A_BOLD)
            stdscr.getch()
            return
    
    main_menu(stdscr, vault)

if __name__ == "__main__":
    curses.wrapper(entry_screen)