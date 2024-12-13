# Local Area Network (LAN) Device Discovery and Communication Program

## Introduction

This Python program demonstrates how to achieve device discovery and simple bidirectional communication within a Local Area Network (LAN). It combines UDP broadcasting and TCP connections, allowing devices on the same LAN to automatically find each other and establish connections for communication.

## Key Concepts

### 1. UDP Broadcasting (Device Discovery)

#### 1.1 Concept of Broadcasting

*   **Broadcast Address:** Broadcasting is a network communication method that sends a message to all devices on a network. In IPv4, a broadcast address is typically `255.255.255.255` (for a full network broadcast), or something like `192.168.1.255` (for a subnet broadcast, where `192.168.1` is your subnet address).
*   **UDP Protocol:** Broadcasting commonly uses the UDP protocol because UDP is connectionless and suitable for sending broadcast messages. UDP is characterized by its simplicity and efficiency, but it does not guarantee reliable message delivery.
*   **Port:** A port number is required for broadcasting to distinguish between different applications or services.

#### 1.2 How it Works

1.  **Sending a Broadcast:** A device sends a UDP message to the broadcast address within the LAN. This message is sent to all devices on the same LAN.
2.  **Listening to Broadcasts:** Other devices on the LAN also listen on the same broadcast port to receive broadcast messages.
3.  **Parsing Messages:** When a device receives a broadcast message, it parses the message content and determines whether it's a broadcast from the same application.
4.  **Device Discovery:** By parsing the broadcast messages, devices can learn the IP addresses of other devices on the LAN, enabling device discovery.

#### 1.3 Advantages and Limitations of Broadcasting

*   **Advantages:**
    *   Simple and easy to implement.
    *   Does not require a central server; devices can be discovered dynamically.
*   **Limitations:**
    *   Broadcast messages are limited to the same LAN and cannot cross routers.
    *   UDP protocol does not guarantee reliable message delivery, and messages may be lost.
    *   Broadcast messages are sent to all devices on the LAN, which may generate unnecessary network traffic.
    *   May be restricted by firewalls or router settings.

### 2. TCP Connection (Bidirectional Communication)

#### 2.1 Concept of TCP

*   **TCP Protocol:** TCP is a reliable, connection-oriented protocol. It provides guarantees for data transmission, such as in-order delivery and data integrity.
*   **Three-Way Handshake:** Establishing a TCP connection requires a three-way handshake process to synchronize the connection state between the two parties.
*   **Port:** TCP also requires a port number to distinguish between different applications or services.

#### 2.2 How it Works

