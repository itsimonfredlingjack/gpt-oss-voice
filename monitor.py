import psutil
from speak import speak  # Vi lånar speak-funktionen från speak.py!

# Hämta CPU-last (mäter under 1 sekund)
print("mäter CPU...")
cpu_usage = psutil.cpu_percent(interval=1)

# Hämta RAM-användning
ram_info = psutil.virtual_memory()
ram_percent = ram_info.percent

# Hämta Disk-användning
disk_info = psutil.disk_usage('/')
disk_percent = disk_info.percent

# Skapa meddelandet - Jarvis style
# Vi avrundar siffrorna så det låter naturligt
message = (
    f"Statusrapport för servern. "
    f"Processorlasten ligger på {int(cpu_usage)} procent. "
    f"Minnesanvändningen är {int(ram_percent)} procent. "
    f"Hårddisken är fylld till {int(disk_percent)} procent."
)

if ram_percent > 80:
    message += " Varning! Minnet börjar ta slut."

print(f"Text som skickas: {message}")

# Skicka till högtalaren
speak(message)
