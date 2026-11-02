import requests, urllib3, json, time, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
urllib3.disable_warnings()

TV_IP = os.environ["TV_IP"]
AUTH = os.environ["VIZIO_AUTH"]
PORT = int(os.environ.get("PORT", "8100"))
H = {"AUTH": AUTH, "Content-Type": "application/json"}
S = requests.Session()
S.verify = False

KEYS = {
    "UP": (3, 8), "DOWN": (3, 0), "LEFT": (3, 1), "RIGHT": (3, 7), "OK": (3, 2),
    "BACK": (4, 0), "HOME": (4, 15), "MENU": (4, 8), "INFO": (4, 6), "EXIT": (9, 0),
    "VOL+": (5, 1), "VOL-": (5, 0), "MUTE": (5, 4), "CH+": (8, 1), "CH-": (8, 0),
    "PLAY": (2, 3), "PAUSE": (2, 2), "FWD": (2, 0), "REW": (2, 1),
    "INPUT": (7, 1), "POWER": (11, 2), "SMARTCAST": (4, 3),
}
KEYS.update({str(n): (6, n) for n in range(10)})
KEYS.update({"-": (6, 10), "CC": (4, 4), "PREV": (8, 2)})

APPS = {
    "YOUTUBE": {"NAME_SPACE": 5, "APP_ID": "1", "MESSAGE": "None"},
}

APPS["YOUTUBE 2"] = dict(APPS["YOUTUBE"])

APP_ICONS = {
    "YOUTUBE": '<svg width="44" height="30" viewBox="0 0 28 20"><rect width="28" height="20" rx="6" fill="#f00"/><path d="M11 5.5l7.5 4.5-7.5 4.5z" fill="#fff"/></svg>',
}

APP_ICONS["YOUTUBE 2"] = APP_ICONS["YOUTUBE"]

KEYMAP = {"ArrowUp": "UP", "ArrowDown": "DOWN", "ArrowLeft": "LEFT", "ArrowRight": "RIGHT",
          "Enter": "OK", "Backspace": "BACK", "Escape": "HOME", "=": "VOL+", "-": "VOL-",
          "m": "MUTE", " ": "PLAY", "p": "PAUSE", "i": "INFO", "y": "YOUTUBE"}
