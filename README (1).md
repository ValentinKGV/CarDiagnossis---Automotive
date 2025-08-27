
# 📖 README – Monitorizarea stării de funcționare a unui autovehicul prin OBD-II, utilizând ESP32 și Arduino

## 📌 Descriere proiect
Acest proiect implementează un sistem hardware-software pentru monitorizarea parametrilor unui autovehicul prin intermediul interfeței **OBD-II**.  
Datele sunt colectate cu ajutorul **ESP32** și transmise către un server **Flask**, unde sunt salvate într-o bază de date **SQLite** și afișate într-o aplicație web ușor de utilizat.

## 🎯 Obiective
- Monitorizarea în timp real a parametrilor motorului (RPM, viteză, temperatură, MAF etc.)  
- Afișarea datelor într-un dashboard web cu grafice și alerte  
- Stocarea sesiunilor pentru analiză ulterioară  
- Semnalarea automată a posibilelor defecțiuni  
- Oferirea unei soluții accesibile și extensibile, potrivită oricărui utilizator

## 🧱 Arhitectura sistemului
Proiectul urmează modelul **3-tier**:
1. **Frontend (prezentare)** – HTML, CSS, JavaScript, Chart.js, Jinja2  
2. **Backend (aplicație)** – Python, Flask, SQLAlchemy, API REST  
3. **Bază de date (date)** – SQLite pentru stocare locală  

Hardware-ul comunică prin protocol **CAN** și transmite datele către server prin **Wi-Fi**.

## 🛠️ Tehnologii utilizate
### Software
- **Python** (Flask, SQLAlchemy, Werkzeug security)  
- **SQLite** – bază de date lightweight  
- **Frontend** – HTML, CSS, JavaScript, Chart.js, Jinja2  

### Hardware
- **ESP32** – microcontroller cu Wi-Fi + Bluetooth  
- **Modul CAN SN65HVD230** – comunicație cu ECU  
- **Regulator TR10S3V3** – conversie 12V → 3.3V  
- **Diodă NUP2105L** – protecție supratensiune  
- **Arduino IDE** – dezvoltare și programare  

## ⚙️ Funcționalități
- Creare cont utilizator și autentificare securizată  
- Pornire / oprire sesiune de monitorizare auto  
- Afișare în timp real a parametrilor motorului  
- Istoric cu medii, alerte și detalii complete  
- Calcul putere și cuplu motor pe baza formulelor tehnice  

## 🧪 Testare
- **Postman** – verificare endpoint-uri API  
- **Wireshark** – analiză flux de date Wi-Fi (ESP32 ↔ Flask)  
- **Osciloscop** – validare comunicație CAN cu ECU  
- Testare manuală completă (înregistrare → monitorizare → salvare → istoric)  

## ⚖️ Comparație cu soluții existente
- Alte lucrări folosesc aplicații desktop sau fișiere CSV  
- Soluția propusă integrează un **dashboard web complet**, API REST și o arhitectură modulară  
- Folosirea transceiver-ului nativ **SN65HVD230** → comunicație mai stabilă decât ELM327  

## ✅ Concluzii
- Proiectul oferă o soluție accesibilă, fiabilă și ușor de utilizat  
- Îndeplinește obiectivele stabilite: monitorizare, stocare, prevenție  
- Arhitectura modulară permite extinderea ușoară  

## 🔮 Perspective viitoare
- Aplicație mobilă (Android/iOS)  
- Notificări automate (email / push) în caz de defecțiuni  
- Export rapoarte (PDF, CSV) pentru service auto  
- Suport pentru mai multe vehicule și conturi utilizator  
