from cryptography.fernet import Fernet


def encrypt_val(clear_text, MASTER_KEY):
    """

    :param clear_text:
    :param MASTER_KEY:
    :return:
    """
    #encrypt user defined function
    f = Fernet(MASTER_KEY)
    clear_text_b = bytes(clear_text, 'utf-8')
    cipher_text = f.encrypt(clear_text_b)
    cipher_text = str(cipher_text.decode('ascii'))

    return cipher_text


def decrypt_val(cipher_text, MASTER_KEY):
    """

    :param cipher_text:
    :param MASTER_KEY:
    :return:
    """
    #decrypt user defined function
    f = Fernet(MASTER_KEY)
    clear_val = f.decrypt(cipher_text.encode()).decode()
    return clear_val
