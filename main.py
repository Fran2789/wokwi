"""
ESP32 para Wokwi - Envía datos vía HTTP al backend (ngrok)
SIN MQTT - SOLO HTTP
Código corregido para tu wiring REAL
"""

import network
import time
from machine import PWM
import urequests as requests
from machine import Pin, ADC
import dht

# ========= CONFIG ==========
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

API_URL = "http://magnific-ariane-imperturbably.ngrok-free.dev"

# ========= HARDWARE (TU WIRING REAL) ==========

# Sensores
dht_sensor = dht.DHT22(Pin(4))   # DHT22 EN PIN 4 (COMO EN TU JSON)

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

# LEDs
led_blue = Pin(19, Pin.OUT)      # LED azul
led_red = Pin(17, Pin.OUT)       # LED rojo
led_green = Pin(27, Pin.OUT)     # LED verde

# Relay y buzzer
relay = Pin(23, Pin.OUT)
buzzer = Pin(26, Pin.OUT)

# Estado inicial
relay.value(0)
led_red.value(0)
led_green.value(0)
led_blue.value(0)

# ========= FUNCIONES ==========

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="")

        if wlan.isconnected():
            print("\n✅ WiFi conectado:", wlan.ifconfig()[0])
            return True
        else:
            print("\n❌ Error conectando WiFi")
            return False

    return True


def read_sensors():
    try:
        time.sleep(2)  # Necesario para evitar ETIMEDOUT

        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()

        ldr_value = ldr.read()
        light = int((ldr_value / 4095.0) * 1000)

        return {
            "temperature": temp,
            "humidity": hum,
            "light": light
        }

    except Exception as e:
        print(f"⚠️ Error leyendo sensores: {e}")
        return None


def send_to_backend(data):
    try:
        url = f"{API_URL}/sensor"
        headers = {"Content-Type": "application/json"}

        print("📤 Enviando datos al backend...")
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta:", result.get("message", ""))

            if "commands" in result:
                execute_commands(result["commands"])

            response.close()
            return True

        else:
            print("⚠️ Error HTTP:", response.status_code)
            response.close()
            return False

    except Exception as e:
        print("❌ Error enviando datos:", e)
        return False


def execute_commands(commands):
    if not commands:
        return

    print("🎮 Ejecutando comandos:", commands)

    # FAN
    if "fan" in commands:
        if commands["fan"] == "on":
            relay.value(1)
            led_red.value(1)
            led_green.value(0)
            beep()
            print("   🌀 Ventilador ON")

        elif commands["fan"] == "off":
            relay.value(0)
            led_red.value(0)
            led_green.value(1)
            print("   🌀 Ventilador OFF")

    # LIGHT 
    if "light" in commands:
     if commands["light_level"] == "on":
        led_blue.value(1)
     elif commands["light_level"] == "off":
        led_blue.value(0)


def beep():
    pwm = PWM(buzzer, freq=2000, duty=512)  # 2 kHz
    time.sleep(5.2)
    pwm.deinit()


def test_connection():
    try:
        print("🔍 Probando conexión a", API_URL)
        response = requests.get(f"{API_URL}/")

        if response.status_code == 200:
            print("✅ Backend responde correctamente")
            print("   Respuesta:", response.json())
            response.close()
            return True

        else:
            print("❌ Código HTTP:", response.status_code)
            response.close()
            return False

    except Exception as e:
        print("❌ No se puede conectar al backend:", e)
        return False


# ========= MAIN ==========
def main():
    print("\n🏠 ESP32 Smart Home - Wokwi + Ngrok\n")

    if not connect_wifi():
        print("WiFi no disponible. Abortando.")
        return

    beep()

    test_connection()

    print("\n🚀 Sistema iniciado\n")

    cycle = 1
    while True:
        print(f"\n--- Ciclo #{cycle} ---")

        data = read_sensors()

        if data:
            print("📊 Datos:", data)
            send_to_backend(data)

        cycle += 1
        time.sleep(10)


if __name__ == "__main__":
    main()
