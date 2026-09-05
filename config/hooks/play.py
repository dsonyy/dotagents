#!/usr/bin/env python3
import os, platform, struct, subprocess, wave, math

SOUND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ding.wav")


def generate(path, freq=880, duration=0.4, rate=44100):
    n = int(rate * duration)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        for i in range(n):
            t = i / rate
            amp = 32767 * math.exp(-8 * t / duration)
            f.writeframes(struct.pack("<h", int(amp * math.sin(2 * math.pi * freq * t))))


def play():
    if not os.path.exists(SOUND):
        generate(SOUND)

    system = platform.system()
    if system == "Darwin":
        subprocess.run(["afplay", SOUND], check=False)
    elif system == "Windows":
        subprocess.run(["powershell", "-c", f'(New-Object Media.SoundPlayer "{SOUND}").PlaySync()'], check=False)
    elif system == "Linux":
        if "microsoft" in platform.uname().release.lower():
            win = subprocess.check_output(["wslpath", "-w", SOUND]).decode().strip()
            subprocess.run(["powershell.exe", "-c", f'(New-Object Media.SoundPlayer "{win}").PlaySync()'], check=False)
        else:
            for cmd in [["paplay", SOUND], ["aplay", SOUND], ["ffplay", "-nodisp", "-autoexit", SOUND]]:
                if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
                    subprocess.run(cmd, check=False)
                    return


if __name__ == "__main__":
    play()
