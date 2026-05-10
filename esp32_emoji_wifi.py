# ESP32-C3 + Matrix WS2812B 8x8 - Emoji WiFi Controller
import gc, json, math, time, network, socket
from machine import Pin
import neopixel

LED_PIN = Pin(2)
NUM_LEDS = 64
MATRIX = 8
WIFI_SSID = 'klk'
WIFI_PASS = 'C0ntr4s3n@'
HTTP_PORT = 80

np = neopixel.NeoPixel(LED_PIN, NUM_LEDS)
brightness_val = 80
auto_cycle = True
selected_emoji = None

def xy(x, y):
    return y * MATRIX + (MATRIX - 1 - x) if y % 2 else y * MATRIX + x

def clear():
    for i in range(NUM_LEDS): np[i] = (0, 0, 0)
    np.write()

def wheel(pos):
    pos = pos % 256
    if pos < 85: return (255-pos*3, pos*3, 0)
    elif pos < 170: pos -= 85; return (0, 255-pos*3, pos*3)
    else: pos -= 170; return (pos*3, 0, 255-pos*3)

def draw_pixels(px, clr, br=1.0):
    c = tuple(int(v*br) for v in clr)
    for y in range(8):
        for x in range(8):
            np[xy(x,y)] = c if px[y][x] else (0,0,0)
    np.write()

def rgb(r,g,b):
    return tuple(int(v * brightness_val/100) for v in (r,g,b))

# 20 EMOJI PIXEL ART
EMOJIS = {}

def emoji(name, color):
    def dec(fn):
        EMOJIS[name] = (fn(), color)
    return dec

@emoji('Smiley', (255,220,0))
def _(): return [
    [0,0,0,0,0,0,0,0],[0,1,1,0,0,1,1,0],[0,0,0,0,0,0,0,0],
    [0,0,1,1,1,1,0,0],[0,1,0,0,0,0,1,0],[0,0,1,0,0,1,0,0],
    [0,0,0,1,1,0,0,0],[0,0,0,0,0,0,0,0]]

@emoji('Skull', (255,255,255))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,0,0,0,0,1,0],[1,0,1,0,0,1,0,1],
    [1,0,1,0,0,1,0,1],[0,1,0,1,1,0,1,0],[0,0,1,1,1,1,0,0],
    [0,0,1,0,0,1,0,0],[0,1,1,1,1,1,1,0]]

@emoji('Ghost', (200,200,255))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,0,0,0,0,1,0],[1,0,1,0,0,1,0,1],
    [1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1],[1,1,0,1,1,0,1,1],
    [1,0,0,1,1,0,0,1],[0,0,0,0,0,0,0,0]]

@emoji('Estrella', (255,220,0))
def _(): return [
    [0,0,0,1,1,0,0,0],[0,0,0,1,1,0,0,0],[0,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1],[0,1,1,1,1,1,1,0],[0,0,1,1,1,1,0,0],
    [0,0,1,0,0,1,0,0],[0,1,0,0,0,0,1,0]]

@emoji('Invader', (0,255,100))
def _(): return [
    [0,0,0,1,1,0,0,0],[0,1,0,1,1,0,1,0],[0,1,0,1,1,0,1,0],
    [1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,0,1,1,1,1,0,1],
    [0,0,1,0,0,1,0,0],[0,1,0,0,0,0,1,0]]

@emoji('Sol', (255,200,0))
def _(): return [
    [0,0,1,0,0,1,0,0],[1,0,0,1,1,0,0,1],[0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],[0,0,1,1,1,1,0,0],[0,1,1,1,1,1,1,0],
    [1,0,0,1,1,0,0,1],[0,0,1,0,0,1,0,0]]

@emoji('Luna', (255,255,180))
def _(): return [
    [0,1,1,1,1,0,0,0],[1,0,0,0,1,1,0,0],[0,0,0,0,0,1,1,0],
    [0,0,0,0,0,0,1,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,1,1,0],
    [0,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0]]

@emoji('Diamante', (100,200,255))
def _(): return [
    [0,0,0,1,1,0,0,0],[0,0,1,0,0,1,0,0],[0,1,0,0,0,0,1,0],
    [1,0,1,0,0,1,0,1],[0,1,0,0,0,0,1,0],[0,0,1,0,0,1,0,0],
    [0,0,0,1,1,0,0,0],[0,0,0,0,0,0,0,0]]

@emoji('Corona', (255,215,0))
def _(): return [
    [0,1,0,0,0,0,1,0],[1,1,1,0,0,1,1,1],[1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,0],[0,1,1,1,1,1,1,0],[0,0,1,1,1,1,0,0],
    [0,0,0,1,1,0,0,0],[0,0,0,0,0,0,0,0]]

@emoji('Hongo', (255,50,50))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,1,0,0,1,1,0],[1,1,0,0,0,0,1,1],
    [1,1,1,1,1,1,1,1],[0,0,1,1,1,1,0,0],[0,0,1,1,1,1,0,0],
    [0,0,1,1,1,1,0,0],[0,0,0,0,0,0,0,0]]

@emoji('Alien', (100,255,100))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,1,0,0,1,1,0],[1,0,0,0,0,0,0,1],
    [1,0,1,0,0,1,0,1],[0,1,1,1,1,1,1,0],[0,0,1,0,0,1,0,0],
    [0,0,1,0,0,1,0,0],[0,1,0,1,1,0,1,0]]

