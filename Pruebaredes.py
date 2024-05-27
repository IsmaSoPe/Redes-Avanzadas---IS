import os
import sys
import logging
import sqlite3
from getpass import getpass
from colorama import init, Fore, Style

# Inicializar colorama
init()

# Configurar logging
logging.basicConfig(filename='network_management.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Conexión a la base de datos
conn = sqlite3.connect('network_management.db')
c = conn.cursor()

# Crear tablas si no existen
c.execute('''CREATE TABLE IF NOT EXISTS campus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE)''')
c.execute('''CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                mask TEXT NOT NULL,
                services TEXT NOT NULL,
                layer TEXT NOT NULL,
                campus_id INTEGER,
                FOREIGN KEY(campus_id) REFERENCES campus(id))''')
conn.commit()

# Funciones de autenticación
def authenticate():
    username = input("Ingrese su usuario: ")
    password = getpass("Ingrese su contraseña: ")
    # Aquí se podría implementar una verificación real
    if username == 'admin' and password == 'admin':
        logging.info(f"Usuario {username} autenticado con éxito")
        return True
    else:
        logging.warning(f"Intento de autenticación fallido para el usuario {username}")
        print(Fore.RED + "Autenticación fallida" + Style.RESET_ALL)
        return False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("Presione Enter para continuar...")

def display_menu():
    clear_screen()
    print(Fore.GREEN + "¿Qué desea hacer?" + Style.RESET_ALL)
    print("1. Ver los dispositivos.")
    print("2. Ver los campus.")
    print("3. Añadir dispositivo.")
    print("4. Añadir campus.")
    print("5. Borrar dispositivo.")
    print("6. Borrar campus.")
    print("7. Generar reporte PDF.")
    print("8. Salir")
    return input("Elija una opción: ")

def list_campuses():
    c.execute("SELECT * FROM campus")
    campuses = c.fetchall()
    for idx, item in enumerate(campuses, start=1):
        print(f"{idx}. {item[1]}")

def view_devices():
    clear_screen()
    print("Elegir un campus")
    list_campuses()
    selector = int(input("\nElija una opción: ")) - 1
    c.execute("SELECT * FROM campus")
    campuses = c.fetchall()
    if 0 <= selector < len(campuses):
        campus_id = campuses[selector][0]
        c.execute("SELECT * FROM devices WHERE campus_id=?", (campus_id,))
        devices = c.fetchall()
        clear_screen()
        if devices:
            for device in devices:
                print(f"Dispositivo: {device[1]}")
                print(f"Dirección IP: {device[2]}")
                print(f"Máscara de Red: {device[3]}")
                print(f"Servicios: {device[4]}")
                print(f"Capa: {device[5]}")
                print("\n---------------------------------\n")
        else:
            print("No hay dispositivos registrados.")
    else:
        print("Opción inválida.")
    pause()

def view_campuses():
    clear_screen()
    list_campuses()
    pause()

def add_device():
    clear_screen()
    print("¿Dónde agregar nuevo dispositivo?")
    list_campuses()
    selector = int(input("\nElija una opción: ")) - 1
    c.execute("SELECT * FROM campus")
    campuses = c.fetchall()
    if 0 <= selector < len(campuses):
        campus_id = campuses[selector][0]
        clear_screen()
        device_name = input("Agregue el nombre de su dispositivo: ")
        ip_address = input("Ingrese la dirección IP del dispositivo: ")
        mask = input("Ingrese la máscara de red del dispositivo: ")
        services = input("Ingrese los servicios comprometidos (separados por comas): ")
        layer = input("Ingrese la capa a la que pertenece el dispositivo (Núcleo, Distribución, Acceso): ")
        
        c.execute("INSERT INTO devices (name, ip_address, mask, services, layer, campus_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (device_name, ip_address, mask, services, layer, campus_id))
        conn.commit()
        logging.info(f"Dispositivo {device_name} agregado al campus {campuses[selector][1]}")
        print("Dispositivo agregado correctamente.")
    else:
        print("Opción inválida.")
    pause()

def add_campus():
    clear_screen()
    nuevo_campus = input("Ingrese el nombre del nuevo campus: ")
    if nuevo_campus:
        try:
            c.execute("INSERT INTO campus (name) VALUES (?)", (nuevo_campus,))
            conn.commit()
            logging.info(f"Campus {nuevo_campus} agregado")
            print("Campus agregado correctamente.")
        except sqlite3.IntegrityError:
            print("El nombre del campus ya existe.")
    else:
        print("Nombre de campus inválido.")
    pause()

def delete_device():
    clear_screen()
    print("Borrar dispositivo")
    print("Elija el campus donde desea borrar el dispositivo:")
    list_campuses()
    selector = int(input("Elija una opción: ")) - 1
    c.execute("SELECT * FROM campus")
    campuses = c.fetchall()
    if 0 <= selector < len(campuses):
        campus_id = campuses[selector][0]
        c.execute("SELECT * FROM devices WHERE campus_id=?", (campus_id,))
        devices = c.fetchall()
        clear_screen()
        if devices:
            for idx, device in enumerate(devices, start=1):
                print(f"{idx}. {device[1]}")
            device_selector = int(input("Elija un dispositivo para borrar: ")) - 1
            if 0 <= device_selector < len(devices):
                device_id = devices[device_selector][0]
                c.execute("DELETE FROM devices WHERE id=?", (device_id,))
                conn.commit()
                logging.info(f"Dispositivo {devices[device_selector][1]} borrado")
                print("Dispositivo borrado correctamente.")
            else:
                print("Opción inválida.")
        else:
            print("No se encontraron dispositivos.")
    else:
        print("Opción inválida.")
    pause()

def delete_campus():
    clear_screen()
    print("Borrar campus")
    print("Elija el campus que desea borrar:")
    list_campuses()
    selector = int(input("Elija una opción: ")) - 1
    c.execute("SELECT * FROM campus")
    campuses = c.fetchall()
    if 0 <= selector < len(campuses):
        campus_id = campuses[selector][0]
        c.execute("DELETE FROM campus WHERE id=?", (campus_id,))
        c.execute("DELETE FROM devices WHERE campus_id=?", (campus_id,))
        conn.commit()
        logging.info(f"Campus {campuses[selector][1]} y sus dispositivos borrados")
        print("Campus y sus dispositivos borrados correctamente.")
    else:
        print("Opción inválida.")
    pause()

def generate_pdf_report():
    # Aquí se agregaría la lógica para generar un reporte PDF utilizando `pdfkit` o similar
    clear_screen()
    print("Generar reporte PDF (funcionalidad aún no implementada)")
    pause()

def main():
    if authenticate():
        while True:
            choice = display_menu()
            if choice == "1":
                view_devices()
            elif choice == "2":
                view_campuses()
            elif choice == "3":
                add_device()
            elif choice == "4":
                add_campus()
            elif choice == "5":
                delete_device()
            elif choice == "6":
                delete_campus()
            elif choice == "7":
                generate_pdf_report()
            elif choice == "8":
                sys.exit()
            else:
                print("Opción inválida.")
                pause()

if __name__ == "__main__":
    main()
