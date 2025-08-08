# Generate the OTP password for registration and login use
import secrets


def otp_generator(length=8):
    otp_list = [str(secrets.randbelow(10)) for _ in range(length)]
    otp = ''.join(otp_list)
    return otp


# print(type(secrets.randbelow(10))) <class 'int'>
# print(otp_generator())
