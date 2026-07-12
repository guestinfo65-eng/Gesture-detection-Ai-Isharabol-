# IshaaraBol — Sign to Speech 

Camera se hand signs aur head gestures padh kar bolne wala web app —
un logon ke liye jo bol nahi sakte.


## VS Code Mein Kholna

1. VS Code kholein
2. **File → Open Folder** → is `ishaarabol-project` folder ko select karein
3. Left side mein `index.html` dikhega

## Chalane Ke 2 Tareeqe

### Tareeqa A (Sabse Aasan): Live Server Extension

1. VS Code ke left side bar mein **Extensions** icon (chaar boxes wala) par click karein
2. Search karein: `Live Server`
3. **"Live Server" by Ritwick Dey** install karein
   (VS Code khud bhi is folder ko kholte hi ye recommend kar dega — "Install" dabana hai)
4. `index.html` file par **right-click** karein
5. **"Open with Live Server"** choose karein
6. Browser khud khul jayega — usme **"▶ Start Camera"** dabayein

### Tareeqa B: Bina Extension Ke — AI Assistant ke saath (Windows)

1. Pehli martaba: apna Fireworks AI API key environment variable mein set karein
   (Command Prompt mein): `set FIREWORKS_API_KEY=fw_your_key_here`
2. `run_windows.bat` file par **double-click** karein — bas Python honi chahiye,
   koi extra install nahi karna (server sirf Python ki standard library use karta hai)
3. Ek kaali window khulegi jo server chalayegi
4. Browser mein khud jaakar ye link kholein: `http://localhost:8080`or
after run the sever.py
http://127.0.0.1:8081/ (RECOMMENDED)
go to chrome/edge and type http://127.0.0.1:8080/
5. ▶ Start Camera dabayein

Agar `FIREWORKS_API_KEY` set nahi hai, AI Assistant offline (rule-based) jawab
deta rahega — baaki poora app usi tarah kaam karta hai.

### Mac/Linux

1. Terminal mein: `export FIREWORKS_API_KEY=fw_your_key_here` (optional —
   ek default key already `server.py` mein set hai)
2. `bash run_mac_linux.sh` (ya seedha `python3 server.py`)
3. Browser mein kholein: `http://localhost:8080`

> ⚠️ File ko seedha double-click karke browser mein na kholein (`file://` se) —
> camera security ki wajah se kaam nahi karegi. Hamesha upar wale 2 tareeqon mein se koi ek use karein.

## Zaroori Batein

- Chrome ya Edge browser use karein (best support)
- Pehli dafa chalane par internet chahiye (AI models download honge, ~15MB)
- Camera permission allow karna zaroori hai
- Sensitivity sliders (screen ke right side mein) adjust kar sakte hain agar
  gestures bohot jaldi ya bilkul detect na ho rahe hon

## Ishare Jo Ye Samajhta Hai

App ab **dono haath (2 hands)** ek saath track karta hai, na ke sirf ek.

### 5 Core one-hand gestures

| Gesture | Matlab |
|---|---|
| Sar upar-neeche hilana | Yes (ہاں) |
| Sar left-right hilana | No (نہیں) |
| Thumbs-up muh ke paas | Paani chahiye |
| Sab fingers mila kar muh chhuna | Bhook lagi hai |
| Haath + pucked lips | Kiss / Pyaar |

### 3 Naye two-hand combo gestures

| Gesture | Matlab |
|---|---|
| Dono khule haath aapas mein milakar muh/seene ke paas (namaste-style) | 🙏 Thank you (شکریہ) |
| Dono haath mutthi (fist) bana kar chehre ke upar utha na | 🆘 Help chahiye |
| Dono khule haath door-door, seedhe uthaye hue | ✋ Stop / Wait (رکو) |

###  My Signs — khud ke 100 custom sign

Fixed 224-combination library ab hata di gayi hai. Iski jagah, right side "My
Signs" panel se aap **khud tak 100 apne custom sign** record kar sakte hain:

