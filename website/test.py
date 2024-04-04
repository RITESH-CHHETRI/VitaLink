from uuid import uuid4

def otpgenerator():
    otp = str(uuid4())
    return otp[:4]