1.  **Connection Request:** Device A initiates a connection request to Device B via TCP (using Device B's IP address and port).
2.  **Accepting the Connection:** Device B listens on the specified TCP port and accepts Device A's connection request.
3.  **Establishing the Connection:** The two devices complete the three-way handshake and establish a TCP connection.
4.  **Data Transmission:** After the connection is established, Device A and Device B can send and receive data over the TCP connection.

#### 2.3 Advantages and Limitations of TCP

*   **Advantages:**
    *   Reliable data transmission, ensuring data is delivered in order and without loss.
    *   Connection-oriented, making it convenient to manage and maintain communication states.
*   **Limitations:**
    *   Compared to UDP, TCP is more complex and has higher overhead.

### 3. Multithreading

*   **Concurrency:** The program uses multithreading to handle broadcast listening, TCP connection listening, and user input simultaneously.
*   **`threading` Module:** Python's `threading` module provides tools for creating and managing threads.
*   **`start_tcp_server` Thread:**  Dedicated to listening for TCP connections, creating a new thread to handle each connection request.
*   **`client_thread` Thread:** Specifically for processing established connections, ensuring that the main thread can continue to listen and broadcast.

## Code Details

### 1. Broadcasting Section

*   **`BROADCAST_IP` and `BROADCAST_PORT`:** Define the broadcast address and port. `255.255.255.255` is the full network broadcast address. In some networks, you may need to use a subnet broadcast address (e.g., `192.168.1.255`).
*   **Creating a UDP Socket:**
    ```python
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ```
    This creates a socket for sending and receiving UDP messages.
*   **Enabling Broadcasting:**
    ```python
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ```
    This enables the socket to send broadcast messages.
*  **Get Local IP Address:**
    ```python
      def get_local_ip():
        """Get local LAN IP address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # No need to connect to actual address, use this to get local ip
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'  # Use loopback if can't get IP
        finally:
            s.close()
        return local_ip
    ```
    This code is for get local IP.
*   **Binding the Socket:**
    ```python
    sock.bind(("", BROADCAST_PORT))
    ```
    This binds the socket to the specified broadcast port. An empty string `""` indicates binding to all available network interfaces.
*   **Sending the Broadcast:**
    ```python
    message = {"ip": local_ip, "time": time.time()}
    message_json = json.dumps(message).encode('utf-8')
    sock.sendto(message_json, (BROADCAST_IP, BROADCAST_PORT))
    ```
    This converts device information (IP address and timestamp) into a JSON string and sends it to the broadcast address.
*   **Receiving Broadcasts:**
    ```python
       while True:
          try:
              sock.settimeout(1) # Set timeout to avoid blocking.
              data, addr = sock.recvfrom(1024)
              if addr[0] != local_ip: # ignore broadcast from self
                received_message = json.loads(data.decode('utf-8'))
                if addr[0] not in discovered_devices:
                    discovered_devices[addr[0]] = received_message
                    print(f"Discovered Device: {addr[0]}")
                    print("Enter IP to connect or s to send message:")
          except socket.timeout:
             break #timeout
    ```
    This receives broadcast messages, parses the JSON string, and stores the device information in the `discovered_devices` dictionary. It also prints discovery information and prompts for input.

### 2. TCP Connection Section

*   **`TCP_PORT`:** Defines the TCP connection port.
*   **`start_tcp_server` function:**
    *   Creates a TCP socket and binds it to the specified port.
    *   Uses the `listen()` method to start listening for connection requests.
    *   Uses the `accept()` method to accept connection requests.
    *   Creates a new `handle_connection` thread to handle each connection.
*   **`handle_connection` function:**
    *   Receives messages from the client.
    *   Prints the received messages.
    *   Closes the connection.
*   **Connection Logic:**
    ```python
        if connected_socket:
            input_text = input("Enter message to send: ")
            if input_text:
               connected_socket.sendall(input_text.encode('utf-8'))
        else:
            input_text = input("Enter IP to connect or s to send message: ")
            if input_text in discovered_devices:
                try:
                    print(f"Connecting to {input_text}:{TCP_PORT}...")
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((input_text, TCP_PORT))
                    print(f"Connected to {input_text}:{TCP_PORT} successfully")
                    connected_socket = client_socket
                    connected_address = (input_text, TCP_PORT)
                    client_thread = threading.Thread(target=handle_connection, args=(client_socket, (input_text,TCP_PORT)))
                    client_thread.start()
                except Exception as e:
                     print(f"Connection failed: {e}")
    ```
    This code checks if a connection already exists. If connected, it will send user input as message, if not, it will prompt user to input an ip to connect, or 's' to send message.

### 3. Usage of Multithreading

*   **Starting the TCP Server Thread:**
    ```python
    server_thread = threading.Thread(target=start_tcp_server, args=(local_ip,))
    server_thread.daemon = True
    server_thread.start()
    ```
    This creates and starts a new thread to run the `start_tcp_server` function for listening to TCP connections. Setting `daemon = True` makes it a daemon thread, which automatically exits when the main thread exits.
*   **Creating Client Connection Thread:**
    ```python
        client_thread = threading.Thread(target=handle_connection, args=(conn, addr))
        client_thread.start()
    ```
   This creates a new thread for each client connection, preventing a single thread from blocking other connections.

## How to Run

1.  Save the code as `discovery_and_connect.py`.
2.  Run `python discovery_and_connect.py` on both devices A and B within the LAN.
3.  After the program starts, it will print the local IP address and start listening for broadcast messages and TCP connections.
4.  Once Device A and B discover each other, the console will print "Discovered Device xxx.xxx.xxx.xxx".
5.  On Device A's console, input the IP address of Device B and press Enter to initiate a connection.
6.  After a successful connection, both devices can input text messages in their console to send messages.

## Possible Improvements

1.  **Better Error Handling:** Implement better error handling, such as catching connection errors and handling message sending failures.
2.  **User-Friendly Interface:** Use a GUI library (e.g., Tkinter, PyQt) to provide a better user experience.
3.  **Data Format:** Use a custom data format or protobuf for transmitting data to improve efficiency and scalability.
4.  **Stronger Robustness:** Consider adding a heartbeat mechanism to detect if a connection is still active.
5.  **Dynamic Broadcast Address:** Automatically calculate the subnet broadcast address based on the device's IP instead of using the full network broadcast.
6.  **Add Device Name:** Include device name in broadcast messages instead of just IP addresses.
7.  **Better Connection Management:** Implement better management of connection states, including disconnection and reconnection.
8. **More Device Discovery Method:**  Add Bonjour/mDNS for more flexible device discovery.

# Programa de Descubrimiento y Comunicación de Dispositivos en Red de Área Local (LAN)

## Introducción

Este programa en Python demuestra cómo lograr el descubrimiento de dispositivos y la comunicación bidireccional simple dentro de una Red de Área Local (LAN). Combina la transmisión UDP (broadcast) y las conexiones TCP, permitiendo que los dispositivos en la misma LAN se encuentren automáticamente y establezcan conexiones para la comunicación.

## Conceptos Clave

### 1. Transmisión UDP (Descubrimiento de Dispositivos)

#### 1.1 Concepto de Transmisión (Broadcast)

*   **Dirección de Broadcast:** La transmisión es un método de comunicación de red que envía un mensaje a todos los dispositivos en una red. En IPv4, una dirección de broadcast suele ser `255.255.255.255` (para un broadcast de red completo), o algo como `192.168.1.255` (para un broadcast de subred, donde `192.168.1` es la dirección de tu subred).
*   **Protocolo UDP:** La transmisión comúnmente utiliza el protocolo UDP porque UDP no está orientado a conexión y es adecuado para enviar mensajes de broadcast. UDP se caracteriza por su simplicidad y eficiencia, pero no garantiza la entrega confiable de mensajes.
*   **Puerto:** Se requiere un número de puerto para la transmisión para distinguir entre diferentes aplicaciones o servicios.

#### 1.2 Cómo Funciona

1.  **Envío de un Broadcast:** Un dispositivo envía un mensaje UDP a la dirección de broadcast dentro de la LAN. Este mensaje se envía a todos los dispositivos en la misma LAN.
2.  **Escucha de Broadcasts:** Otros dispositivos en la LAN también escuchan en el mismo puerto de broadcast para recibir mensajes de broadcast.
3.  **Análisis de Mensajes:** Cuando un dispositivo recibe un mensaje de broadcast, analiza el contenido del mensaje y determina si es un broadcast de la misma aplicación.
4.  **Descubrimiento de Dispositivos:** Al analizar los mensajes de broadcast, los dispositivos pueden conocer las direcciones IP de otros dispositivos en la LAN, permitiendo el descubrimiento de dispositivos.

#### 1.3 Ventajas y Limitaciones de la Transmisión

*   **Ventajas:**
    *   Simple y fácil de implementar.
    *   No requiere un servidor central; los dispositivos se pueden descubrir dinámicamente.
*   **Limitaciones:**
    *   Los mensajes de broadcast están limitados a la misma LAN y no pueden cruzar routers.
    *   El protocolo UDP no garantiza la entrega confiable de mensajes, y es posible que los mensajes se pierdan.
    *   Los mensajes de broadcast se envían a todos los dispositivos en la LAN, lo que puede generar tráfico de red innecesario.
    *   Puede estar restringido por firewalls o la configuración del router.

### 2. Conexión TCP (Comunicación Bidireccional)

#### 2.1 Concepto de TCP

*   **Protocolo TCP:** TCP es un protocolo confiable y orientado a conexión. Proporciona garantías para la transmisión de datos, como la entrega en orden y la integridad de los datos.
*   **Handshake de Tres Vías:** El establecimiento de una conexión TCP requiere un proceso de handshake de tres vías para sincronizar el estado de la conexión entre las dos partes.
*   **Puerto:** TCP también requiere un número de puerto para distinguir entre diferentes aplicaciones o servicios.

#### 2.2 Cómo Funciona

1.  **Solicitud de Conexión:** El dispositivo A inicia una solicitud de conexión al dispositivo B a través de TCP (utilizando la dirección IP y el puerto del dispositivo B).
2.  **Aceptación de la Conexión:** El dispositivo B escucha en el puerto TCP especificado y acepta la solicitud de conexión del dispositivo A.
3.  **Establecimiento de la Conexión:** Los dos dispositivos completan el handshake de tres vías y establecen una conexión TCP.
4.  **Transmisión de Datos:** Después de que se establece la conexión, el dispositivo A y el dispositivo B pueden enviar y recibir datos a través de la conexión TCP.

#### 2.3 Ventajas y Limitaciones de TCP

*   **Ventajas:**
    *   Transmisión de datos confiable, asegurando que los datos se entreguen en orden y sin pérdidas.
    *   Orientado a conexión, lo que facilita la gestión y el mantenimiento de los estados de comunicación.
*   **Limitaciones:**
    *   En comparación con UDP, TCP es más complejo y tiene una sobrecarga mayor.

### 3. Multihilo (Multithreading)

*   **Concurrencia:** El programa utiliza multihilo para manejar simultáneamente la escucha de broadcasts, la escucha de conexiones TCP y la entrada del usuario.
*   **Módulo `threading`:** El módulo `threading` de Python proporciona herramientas para crear y gestionar hilos.
*   **Hilo `start_tcp_server`:** Dedicado a escuchar conexiones TCP, creando un nuevo hilo para manejar cada solicitud de conexión.
*   **Hilo `client_thread`:** Específicamente para procesar las conexiones establecidas, asegurando que el hilo principal pueda seguir escuchando y transmitiendo.

## Detalles del Código

### 1. Sección de Broadcast

*   **`BROADCAST_IP` y `BROADCAST_PORT`:** Definen la dirección y el puerto de broadcast. `255.255.255.255` es la dirección de broadcast de red completa. En algunas redes, es posible que necesites usar una dirección de broadcast de subred (por ejemplo, `192.168.1.255`).
*   **Creación de un Socket UDP:**
    ```python
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ```
    Esto crea un socket para enviar y recibir mensajes UDP.
*   **Habilitación del Broadcast:**
    ```python
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ```
    Esto habilita el socket para enviar mensajes de broadcast.
*   **Obtener Dirección IP Local:**
    ```python
      def get_local_ip():
        """Obtener la dirección IP local de la LAN"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # No es necesario conectar a una dirección real, usar esto para obtener la IP local
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'  # Usar loopback si no se puede obtener la IP
        finally:
            s.close()
        return local_ip
    ```
    Este código es para obtener la IP local.
*   **Enlace del Socket:**
    ```python
    sock.bind(("", BROADCAST_PORT))
    ```
    Esto vincula el socket al puerto de broadcast especificado. Una cadena vacía `""` indica vincularse a todas las interfaces de red disponibles.
*   **Envío del Broadcast:**
    ```python
    message = {"ip": local_ip, "time": time.time()}
    message_json = json.dumps(message).encode('utf-8')
    sock.sendto(message_json, (BROADCAST_IP, BROADCAST_PORT))
    ```
    Esto convierte la información del dispositivo (dirección IP y marca de tiempo) en una cadena JSON y la envía a la dirección de broadcast.
*   **Recepción de Broadcasts:**
   ```python
       while True:
          try:
              sock.settimeout(1) # Establecer timeout para evitar bloqueo.
              data, addr = sock.recvfrom(1024)
              if addr[0] != local_ip: # Ignorar broadcast propio.
                received_message = json.loads(data.decode('utf-8'))
                if addr[0] not in discovered_devices:
                    discovered_devices[addr[0]] = received_message
                    print(f"Dispositivo Descubierto: {addr[0]}")
                    print("Ingresa IP para conectar o 's' para enviar mensaje:")
          except socket.timeout:
             break # timeout
    ```
     Esto recibe mensajes de broadcast, analiza la cadena JSON y almacena la información del dispositivo en el diccionario `discovered_devices`. También imprime la información de descubrimiento y solicita la entrada.

### 2. Sección de Conexión TCP

*   **`TCP_PORT`:** Define el puerto de conexión TCP.
*   **Función `start_tcp_server`:**
    *   Crea un socket TCP y lo vincula al puerto especificado.
    *   Utiliza el método `listen()` para comenzar a escuchar las solicitudes de conexión.
    *   Utiliza el método `accept()` para aceptar las solicitudes de conexión.
    *   Crea un nuevo hilo `handle_connection` para manejar cada conexión.
*   **Función `handle_connection`:**
    *   Recibe mensajes del cliente.
    *   Imprime los mensajes recibidos.
    *   Cierra la conexión.
*   **Lógica de Conexión:**
     ```python
        if connected_socket:
            input_text = input("Ingresa mensaje para enviar: ")
            if input_text:
               connected_socket.sendall(input_text.encode('utf-8'))
        else:
            input_text = input("Ingresa IP para conectar o 's' para enviar mensaje: ")
            if input_text in discovered_devices:
                try:
                    print(f"Conectando a {input_text}:{TCP_PORT}...")
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((input_text, TCP_PORT))
                    print(f"Conexión a {input_text}:{TCP_PORT} establecida")
                    connected_socket = client_socket
                    connected_address = (input_text, TCP_PORT)
                    client_thread = threading.Thread(target=handle_connection, args=(client_socket, (input_text,TCP_PORT)))
                    client_thread.start()
                except Exception as e:
                     print(f"Conexión fallida: {e}")
    ```
    Este código verifica si ya existe una conexión. Si ya está conectado, enviará la entrada del usuario como un mensaje; de lo contrario, solicitará al usuario que ingrese una IP para conectarse o 's' para enviar un mensaje.

### 3. Uso de Multihilo

*   **Inicio del Hilo del Servidor TCP:**
    ```python
    server_thread = threading.Thread(target=start_tcp_server, args=(local_ip,))
    server_thread.daemon = True
    server_thread.start()
    ```
    Esto crea e inicia un nuevo hilo para ejecutar la función `start_tcp_server` para escuchar las conexiones TCP. Configurar `daemon = True` lo convierte en un hilo demonio, que se cierra automáticamente cuando se cierra el hilo principal.
*  **Creación de un hilo para cada conexión de cliente:**
    ```python
        client_thread = threading.Thread(target=handle_connection, args=(conn, addr))
        client_thread.start()
    ```
    Esto crea un nuevo hilo para cada conexión de cliente, evitando que un solo hilo bloquee otras conexiones.

## Cómo Ejecutar

1.  Guarda el código como `discovery_and_connect.py`.
2.  Ejecuta `python discovery_and_connect.py` en ambos dispositivos A y B dentro de la LAN.
3.  Después de que el programa se inicie, imprimirá la dirección IP local y comenzará a escuchar los mensajes de broadcast y las conexiones TCP.
4.  Una vez que los Dispositivos A y B se descubran mutuamente, la consola imprimirá "Dispositivo Descubierto xxx.xxx.xxx.xxx".
5.  En la consola del Dispositivo A, ingresa la dirección IP del Dispositivo B y presiona Enter para iniciar una solicitud de conexión.
6.  Después de una conexión exitosa, ambos dispositivos pueden ingresar mensajes de texto en sus consolas para enviarlos.

## Posibles Mejoras

1.  **Mejor Manejo de Errores:** Implementar un mejor manejo de errores, como capturar errores de conexión y manejar fallas en el envío de mensajes.
2.  **Interfaz de Usuario Más Amigable:** Usar una biblioteca de interfaz gráfica (por ejemplo, Tkinter, PyQt) para proporcionar una mejor experiencia de usuario.
3.  **Formato de Datos:** Usar un formato de datos personalizado o protobuf para transmitir datos para mejorar la eficiencia y escalabilidad.
4.  **Mayor Robustez:** Considerar agregar un mecanismo de latido (heartbeat) para detectar si una conexión aún está activa.
5.  **Dirección de Broadcast Dinámica:** Calcular automáticamente la dirección de broadcast de la subred en función de la IP del dispositivo en lugar de usar el broadcast de red completo.
6.  **Agregar Nombre de Dispositivo:** Incluir el nombre del dispositivo en los mensajes de broadcast en lugar de solo las direcciones IP.
7.  **Mejor Gestión de Conexiones:** Implementar una mejor gestión de los estados de conexión, incluyendo desconexión y reconexión.
8.  **Método de Descubrimiento de Dispositivos Adicional:** Agregar Bonjour/mDNS para un descubrimiento de dispositivos más flexible.

