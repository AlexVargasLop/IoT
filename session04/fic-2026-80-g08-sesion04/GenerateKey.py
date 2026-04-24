from cryptography.fernet import Fernet
import base64
import json
import os



def generate_key():
    key = Fernet.generate_key()
    print("La clave de cifrado es: {}".format(key.decode("utf-8")))
    return key


def store_key(key, filename):
    script = os.path.dirname(os.path.abspath(__file__))
    filename_path = os.path.join(script, filename)
    
    data = {"key": key.decode("utf-8")}

    with open(filename_path, "w") as f:
        json.dump(data, f, indent=4)

    print("Clave guardada correctamente en", filename)


if __name__ == '__main__':
    try:
        key_to_store = generate_key()
        store_key(key_to_store, 'file_key.json')
    except Exception as e:
        print(e)