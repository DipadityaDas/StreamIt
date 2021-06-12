import socket
import cv2
import pickle
import struct
import threading

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 2222
ip = ""
s.bind((ip, port))
s.listen()


def receive(session, addr):
	data = b""
	payload_size = struct.calcsize(">L")
	while True:
		while len(data) < payload_size:
			data += session.recv(4096)

		packed_msg_size = data[:payload_size]
		data = data[payload_size:]
		msg_size = struct.unpack(">L", packed_msg_size)[0]
		while len(data) < msg_size:
			data += session.recv(4096)

		frame_data = data[:msg_size]
		data = data[msg_size:]
		frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
		frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
		cv2.imshow('ImageWindow', frame)
		if cv2.waitKey(1) == 27:
			break
	cv2.destroyAllWindows()


def send(session, addr):
	connection = session.makefile('wb')
	# cam = cv2.VideoCapture('http://192.168.1.4:8080/video')
	cam = cv2.VideoCapture(0)
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

	while True:
		ret, frame = cam.read()
		frame = cv2.resize(frame, (900, 600))
		result, frame = cv2.imencode('.jpg', frame, encode_param)
		data = pickle.dumps(frame, 0)
		size = len(data)
		session.sendall(struct.pack(">L", size) + data)
	cam.release()


while True:
	session, addr = s.accept()
	t1 = threading.Thread(target=receive, args=(session, addr))
	t2 = threading.Thread(target=send, args=(session, addr))
	t1.start()
	t2.start()
