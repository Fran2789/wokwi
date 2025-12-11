import requests

API_URL = "http://magnific-ariane-imperturbably.ngrok-free.dev"

def send_sensor_data(temperature, humidity, light):
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "light": light
    }
    r = requests.post(f"{API_URL}/sensor", json=data)
    print(f"[Sensor] Status: {r.status_code}")
    print(f"[Sensor] Response: {r.text}")

def send_control(actuator, action):
    data = {
        "actuator": actuator,
        "action": action
    }
    r = requests.post(f"{API_URL}/control", json=data)
    print(f"[Control] Status: {r.status_code}")
    print(f"[Control] Response: {r.text}")

def main_menu():
    while True:
        print("\n=== TEST EVENTS MENU ===")
        print("1. Enviar datos de sensores")
        print("2. Controlar actuador (ventilador/luz)")
        print("3. Salir")
        choice = input("Selecciona una opción: ")
        if choice == "1":
            temp = float(input("Temperatura: "))
            hum = float(input("Humedad: "))
            light = float(input("Luz: "))
            send_sensor_data(temp, hum, light)
        elif choice == "2":
            actuator = input("Actuador (fan/light): ").strip()
            action = input("Acción (on/off/toggle): ").strip()
            send_control(actuator, action)
        elif choice == "3":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main_menu()
