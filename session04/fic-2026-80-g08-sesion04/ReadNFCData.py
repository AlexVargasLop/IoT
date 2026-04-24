import RPi.GPIO as GPIO
import pn532 as nfc
from pn532.spi import PN532_SPI
from cryptography.fernet import Fernet
import base64
from datetime import datetime, timedelta
import json



def readData(pn532_device, uid, block):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    if pn532_device.mifare_classic_authenticate_block(
        uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a):
        data = pn532_device.mifare_classic_read_block(block)
        return data
    else:
        print(f"Authentication failed for block {block}")
        return None


def decypher_message_from_card(message_bytes, fileKeyName):
    # Cargar la clave
    with open(fileKeyName, 'r') as f:
        data = json.load(f)
    key = data["key"].encode()  # str → bytes, listo para Fernet
    fernet = Fernet(key)
    decrypted = fernet.decrypt(bytes(message_bytes))
    return decrypted.decode('utf-8')


def getInfoIndex(pn532_device, uid, block_to_read):
    """
    Lee el bloque índice (4 o 6) que contiene:
    'DT:B-08;Size-057' o 'ID:B-10;Size-036'
    Devuelve el bloque de inicio y el número de bytes a leer
    """
    block_data = readData(pn532_device, uid, block_to_read)
    if block_data is None:
        return None, None

    text = block_data.decode('utf-8').strip('\x00')
    # Ejemplo: 'DT:B-08;Size-057'
    try:
        start_block = int(text.split('B-')[1].split(';')[0])
        bytes_to_read = int(text.split('Size-')[1])
        return start_block, bytes_to_read
    except Exception as e:
        print(f"Error parsing index block {block_to_read}: {e}")
        return None, None


def calculate_blocks_to_read(bytesNumber):
    return (bytesNumber + 15) // 16  # redondeo hacia arriba


def getInfoFromCard(pn532_device, uid, start_block, bytes_to_read):
    """
    Lee todos los bloques necesarios para reconstruir los bytes
    """
    read_bytes = bytearray()
    current_block = start_block
    blocks_to_read = calculate_blocks_to_read(bytes_to_read)

    blocks_read = 0
    while blocks_read < blocks_to_read:
        if current_block % 4 == 3:
            current_block += 1
            continue  # no contar esta iteración
        data = readData(pn532_device, uid, current_block)
        if data is None:
            raise Exception(f"No se pudo leer el bloque {current_block}")
        read_bytes.extend(data)
        current_block += 1
        blocks_read += 1

    # Cortar los bytes sobrantes (relleno con 0)
    return read_bytes[:bytes_to_read]


def get_reader_uid():
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    pn532.SAM_configuration()
    return pn532


def read_info_from_card(pn532_device, uid):
    try:
        # Leer bloque índice de fecha (bloque 4)
        start_block_date, bytes_date = getInfoIndex(pn532_device, uid, 4)
        card_date_bytes = getInfoFromCard(pn532_device, uid, start_block_date, bytes_date)
        card_date = decypher_message_from_card(card_date_bytes, 'file_key.json')

        # Leer bloque índice de ID (bloque 6)
        start_block_id, bytes_id = getInfoIndex(pn532_device, uid, 6)
        card_id_bytes = getInfoFromCard(pn532_device, uid, start_block_id, bytes_id)
        card_id = decypher_message_from_card(card_id_bytes, 'file_key.json')

    except Exception as e:
        print(f"Error leyendo tarjeta: {e}")
        card_date = 'Error'
        card_id = 'Error'

    return card_date, card_id


def read_tachograph_info_from_card(pn532_device):
    print('Waiting for RFID/NFC card to read from!')
    target_time = datetime.now() + timedelta(seconds=10)
    while True:
        uid = pn532_device.read_passive_target(timeout=0.5)
        print('.', end="")
        if uid is not None:
            print('\nFound card with UID:', [hex(i) for i in uid])
            return read_info_from_card(pn532_device, uid)
        elif datetime.now() > target_time:
            print('\nTimeout: no se detectó tarjeta')
            return 'Error', 'Error'


if __name__ == '__main__':
    try:
        pn532 = get_reader_uid()
        card_date, card_id = read_tachograph_info_from_card(pn532)
        print(f"\nFecha de validez de la tarjeta: {card_date}")
        print(f"ID del titular: {card_id}")
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()