import qrcode

url = "http://10.42.0.1:5000"
img = qrcode.make(url)
img.save("qrcode.png")
print("QR Code created!")