@emoji('Casa', (180,100,50))
def _(): return [
    [0,0,0,1,1,1,0,0],[0,0,1,1,1,1,1,0],[0,1,1,1,1,1,1,1],
    [1,1,1,0,0,1,1,1],[1,1,1,0,0,1,1,1],[1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],[0,1,1,0,0,1,1,0]]

@emoji('Auto', (255,80,80))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,0,0,0,0,1,0],[0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],[0,1,0,0,0,0,1,0],[1,1,0,1,1,0,1,1],
    [0,0,1,0,0,1,0,0],[0,0,0,0,0,0,0,0]]

@emoji('Trofeo', (255,200,0))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,1,0,0,1,1,0],[1,0,0,1,1,0,0,1],
    [0,0,1,0,0,1,0,0],[0,0,1,0,0,1,0,0],[0,0,1,1,1,1,0,0],
    [0,0,1,1,1,1,0,0],[1,1,1,1,1,1,1,1]]

@emoji('Paraguas', (80,80,255))
def _(): return [
    [0,1,1,1,1,1,1,0],[1,0,1,0,1,0,1,0],[1,1,1,1,1,1,1,1],
    [0,0,0,1,1,0,0,0],[0,0,0,1,1,0,0,0],[0,0,0,1,1,0,0,0],
    [0,0,1,0,0,1,0,0],[0,1,0,0,0,0,0,0]]

@emoji('Robot', (180,180,180))
def _(): return [
    [0,1,1,1,1,1,1,0],[1,0,1,0,0,1,0,1],[1,0,0,1,1,0,0,1],
    [0,1,1,1,1,1,1,0],[0,0,1,0,0,1,0,0],[0,1,1,0,0,1,1,0],
    [0,1,0,0,0,0,1,0],[0,1,1,0,0,1,1,0]]

@emoji('Nota', (255,100,200))
def _(): return [
    [0,0,1,1,0,0,0,0],[0,0,1,0,1,0,0,0],[0,0,1,0,0,1,0,0],
    [0,0,1,0,0,1,0,0],[0,0,1,0,0,1,0,0],[0,1,1,0,0,1,0,0],
    [1,1,1,1,1,1,0,0],[1,1,1,1,1,1,0,0]]

@emoji('Pirata', (255,255,255))
def _(): return [
    [0,0,1,1,1,1,0,0],[0,1,0,0,0,0,1,0],[1,0,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,1],[0,1,0,0,0,0,1,0],[0,0,1,1,1,1,0,0],
    [0,0,1,0,0,1,0,0],[0,1,0,1,1,0,1,0]]

print(f'EMOJIS loaded: {len(EMOJIS)}')
# ===== WIFI =====

ip_addr = None

def connect_wifi():
    global ip_addr
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("WiFi: conectando a " + WIFI_SSID + "...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(30):
            if wlan.isconnected():
                break
            time.sleep(0.5)
            print(".", end="")
        print()
    if wlan.isconnected():
        ip_addr = wlan.ifconfig()[0]
        print("WiFi: IP = " + ip_addr)
        return True
    print("WiFi: ERROR")
    return False

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', HTTP_PORT))
    s.listen(1)
    s.settimeout(0.05)
    return s

def http_process(server):
    global brightness_val, auto_cycle, selected_emoji
    try:
        conn, addr = server.accept()
        conn.settimeout(0.5)
        try:
            data = conn.recv(1024)
            if data:
                text = data.decode('utf-8', 'ignore')
                hdr_end = text.find('\r\n\r\n')
                body = text[hdr_end+4:].strip() if hdr_end >= 0 else ''
                cmd = None
                if body and body[0] == '{':
                    try: cmd = json.loads(body)
                    except: pass
                if cmd:
                    t = cmd.get('t', '')
                    if t == 'emoji':
                        selected_emoji = cmd.get('n', '')
                        print("[HTTP] Emoji: " + selected_emoji)
                        resp = '{"ok":true}'
                    elif t == 'bri':
                        brightness_val = max(1, min(100, int(cmd.get('v', 80))))
                        resp = '{"ok":true}'
                    elif t == 'auto':
                        auto_cycle = not auto_cycle
                        resp = '{"ok":true,"auto":' + str(auto_cycle).lower() + '}'
                    else:
                        resp = '{"ok":false}'
                    conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n' + resp.encode())
        except: pass
        try: conn.close()
        except: pass
    except OSError: pass

def main():
    global auto_cycle, selected_emoji, brightness_val
    clear()
    if not connect_wifi():
        for i in range(NUM_LEDS): np[i] = (40, 0, 0)
        np.write()
        return
    server = start_server()
    names = list(EMOJIS.keys())
    idx = 0
    pulse_t = 0
    print("HTTP: http://" + ip_addr + ":80/cmd")
    while True:
        http_process(server)
        if auto_cycle:
            pulse_t += 1
            if pulse_t >= 50:
                pulse_t = 0
                idx = (idx + 1) % len(names)
                selected_emoji = names[idx]
        if selected_emoji and selected_emoji in EMOJIS:
            px, clr = EMOJIS[selected_emoji]
            s = 0.8 + 0.2 * math.sin(pulse_t * 0.3)
            c = tuple(int(v * brightness_val / 100 * s) for v in clr)
            for y in range(8):
                for x in range(8):
                    np[xy(x,y)] = c if px[y][x] else (0,0,0)
        else:
            b = int(10 + 8 * math.sin(pulse_t * 0.15))
            for i in range(NUM_LEDS): np[i] = (0, 0, b)
        np.write()
        time.sleep(0.06)

if __name__ == '__main__':
    main()
