import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
from machine import Pin
import rp2
import sys

# Windows Hotspot
#ssid (Uporabniško ime Windows Hotspot-a)
#password (Geslo Windows Hotspot-a)

# Raspberry Pi Hotspot
ssid = 'RaspberryTips-WiFi'
password = 'RPIjedober.12'

led1 = Pin('GP22', Pin.OUT)
led2 = Pin('GP21', Pin.OUT)
led3 = Pin('GP20', Pin.OUT)
IR_led = Pin('GP26', Pin.OUT)

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    return ip

def open_socket(ip):
    address = (ip, 3005)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection
    
def webpage(temperature, stateLED, stateLED1, stateLED2, stateLED3, stateSEM, stateIR, field_Odg):
    
    temperatura = temperature
    state = stateLED
    
    style = "<style> \
               body { \
                   font-family: 'Times New Roman'; \
               } \
               header { \
                    background-color: #f5fffa; \
                    padding: 18px; \
                    grid-area: header; \
                    position: relative; \
                    text-align: center; \
                    font-size: 20px; \
                    font-weight: bold; \
                    padding-bottom: 20px; \
                    padding-top: 20px; \
                    margin: auto; \
               } \
               #content1 { \
                   background-color:  #f5fffa; \
                   margin: auto; \
                   padding: 8px; \
                   text-align: center; \
                   font-weight: bold; \
                   font-size: 17px; \
                   align-self: flex-start; \
                } \
                #content2 { \
                   background-color: #fffacd; \
                   margin: auto; \
                   padding: 10px; \
                   text-align: left; \
                   font-size: 17px; \
                } \
                .center-text { \
                   text-align: center; \
                } \
                #content3 { \
                   background-color: #ffffe0; \
                   margin: auto; \
                   padding: 10px; \
                   text-align: center; \
                   font-size: 20px; \
                } \
           </style>"
    
    optionsChart = "{ type: 'line', \
    data: { \
        labels: labels, \
        datasets: [{ \
            label: 'Temperature (°C)', \
            data: data, \
            borderColor: 'red', \
            fill: false \
        }] \
    }, \
    options: { scales: { y: { beginAtZero: false } } } \
    }"
    
    PR_fetchData = "{ \
    let res = await fetch('/temp'); \
    let json = await res.json(); \
    let now = new Date().toLocaleTimeString(); \
    labels.push(now); \
    data.push(json.temperature); \
    if (labels.length > 20) { labels.shift(); data.shift(); } \
    localStorage.setItem('labels', JSON.stringify(labels)); \
    localStorage.setItem('data', JSON.stringify(data)); \
        chart.update(); \
    }"
    
    html= f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n
