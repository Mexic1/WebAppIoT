from flask import Flask, render_template, request, jsonify,redirect, url_for, session,flash
from azure.eventhub import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import threading
import time
import json
import pyodbc
import re


app = Flask(__name__)
app.secret_key = 'secret123'
# 🔹 Variabile Globale
received_temperature = None
received_humidity = None

EVENT_HUB_CONNECTION_STRING = "Endpoint=sb://ihsuproddbres037dednamespace.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=204trTHRb8HdtAxXONNIcWmERpe/OcoOSAIoTGt7Q2g=;EntityPath=iothub-ehub-arduinotem-63773205-02863a705e"
EVENT_HUB_NAME = "iothub-ehub-arduinotem-63773205-02863a705e"  
CONSUMER_GROUP = "$Default" 

# 🔹Funcție pentru a te conecta la baza de date Azure SQL
#----------------------------------------------------------------------
def get_db_connection():
    try:
        server = 'ps2n.database.windows.net'
        database = 'ps2n'
        username = 'Mexic'
        password = 'L0wlevel'
        driver = '{ODBC Driver 17 for SQL Server}'

        # Conectare la baza de date
        connection = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        return connection
    except Exception as e:
        print(f"❌ Eroare la conexiune: {e}")
        return None
    
def save_message_to_db(message_text):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO Mesaje (Mesaj, Data) VALUES (?, ?)", (message_text, current_time))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Eroare la salvarea mesajului: {e}")
#----------------------------------------------------------------------
# 🔹 Configurare SMTP pentru a trimite emailuri
#----------------------------------------------------------------------
def send_email(subiect,mesaj):
    SMTP_SERVER = 'smtp.mail.yahoo.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'cmorar100@yahoo.ro'
    SMTP_PASSWORD = 'bqsxrsfiecsrjpik'
    RECIPIENT_EMAIL = 'cmorar29@yahoo.com'

    message = MIMEMultipart()
    message['From'] = SMTP_USERNAME
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = subiect

    body = mesaj + time.strftime("%Y-%m-%d %H:%M:%S")
    message.attach(MIMEText(body, 'plain'))

    try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = message.as_string()
            server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, text)
            server.quit()
            print("E-mail trimis cu succes!")
    except Exception as e:
            print("Eroare la trimiterea e-mailului:", e)

#----------------------------------------------------------------------
# 🔹 Configurare Event Hub pentru a asculta mesajele de la Arduino
#----------------------------------------------------------------------
def on_event(partition_context, event):
    try:
        message_body = json.loads(event.body_as_str())
        if("temperature" in message_body and "humidity" in message_body):
            global received_temperature, received_humidity
            received_temperature = message_body["temperature"]
            received_humidity = message_body["humidity"]
        if("inundatie" in message_body):
            global received_water
            received_water = message_body["inundatie"]
            print(f"📩 New Message Received Inundatie: {message_body}")
            subiect = "Alerta inundatie!"
            mesaj = "A fost detectată o inundație la data și ora:"
            send_email(subiect, mesaj)
        if("hot" in message_body):
            print(f"📩 New Message Received TALHARI: {message_body}")
            subiect = "Alerta Talhari!"
            mesaj = "A fost detectată o tentativă de furt la data și ora:"
            send_email(subiect, mesaj)
            
    except json.JSONDecodeError:
        print("❌ Failed to decode message body.")
    partition_context.update_checkpoint()  

def threaded_event_listener():
    try:
            print("🔌 Starting Event Hub listener...")
            client = EventHubConsumerClient.from_connection_string(EVENT_HUB_CONNECTION_STRING, consumer_group=CONSUMER_GROUP)
            with client:
                client.receive(on_event, starting_position="@latest")  # Read latest messages
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Event Hub listener...")
    finally:
        client.close()

listener_thread = threading.Thread(target=threaded_event_listener, daemon=True)
listener_thread.start()
#----------------------------------------------------------------------
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# 🔹 Configurare Azure IoT Hub pentru a trimite comenzi către Arduino
#----------------------------------------------------------------------
CONNECTION_STRING = "HostName=arduinotemp.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=204trTHRb8HdtAxXONNIcWmERpe/OcoOSAIoTGt7Q2g="
DEVICE_ID = "EnabDevID"  
iot_hub_manager = IoTHubRegistryManager(CONNECTION_STRING)
#----------------------------------------------------------------------


# 🔹 Rutele Flask
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    parola = request.form['parola']
    repeat_parola = request.form['repeat_parola']

    if parola != repeat_parola:
        flash('Parolele nu coincid. Te rugăm să le verifici.')
        return redirect(url_for('home'))

    if not is_valid_email(email):
        flash('Email invalid. Formatul corect este exemplu@email.com')
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conturi WHERE email = ?", (email))
    existing_user = cursor.fetchone()

    if existing_user:
        flash('Email deja înregistrat.')
        return redirect(url_for('home'))
    
    cursor.execute("INSERT INTO conturi (email, parola) VALUES (?, ?)", (email, parola))
    conn.commit()
    conn.close()
    flash('Cont creat cu succes! Te poți autentifica.')
    return redirect(url_for('home'))

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    parola = request.form['parola']

    if not is_valid_email(email):
        flash('Email invalid. Formatul corect este exemplu@gmail.com')
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conturi WHERE email = ? AND parola = ?", (email, parola))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['email'] = email
        return redirect(url_for('index'))
    else:
        flash('Email sau parolă incorectă.')
        return redirect(url_for('home'))

@app.route("/index")
def index():
    if 'email' not in session:
        return redirect(url_for('home'))
    conn = get_db_connection()
    messages = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Mesaj, Data FROM Mesaje ORDER BY Data DESC")
            messages = [{"Mesaj": row[0], "Data": row[1].strftime("%Y-%m-%d %H:%M:%S")} for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            print(f"❌ Eroare la citirea mesajelor: {e}")
    
    return render_template("main.html", received_temperature=received_temperature, received_humidity=received_humidity, messages=messages)


@app.route("/get_telemetry")
def get_telemetry():
    
    return jsonify({
        "temperature": received_temperature,
        "humidity": received_humidity
    })

@app.route("/send_led_state", methods=["POST"])
def send_command():
    try:
        data = request.get_json()
        command = data["command"].lower()
        message = json.dumps({"command": command})
        iot_hub_manager.send_c2d_message(DEVICE_ID, message)
    except Exception as e:
        print(f"❌ Failed to send command: {e}")

    return jsonify({"status": "success", "message": "command"}), 200


@app.route("/send_custom_command", methods=["POST"])
def send_custom_command():
    try:
        data = request.get_json()
        command = data["message"]
        save_message_to_db(command)
        message = json.dumps({"message": command})
        iot_hub_manager.send_c2d_message(DEVICE_ID, message)

        return jsonify({
            "status": "success",
            "Mesaj": command,
            "Data": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

    #return jsonify({"status": "success", "message": "command"}), 200

if __name__ == "__main__":
    app.run(debug=True)
