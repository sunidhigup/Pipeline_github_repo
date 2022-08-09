from cryptography.fernet import Fernet


def key_generator():
    """

    :return:
    """
    key = Fernet.generate_key()
    #Openinig Key file
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key


def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    #Loading key
    return open("key.key", "rb").read()