\r\n
           <!DOCTYPE html>
           <html>
           <head>
           <title>LED in temperatura</title>
           <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
           {style}
           </head>
           <body>
           <header>
           <h1>Priziganje LED diode</h1>
           </header>
           <div id="content1">
           <p>Tukaj boste lahko prizigali LED diode na razlicne nacine.</p>
           </div>
           <div id="content2">
           <form action="./lighton">
           <p><b>Vklop LED diode.</b></p>
           <input type="submit" value="Light on" />
           </form>
           <p><b>Izklop LED diode.</b></p>
           <form action="./lightoff">
           <input type="submit" value="Light off" />
           </form>
           <p><b>Klikanje vklop/izklop na posameznih LED diodah (na GPIO).</b></p>
           <p><b>Vklop/Izklop LED1 dioda.</b></p>
           <form action="./lightonLED1">
           <input type="submit" value="LED1 on" />
           </form>
           <form action="./lightoffLED1">
           <input type="submit" value="LED1 off" />
           </form>
           <p><b>Vklop/Izklop LED2 dioda.</b></p>
           <form action="./lightonLED2">
           <input type="submit" value="LED2 on" />
           </form>
           <form action="./lightoffLED2">
           <input type="submit" value="LED2 off" />
           </form>
           <p><b>Vklop/Izklop LED3 dioda.</b></p>
           <form action="./lightonLED3">
           <input type="submit" value="LED3 on" />
           </form>
           <form action="./lightoffLED3">
           <input type="submit" value="LED3 off" />
           </form>
           <p><b>Tukaj boste lahko prizgali ali ugasnili semafor.</b></p>
           <p><b>Vklop/Izklop semaforja.</b></p>
           <form action="./lightonSemaphore">
           <input type="submit" value="Semaphore on" />
           </form>
           <form action="./lightoffSemaphore">
           <input type="submit" value="Semaphore off" />
           </form>
           <p><b>Tukaj boste lahko prizgali ali ugasnili IR (infrardeca)</b></p>
           <p><b>Vklop/Izklop IR (infrardeca).</b><p>
           <form action="./lightonIR">
           <input type="submit" value="IR on" />
           </form>
           <form action="./lightoffIR">
           <input type="submit" value="IR off" />
           </form>
           <p><b>Prekinitev povezave z omrezjem.</b></p>
           <form action="./close">
           <input type="submit" value="Stop server" />
           </form>
           <p><b>Prikazovanje stanje o LED diodah.</b></p>
           <p>LED is {stateLED}.</p>
           <p><b>Prikazovanje stanje o LED1 diodah.</b></p>
           <p>LED is {stateLED1}.</p>
           <p><b>Prikazovanje stanje o LED2 diodah.</b></p>
           <p>LED is {stateLED2}.</p>
           <p><b>Prikazovanje stanje o LED3 diodah.</b></p>
           <p>LED is {stateLED3}.</p>
           <p><b>Prikazovanje stanje semaforja.</b></p>
           <p>Semaphore is {stateSEM}.</p>
           <p><b>Prikazovanje IR stanje</b></p>
           <p>IR is {stateIR}.</p>
           <p><b>Prikazovanje temperature v okolici.</b></p>
           <p>Temperature is {temperature} °C.</p>
           </div>
           <div id="content3">
           <p><b>Danasnji kviz: </b></p>
           <p><b>Kateri program je nastal prvi?</b></p>
           <form action="./clickJava">
           <input type="submit" value="Java" />
           </form>
           <form action="./clickPython">
           <input type="submit" value="Python" />
           </form>
           <form action="./clickMicroPy">
           <input type="submit" value="MicroPy" />
           </form>
           <p><b>Odgovor je {field_Odg}.</b></p>
           </div>
           <h1 class="center-text">Graficni prikaz temperature</h1>
           <canvas id="tempChart" width="400" height="200"></canvas>
           <script>
           let labels = JSON.parse(localStorage.getItem("labels")) || [];
           let data = JSON.parse(localStorage.getItem("data")) || [];
           let ctx = document.getElementById('tempChart').getContext('2d');
           let chart = new Chart(ctx, {optionsChart});
           
           async function fetchData() {PR_fetchData}
           
           setInterval(fetchData, 6000);
           </script>
           </body>
           </html>
           """
    return str(html)

def serve(connection):
    stateLED = 'ON'
    stateLED1 = 'OFF'
    stateLED2 = 'OFF'
    stateLED3 = 'OFF'
    stateSEM  = 'OFF'
    stateIR   = 'OFF'
    field_Odg = '___'
    pico_led.on()
    led1.value(0)
    led2.value(0)
    led3.value(0)
    IR_led.value(0)
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, stateLED, stateLED1, stateLED2, stateLED3, stateSEM, stateIR, field_Odg)
        if "GET /temp" in request:
            try:
                temperature_sensor = pico_temp_sensor.temp
                response = '{{"temperature": {:.2f}}}'.format(temperature_sensor)
                client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
                client.send(response)
            except Exception as e:
                client.send("HTTP/1.1 500 Internal Server Error\r\n\r\n")
        else:
            try:
                request = request.split()[1]
            except IndexError:
                pass
            if request == '/lighton?':
                pico_led.on()
                stateLED = 'ON'
            elif request == '/lightoff?':
                pico_led.off()
                stateLED = 'OFF'
            elif request == '/lightonLED1?':
                led1.value(1)
                stateLED1 = 'ON'
            elif request == '/lightoffLED1?':
                led1.value(0)
                stateLED1 = 'OFF'
            elif request == '/lightonLED2?':
                led2.value(1)
                stateLED2 = 'ON'
            elif request == '/lightoffLED2?':
                led2.value(0)
                stateLED2 = 'OFF'
            elif request == '/lightonLED3?':
                led3.value(1)
                stateLED3 = 'ON'
            elif request == '/lightoffLED3?':
                led3.value(0)
                stateLED3 = 'OFF'
            elif request == '/lightonSemaphore?':
                led1.value(1)
                led2.value(0)
                led3.value(0)
                stateLED1 = 'ON'
                sleep(6)
                led1.value(0)
                led2.value(1)
                led3.value(0)
                sleep(0.5)
                led1.value(0)
                led2.value(0)
                led3.value(1)
                sleep(6)
                led1.value(0)
                led2.value(1)
                led3.value(0)
                sleep(3)
                led1.value(1)
                led2.value(0)
                led3.value(0)
                stateSEM = 'ON'
            elif request == '/lightoffSemaphore?':
                led1.value(0)
                led2.value(0)
                led3.value(0)
                stateSEM = 'OFF'
                stateLED1 = 'OFF'
            elif request == '/lightonIR?':
                IR_led.value(1)
                stateIR = 'ON'
            elif request == '/lightoffIR?':
                IR_led.value(0)
                stateIR = 'OFF'
            elif request == '/clickJava?':
                led1.value(0)
                led2.value(1)
                led3.value(0)
                stateLED1 = 'OFF'
                stateLED2 = 'ON'
                stateLED3 = 'OFF'
                field_Odg = 'delno pravilen'
            elif request == '/clickPython?':
                led1.value(0)
                led2.value(0)
                led3.value(1)
                stateLED1 = 'OFF'
                stateLED2 = 'OFF'
                stateLED3 = 'ON'
                field_Odg = 'pravilen'
            elif request == '/clickMicroPy?':
                led1.value(1)
                led2.value(0)
                led3.value(0)
                stateLED1 = 'ON'
                stateLED2 = 'OFF'
                stateLED3 = 'OFF'
                field_Odg = 'napacen'
            elif request == '/close?':
                sys.exit()
            client.send(html)
        client.close()
        
ip = connect()
connection = open_socket(ip)
serve(connection)