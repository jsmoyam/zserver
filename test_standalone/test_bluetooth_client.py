
import bluetooth

bd_addr = "B8:27:EB:62:FB:FF"

port = 1

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))

sock.send("test1 4 5")

response = sock.recv(1024).decode("utf-8")
print(response)

sock.close()