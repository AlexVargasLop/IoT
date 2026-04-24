import RPi.GPIO as GPIO
import pn532 as nfc
from pn532.spi import PN532_SPI
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import base64
import string
import json
import os
import random


def load_key(filename):
    script = os.path.dirname(os.path.abspath(__file__))
    filename_path = os.path.join(script, filename)

    with open(filename_path, "r") as f:
        data = json.load(f)
    return data["key"].encode()


def storeData(data: bytes, block):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'

    pn532.mifare_classic_authenticate_block(
        uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    pn532.mifare_classic_write_block(block, data)
    if pn532.mifare_classic_read_block(block) == data:
        print('write block %d successfully' % block)


def cypher_message(message, fileKeyName):
    key = load_key(fileKeyName)
    print("La clave de cifrado es: {}".format(key.decode("utf-8")))

    # using the generated key
    fernet = Fernet(key)
    crypted = fernet.encrypt(message.encode('utf-8'))
    print("Mensaje cifrado: {}".format(crypted))
    return crypted


def generate_cardtime():
    today = datetime.today()
    random_days = random.randint(1, 365)

    validity_date = today + timedelta(days=random_days)
    date_str = validity_date.strftime("%d-%m-%Y")
    new_text = f"Date: {date_str}"
    print("Fecha de validez generada:", new_text)
    return new_text


def generate_cardholder_id():
    numbers = ''.join(random.choice("0123456789") for _ in range(8))
    letter = random.choice(string.ascii_uppercase)
    myText = f"ID:{numbers}{letter}"
    print("ID generado:", myText)
    return myText


def store_data_bytes(data_bytes, current_block, current_sector):
    index = 0
    while index < len(data_bytes):
        # saltar bloques trailer
        if current_block % 4 == 3:
            current_block += 1
            current_sector += 1
            continue

        chunk = data_bytes[index:index+16]
        if len(chunk) < 16:
            chunk = chunk + b'\x00' * (16 - len(chunk))

        storeData(chunk, current_block)
        #print(current_block)

        index += 16
        current_block += 1
    return current_block, current_sector

def wait_for_card(pn532):
    print('Waiting for RFID/NFC card to write to!')
    # Esperamos a tener una tarjeta
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print('.', end="")
        # Try again if no card is available.
        if uid is not None:
            break
    print('Found card with UID:', [hex(i) for i in uid])
    return uid


def initialize_the_reader():
    # Iniciamos el lector/escritor NFC
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()
    uid = wait_for_card(pn532)
    return pn532, uid


if __name__ == '__main__':
    try:
        pn532, uid = initialize_the_reader()

        # Generar una fecha de validez de la tarjeta
        cardtime_text = generate_cardtime()
        cardtime_bytes = cypher_message(cardtime_text, 'file_key.json')
        # Vamos a empezar a guardar en el bloque 8
        current_block = 12
        current_sector = 3
        # Guardamos el bloque 4
        block4_text = 'DT:B-' + str(current_block).zfill(2) + ';Size-' + str(len(cardtime_bytes)).zfill(3)
        block4_text_bytes = block4_text.encode('utf-8')
        print("La información a almacenar en Bloque 4: {}".format(block4_text_bytes))
        storeData(block4_text_bytes, 4)

        # Almacenamos los datos en los bloques correspondientes
        print("La información a almacenar sobre la info del Bloque 4: {}".format(cardtime_bytes))
        current_block, current_sector = store_data_bytes(cardtime_bytes, current_block, current_sector)

        # A partir de este momento, generar aleatoriamente un DNI (número a numero - 8 números - y una letra del alfabeto)
        id_text = generate_cardholder_id()
        id_bytes = cypher_message(id_text, 'file_key.json')
        # Guardamos el bloque 6
        block6_text = 'ID:B-' + str(current_block).zfill(2) + ';Size-' + str(len(id_bytes)).zfill(3)
        block6_text_bytes = block6_text.encode('utf-8')
        print("La información a almacenar en Bloque 6: {}".format(block6_text_bytes))
        storeData(block6_text_bytes, 6)

        # Almacenamos los datos en los bloques correspondientes
        print("La información a almacenar sobre la info del Bloque 6: {}".format(id_bytes))
        current_block, current_sector = store_data_bytes(id_bytes, current_block, current_sector)

    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()