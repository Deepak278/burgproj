import qrcode
from flask import url_for
from app import app

# Generate QR code that points to student selection page
with app.app_context():
    student_url = url_for('student', _external=True)
    print(f"Generating QR code for: {student_url}")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(student_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("static/qr_code.png")

    print("QR code generated successfully at static/qr_code.png")