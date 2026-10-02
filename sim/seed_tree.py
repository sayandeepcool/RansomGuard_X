import os
import random
import string

def generate_dummy_files(base_dir="/kaggle/working/RansomGuard_X/RansomGuard_Test", num_files=2000):
    folders = ["Documents", "Projects", "Database", "Honeypot"]
    exts = [".txt", ".docx", ".csv", ".json", ".bin", ".py"]
    
    for folder in folders:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
        
    for i in range(num_files):
        folder = random.choice(folders)
        ext = random.choice(exts)
        filename = f"file_{i:04d}{ext}"
        filepath = os.path.join(base_dir, folder, filename)
        
        size = random.randint(512, 10240)
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=size)).encode()
        
        with open(filepath, "wb") as f:
            f.write(content)

if __name__ == "__main__":
    generate_dummy_files()
    print("Test environment seeded with dummy files successfully.")
