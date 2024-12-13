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