1. Sign ka naam likhein (English zaroori, Urdu optional).
2. Camera ke saamne apna hand pose banayein.
3. "🔴 Record sign" dabayein aur 2 second steady rakhein.
4. Sign save ho jata hai — hamesha ke liye, `server.py` ke folder mein
   `custom_gestures.json` file mein (browser cache mein nahi, is liye
   restart ke baad bhi yaad rehta hai).

Ek ya dono haathon se sign record kiya ja sakta hai — jitne haath record ke
waqt dikhe, wahi baad mein match honge. Kisi bhi sign ko list se "✕" dabakar
delete kiya ja sakta hai.

##  Help Assistant (Fireworks AI, offline fallback ke saath)

Top right mein ek **"AI Assistant"** button hai. Isse click karke ek chat panel
khulta hai jo aapke sawalon ka jawab deta hai — gestures samajhne mein, camera
ya awaaz ki dikkat door karne mein, waghera.

Ye **Fireworks AI** (`server.py` ke zariye) se jawab deta hai — API key sirf
server side (`server.py` ke andar `DEFAULT_FIREWORKS_API_KEY`, ya
`FIREWORKS_API_KEY` environment variable) mein rehti hai, browser ke
JavaScript mein kahin nahi dikhti. Ek default key already `server.py` mein
daali hui hai to bina kuch set kiye bhi ye chal jayega — agar aap apni khud
ki key use karna chahein to bas `FIREWORKS_API_KEY` environment variable set
kar dein, wo default key ko override kar degi.

Agar key kaam na kare, ya Fireworks tak request na pahunche (internet down,
rate limit, waghera), assistant khud offline built-in rule-based jawab par
fall back kar jata hai (jaise "camera nahi chal raha", "sensitivity", "sab
gestures" jaise keywords se) — is se app kabhi bhi bilkul jawab dena band
nahi karta. Ab jab bhi Fireworks fail ho, chat mein khud hi asal wajah bhi
dikhti hai (sirf browser console mein nahi), taake pata chal sake ke masla
kya hai. Quick-tap buttons bhi diye gaye hain sabse common sawalon ke liye.

### 🔌 Connection kaise test karein

AI Assistant panel mein ek **"🔌 Test AI connection"** button hai — dabane par
seedha Fireworks ko ek chhota test message bhejta hai aur batata hai ke
connection theek hai ya nahi, aur agar nahi to exact wajah (galat API key,
model available nahi, internet down, waghera). Ye sirf `python server.py`
(ya `run_windows.bat` / `run_mac_linux.sh`) se chalane par kaam karta hai —
Live Server extension mode mein ye endpoint available nahi hota.

Agar `FIREWORKS_MODEL` (server.py mein) kisi wajah se available na ho (jaise
account mein wo model enabled na ho), server khud-b-khud ek doosre, aam
taur par available Fireworks model (`FIREWORKS_FALLBACK_MODEL`) se dubara
try karta hai — is se ek single galat model name se pura assistant band
nahi hota.

## Fix / Behtar Banana Ho To

Saara code `index.html` ke andar `<script type="module">` section mein hai.
Thresholds jahan tune karne hain, wahan comments mein likha hai
(jaise `MIN_RANGE`, `NEAR_MOUTH`, `maxPairDist` waghera).

Help Assistant ka code `// ---------- Help Assistant` comment ke baad shuru
hota hai, usi script section mein. Naye sawal-jawab add karne ho to
`ASSIST_RULES` array mein ek naya `{ keys: [...], reply: "..." }` object daal
dein.

Two-hand combo gestures ka code `classifyTwoHands()` function mein hai
(`// ---------- Two-hand combo gestures` comment ke paas) — naya combo add
karna ho to ek naya condition wahan daal dein aur `TWO_HAND_LIBRARY` object
mein uska English/Urdu/icon add kar dein.

Custom "My Signs" ka code `// ---------- Custom Sign Trainer` comment ke
paas hai (`classifyCustom`, `recordMySign`, `handToVector`). Storage
`server.py` ke `/api/gestures` endpoints se hoti hai, jo `custom_gestures.json`
file mein save/load karte hain — is file ko delete karne se sab custom signs
reset ho jayenge.