KEYMAP.update({str(n): str(n) for n in range(10)})

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Remote</title>
<style>
body{font:16px sans-serif;background:#111;color:#eee;padding:16px;max-width:280px;margin:0 auto;display:flex;flex-direction:column;gap:16px}
button{padding:16px 0;background:#333;color:#eee;border:0;border-radius:10px;cursor:pointer;font:inherit;display:flex;align-items:center;justify-content:center;gap:6px;touch-action:manipulation;user-select:none;-webkit-user-select:none}
button:active{background:#07f}
button.sm{padding:8px 0;font-size:13px}
button.tiny{padding:6px 0;font-size:12px;border-radius:6px}
svg.i{width:26px;height:26px;fill:currentColor}
.topbar{display:flex;justify-content:space-between;align-items:center}
.topbar button{padding:8px 18px;font-size:13px}
.apps{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.apps button{flex-direction:column;font-size:11px;min-height:72px;padding:10px 2px}
.apps.nolabels .lbl{display:none}
.numbers{display:flex;flex-direction:column;gap:8px}
.numbers-toggle{width:100%;padding:8px 0;font-size:13px}
.grp{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:12px;background:#1d1d1d;border:1px solid #484848;border-radius:16px}
.grp button{padding:20px 0;font-size:20px}
.grp button.tiny{padding:6px 0;font-size:12px;border-radius:6px}
.grp[hidden]{display:none}
.tr{display:grid;grid-template-columns:1fr 1fr 1.4fr 1fr 1fr;gap:8px}
.tr button{padding:14px 0}
.tr .big{background:#3a3a3a}
.mid{display:grid;grid-template-columns:1fr 0.7fr 1fr;gap:8px;align-items:stretch}
.pill{display:flex;flex-direction:column;gap:6px;padding:8px;background:#1d1d1d;border:1px solid #484848;border-radius:16px;text-align:center;font-size:12px;color:#aaa}
.pill div{display:flex;gap:6px}
.pill button{flex:1;font-size:22px;padding:14px 0}
.stack{display:flex;flex-direction:column;gap:6px;justify-content:center}
.dpad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:22px 0}
.dpad button{padding:22px 0;font-size:20px}
.sec{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.sec button{padding:10px 0;font-size:13px}
</style>
<div class=topbar id=topbar></div>
<div class="apps nolabels" id=apps></div>
<div class=numbers><button class=numbers-toggle id=numbers-toggle type=button aria-expanded=false aria-controls=nums>Numbers +</button><div class=grp id=nums hidden></div></div>
<div class=tr id=tr></div>
<div class=mid id=mid></div>
<div class=dpad id=dpad></div>
<div class=sec id=sec></div>
<script>
const appList=__APPS__, appIcons=__AICONS__, km=__KEYMAP__;
const $=id=>document.getElementById(id);
const send=u=>fetch(u).then(r=>r.text()).then(console.log);
const I={
 play:'<path d="M8 5v14l11-7z"/>',
 pause:'<path d="M6 5h4v14H6zM14 5h4v14h-4z"/>',
 prev:'<path d="M6 6h2v12H6zM20 6v12L9 12z"/>',
 rew:'<path d="M11 18V6l-8.5 6zm.5-6l8.5 6V6z"/>',
 fwd:'<path d="M4 18l8.5-6L4 6zm9-12v12l8.5-6z"/>',
};
const ic=n=>`<svg class=i viewBox="0 0 24 24">${I[n]}</svg>`;
const power='<svg class=i viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2.4 stroke-linecap=round><path d="M12 3v9"/><path d="M6.4 6.6a8 8 0 1 0 11.2 0"/></svg>';
const b=(k,label,c='')=>`<button class="${c}" data-k="${k}">${label??k}</button>`;
const blank='<span></span>';

$('topbar').innerHTML=b('INPUT',null,'sm')+'<button class=sm id=lbl-toggle type=button>Labels: off</button>'+b('POWER',power,'sm');
const home=b('HOME','<svg class=i viewBox="0 0 24 24"><path d="M12 3l9 8h-3v9h-5v-6h-2v6H6v-9H3z"/></svg><span class=lbl>HOME</span>');
const row=appList.map(n=>`<button data-k="${n}">${appIcons[n]||''}<span class=lbl>${n}</span></button>`);
row.splice(1,0,home);
$('apps').innerHTML=row.join('');
$('lbl-toggle').addEventListener('click',e=>{
  const off=$('apps').classList.toggle('nolabels');
  e.currentTarget.textContent='Labels: '+(off?'off':'on');
});
$('nums').innerHTML=['1','2','3','4','5','6','7','8','9'].map(k=>b(k,k,'tiny')).join('')+blank+b('0','0','tiny')+b('-','-','tiny');
const numbersToggle=$('numbers-toggle');
numbersToggle.addEventListener('click',()=>{
  const expanded=numbersToggle.getAttribute('aria-expanded')==='true';
  numbersToggle.setAttribute('aria-expanded',String(!expanded));
  $('nums').hidden=expanded;
  numbersToggle.textContent=expanded?'Numbers +':'Numbers −';
});
$('tr').innerHTML=b('PREV',ic('prev'))+b('REW',ic('rew'))+b('PLAY',ic('play'),'big')+b('PAUSE',ic('pause'))+b('FWD',ic('fwd'));
$('mid').innerHTML=`<div class=pill>CH<div>${b('CH-','&minus;')}${b('CH+','+')}</div></div>`
 +`<div class=stack>${b('MUTE','MUTE','tiny')}${b('CC','CC','tiny')}</div>`
 +`<div class=pill>VOL<div>${b('VOL-','&minus;')}${b('VOL+','+')}</div></div>`;
$('dpad').innerHTML=blank+b('UP','&#9650;')+blank
 +b('LEFT','&#9664;')+b('OK')+b('RIGHT','&#9654;')
 +blank+b('DOWN','&#9660;')+blank;
$('sec').innerHTML=b('BACK')+b('MENU')+b('INFO');

const REPEAT=new Set(['VOL+','VOL-']);   // keys that repeat while held
const route=k=>(appList.includes(k)?'/a/':'/k/')+encodeURIComponent(k);
let timer;
const stop=()=>clearInterval(timer);
const start=k=>{
  stop();
  navigator.vibrate?.(10);
  send(route(k));
  if(REPEAT.has(k)) timer=setInterval(()=>send(route(k)),120);
};

// mouse / touch
document.addEventListener('pointerdown',e=>{
  const el=e.target.closest('[data-k]');
  if(el){e.preventDefault();start(el.dataset.k);}
});
['pointerup','pointercancel'].forEach(t=>document.addEventListener(t,stop));

// keyboard
addEventListener('keydown',e=>{
  const k=km[e.key.length==1?e.key.toLowerCase():e.key];
  if(!k) return;
  e.preventDefault();
  if(!e.repeat) start(k);
});
addEventListener('keyup',stop);
addEventListener('blur',stop);
</script>"""
PAGE = (PAGE.replace("__APPS__", json.dumps(list(APPS)))
            .replace("__AICONS__", json.dumps(APP_ICONS))
            .replace("__KEYMAP__", json.dumps(KEYMAP)))

def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def reply(self, body, ctype="text/plain", code=200):
        self.send_response(code); self.send_header("Content-Type", ctype); self.end_headers()
        self.wfile.write(body.encode())
    def tv(self, name, path, payload):
        t = time.perf_counter()
        try:
            r = S.put(f"https://{TV_IP}:7345{path}", headers=H, timeout=5, json=payload)
            ms = (time.perf_counter() - t) * 1000
            log(f"{self.client_address[0]:<15} {name:<10} -> TV {r.status_code} ({ms:.0f}ms)")
            return self.reply(str(r.status_code))
        except requests.RequestException as e:
            log(f"{self.client_address[0]:<15} {name:<10} -> FAILED: {type(e).__name__}")
            return self.reply("TV unreachable", code=502)
    def do_GET(self):
        p = unquote(self.path)
        if p == "/":
            log(f"{self.client_address[0]:<15} page loaded")
            return self.reply(PAGE, "text/html")
        if p.startswith("/k/") and p[3:] in KEYS:
            cs, c = KEYS[p[3:]]
            return self.tv(p[3:], "/key_command/",
                {"KEYLIST": [{"CODESET": cs, "CODE": c, "ACTION": "KEYPRESS"}]})
        if p.startswith("/a/") and p[3:] in APPS:
            return self.tv(p[3:], "/app/launch", {"VALUE": APPS[p[3:]]})
        if p != "/favicon.ico":
            log(f"{self.client_address[0]:<15} 404 {p}")
        self.send_response(404); self.end_headers()

if __name__ == "__main__":
    srv = HTTPServer(("0.0.0.0", PORT), Handler)
    log(f"Remote running on port {PORT}, TV at {TV_IP}. Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        log("Stopping.")
    finally:
        srv.server_close()