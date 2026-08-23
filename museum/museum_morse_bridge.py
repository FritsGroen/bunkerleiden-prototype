#!/usr/bin/env python3
import asyncio
import os
import ssl
from pathlib import Path

import serial
from aiohttp import web, WSMsgType

SERIAL_DEVICE = os.environ.get("MORSE_SERIAL", "/dev/ttyUSB0")
BAUD = int(os.environ.get("MORSE_BAUD", "115200"))
PORT = int(os.environ.get("MORSE_PORT", "8765"))
WEB_ROOT = Path(os.environ.get("MORSE_WEB_ROOT", "/opt/bunker-morse/www"))
CERT_FILE = os.environ.get("MORSE_CERT", "/opt/bunker-morse/tls/server.crt")
KEY_FILE = os.environ.get("MORSE_KEY", "/opt/bunker-morse/tls/server.key")

clients = set()
serial_ok = False
last_serial_line = ""

MUSEUM_CLIENT = r'''
<script>
(function(){
  let museumWs=null,retry=null;
  function museumStatus(text,state){
    const box=document.getElementById('serialStatus');
    const txt=document.getElementById('serialStatusText');
    const btn=document.getElementById('serialBtn');
    if(txt)txt.textContent=text;
    if(box)box.className='serialstatus'+(state?' '+state:'');
    if(btn){btn.textContent=museumWs&&museumWs.readyState===WebSocket.OPEN?'MUSEUMTASTER · VERBONDEN':'MUSEUMTASTER · VERBINDEN';btn.classList.toggle('connected',!!(museumWs&&museumWs.readyState===WebSocket.OPEN));}
  }
  function schedule(){clearTimeout(retry);retry=setTimeout(()=>connectMuseum(false),1800)}
  function route(line){
    const u=(line||'').trim().toUpperCase();
    if(u==='BRIDGE:CONNECTED'){museumStatus('MUSEUMTASTER · ORANGE PI VERBONDEN','on');return}
    if(u==='BRIDGE:SERIAL_ON'||u==='READY'){museumStatus('MUSEUMTASTER · ESP32 GEREED','on');return}
    if(u==='BRIDGE:SERIAL_OFF'){museumStatus('ORANGE PI BEREIKBAAR · ESP32 NIET GEVONDEN','bad');return}
    if((u==='TONE:ON'||u==='TONE:OFF')&&typeof handleEspLine==='function')handleEspLine(u);
  }
  function connectMuseum(force){
    if(museumWs&&(museumWs.readyState===WebSocket.OPEN||museumWs.readyState===WebSocket.CONNECTING)){
      if(!force)return;
      try{museumWs.close()}catch(e){}
    }
    clearTimeout(retry);museumStatus('MUSEUMTASTER · VERBINDEN…');
    try{
      museumWs=new WebSocket('wss://'+location.host+'/ws');
      museumWs.onopen=()=>museumStatus('MUSEUMTASTER · ORANGE PI VERBONDEN','on');
      museumWs.onmessage=e=>route(e.data);
      museumWs.onerror=()=>museumStatus('MUSEUMTASTER · GEEN VERBINDING','bad');
      museumWs.onclose=()=>{museumWs=null;museumStatus('MUSEUMTASTER · OPNIEUW VERBINDEN…','bad');schedule()};
    }catch(e){museumWs=null;museumStatus('MUSEUMTASTER · GEEN VERBINDING','bad');schedule()}
  }
  window.toggleEsp32=function(){connectMuseum(true)};
  setTimeout(()=>connectMuseum(false),700);
})();
</script>
'''


async def broadcast(message: str):
    if not clients:
        return
    dead = []
    for ws in list(clients):
        try:
            await ws.send_str(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


async def serial_worker(app):
    global serial_ok, last_serial_line
    loop = asyncio.get_running_loop()
    while True:
        ser = None
        try:
            ser = serial.Serial(SERIAL_DEVICE, BAUD, timeout=0.20)
            serial_ok = True
            await broadcast("BRIDGE:SERIAL_ON")
            while True:
                raw = await loop.run_in_executor(None, ser.readline)
                if not raw:
                    await asyncio.sleep(0.005)
                    continue
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                last_serial_line = line
                upper = line.upper()
                if upper in ("TONE:ON", "TONE:OFF", "KEY:DOWN", "KEY:UP", "READY"):
                    await broadcast(upper)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            serial_ok = False
            await broadcast("BRIDGE:SERIAL_OFF")
            print(f"Serial bridge waiting for {SERIAL_DEVICE}: {exc}", flush=True)
            await asyncio.sleep(2)
        finally:
            serial_ok = False
            if ser is not None:
                try:
                    ser.close()
                except Exception:
                    pass


async def ws_handler(request):
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    clients.add(ws)
    await ws.send_str("BRIDGE:CONNECTED")
    await ws.send_str("BRIDGE:SERIAL_ON" if serial_ok else "BRIDGE:SERIAL_OFF")
    if serial_ok:
        await ws.send_str("READY")
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT and msg.data == "PING":
                await ws.send_str("PONG")
    finally:
        clients.discard(ws)
    return ws


async def status_handler(request):
    return web.json_response({
        "ok": True,
        "serial": serial_ok,
        "device": SERIAL_DEVICE,
        "baud": BAUD,
        "clients": len(clients),
        "last_line": last_serial_line,
        "tls": Path(CERT_FILE).exists() and Path(KEY_FILE).exists(),
    })


async def index_handler(request):
    raise web.HTTPFound("/morse.html")


async def morse_handler(request):
    page = WEB_ROOT / "morse.html"
    if not page.exists():
        raise web.HTTPNotFound(text="morse.html ontbreekt")
    html = page.read_text(encoding="utf-8")
    if "MUSEUMTASTER · ORANGE PI VERBONDEN" not in html:
        html = html.replace("</body>", MUSEUM_CLIENT + "\n</body>", 1)
    return web.Response(text=html, content_type="text/html", headers={"Cache-Control": "no-store"})


async def on_startup(app):
    app["serial_task"] = asyncio.create_task(serial_worker(app))


async def on_cleanup(app):
    task = app.get("serial_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def build_app():
    app = web.Application()
    app.router.add_get("/", index_handler)
    app.router.add_get("/morse.html", morse_handler)
    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/status", status_handler)
    app.router.add_static("/", str(WEB_ROOT), show_index=False)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


def ssl_context():
    if not (Path(CERT_FILE).exists() and Path(KEY_FILE).exists()):
        return None
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    return ctx


if __name__ == "__main__":
    tls = ssl_context()
    scheme = "https" if tls else "http"
    print(f"Bunker Morse bridge: {SERIAL_DEVICE} @ {BAUD} -> {scheme}://0.0.0.0:{PORT}/", flush=True)
    web.run_app(build_app(), host="0.0.0.0", port=PORT, access_log=None, ssl_context=tls)
