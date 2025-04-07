# 🌐 Smart Monitoring System with Arduino & ESP8266

Acest proiect reprezintă un sistem inteligent de monitorizare care utilizează o placă **Arduino ATmega** și un modul **ESP8266** pentru a colecta și transmite date de la diferiți senzori către **cloud**. Aplicația web, realizată cu **Python (Flask)**, **HTML**, **CSS**, **Jinja2** și **AJAX**, permite controlul în timp real și vizualizarea datelor primite.

---

## ⚙️ Tehnologii utilizate

### 🧠 Hardware
- **Arduino UNO (ATmega328P)**
- **ESP8266 WiFi Module**
- **Senzor de temperatură și umiditate (DHT11 / DHT22)**
- **Senzor de apă / inundații**
- **Senzor pentru detecție mișcare / intruziune**

### ☁️ Software / Backend
- **Python 3.x**
- **Flask Framework**
- **Azure IoT Hub & Event Hub** pentru procesarea mesajelor din cloud
- **Azure SQL Database** pentru stocarea comenzilor trimise
- **smtplib** pentru trimitere alerte prin email

### 🌐 Frontend
- **HTML5 / CSS3 (custom & responsive design)**
- **Jinja2** pentru template rendering
- **AJAX (JavaScript)** pentru actualizare dinamică a datelor
- **Tabele interactive** pentru datele de telemetrie și comenzile trimise

---

## 📡 Funcționalități principale

- ✅ Afișare date în timp real (temperatură, umiditate)
- ✅ Alerte automate pe email pentru inundații sau intruziuni
- ✅ Control LED (ON/OFF/BLINK) de la distanță
- ✅ Trimitere comenzi personalizate către Arduino
- ✅ Salvarea comenzilor în baza de date și afișarea lor într-un tabel
- ✅ Interfață web modernă și responsive

---

## 🔧 Cum funcționează

1. Arduino colectează date de la senzori.
2. ESP8266 trimite aceste date către **Azure IoT Hub**.
3. Aplicația Flask ascultă aceste date prin **Event Hub** și le actualizează în frontend.
4. Comenzile trimise din site sunt direcționate către Arduino tot prin IoT Hub.
5. Comenzile sunt salvate și afișate în interfața web.

---

