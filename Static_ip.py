import netifaces
import subprocess
import os

# Ruta al archivo donde se guardará la última dirección IP asignada
LAST_IP_FILE = "/tmp/last_assigned_ip.txt"

def get_network_info(interface):
    # Obtiene la dirección IP y la máscara de subred de la interfaz especificada
    iface_info = netifaces.ifaddresses(interface)
    ip_address = iface_info[netifaces.AF_INET][0]['addr']
    netmask = iface_info[netifaces.AF_INET][0]['netmask']
    gateway = netifaces.gateways()[netifaces.AF_INET][0][0]
    return ip_address, netmask, gateway

def is_ip_configured(ip_address, interface):
    # Verifica si la dirección IP ya está configurada en la interfaz
    command = f"ip addr show {interface} | grep {ip_address}"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def is_route_configured(gateway):
    # Verifica si la ruta predeterminada ya está configurada
    command = f"ip route show default | grep via {gateway}"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def assign_static_ip(ip_address, netmask, gateway, interface):
    # Verifica si la dirección IP ya está configurada en la interfaz
    if is_ip_configured(ip_address, interface):
        print(f"La dirección IP {ip_address} ya está configurada en la interfaz {interface}.")
        return
    
    # Configura la IP estática en la interfaz
    command = f"sudo ip addr add {ip_address}/{netmask} dev {interface}"
    subprocess.run(command, shell=True)

    # Verifica si la ruta predeterminada ya está configurada
    if is_route_configured(gateway):
        print(f"La ruta predeterminada a {gateway} ya está configurada.")
        return
    
    # Configura la ruta predeterminada
    command = f"sudo ip route add default via {gateway}"
    subprocess.run(command, shell=True)

def save_last_assigned_ip(ip_address):
    # Guarda la última dirección IP asignada en un archivo
    with open(LAST_IP_FILE, "w") as f:
        f.write(ip_address)

def load_last_assigned_ip():
    # Carga la última dirección IP asignada desde el archivo
    if os.path.exists(LAST_IP_FILE):
        with open(LAST_IP_FILE, "r") as f:
            return f.read().strip()
    return None

if __name__ == "__main__":
    # Interfaz de red a utilizar
    interface = "eth0"  # Puedes cambiarlo según tu configuración

    # Obtener la dirección IP asignada por DHCP o cargar la última asignada
    ip_address, netmask, gateway = get_network_info(interface)
    if not ip_address:
        print("No se pudo obtener la dirección IP de la interfaz, usando la última asignada.")
        ip_address = load_last_assigned_ip()

    # Imprimir la dirección IP obtenida o cargada
    print(f"IP asignada por DHCP: {ip_address}")

    if ip_address:
        # Asignar la IP obtenida o cargada como IP estática en la interfaz
        assign_static_ip(ip_address, netmask, gateway, interface)

        # Guardar la dirección IP asignada para su uso posterior
        save_last_assigned_ip(ip_address)
    else:
        print("No se pudo obtener la dirección IP de la interfaz ni cargar la última asignada.")
