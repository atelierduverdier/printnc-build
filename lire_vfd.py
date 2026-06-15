#!/usr/bin/env python3
# =========================================================================
# lire_vfd.py - Atelier du Verdier
#
# Lit les parametres du VFD HuangYang (Huanyang) via le protocole HYComm
# sur liaison RS485, et les sauvegarde dans vfd_parametres.txt
#
# IMPORTANT : le HuangYang n'utilise PAS le Modbus standard mais son
# propre protocole "HYComm". La trame de lecture d'un parametre est :
#   [adresse][0x01][0x03][numero_PD][0x00][0x00][CRC16]
# La reponse est :
#   [adresse][0x01][0x03][numero_PD][val_hi][val_lo][CRC16]
#
# PREREQUIS :
#   pip3 install pyserial --break-system-packages
#
# UTILISATION (sur le Raspberry Pi, LinuxCNC ARRETE) :
#   python3 lire_vfd.py
# =========================================================================

import serial
import time
import sys

# --- A adapter selon ton installation ---
PORT        = '/dev/ttyAMA2'   # Pi 5 = ttyAMA2, Pi 4 = ttyAMA3
BAUD        = 9600
ADRESSE     = 0x01
FICHIER_OUT = 'vfd_parametres.txt'
# ----------------------------------------

# Pour les parametres connus : (description, diviseur, unite)
# Correspondances officielles HuangYang (serie HY), croisees avec man hy_vfd.
INFOS = {
    0:   ("PD000 reserve",                           1, ""),
    1:   ("Frequence min",                         100, "Hz"),
    2:   ("Source frequence (0=clavier 1=ext 2=RS485)", 1, ""),
    3:   ("Source run (0=clavier 1=ext 2=RS485)",    1, ""),
    4:   ("Frequence de base",                     100, "Hz"),
    5:   ("Frequence max",                         100, "Hz"),
    6:   ("Frequence intermediaire",               100, "Hz"),
    7:   ("Frequence min (torque boost)",          100, "Hz"),
    8:   ("Tension max",                            10, "V"),
    9:   ("Tension intermediaire",                  10, "V"),
    10:  ("Tension min",                            10, "V"),
    11:  ("Frequence min de fonctionnement",       100, "Hz"),
    14:  ("Temps acceleration",                     10, "s"),
    15:  ("Temps deceleration",                     10, "s"),
    16:  ("Sens rotation autorise (0=avant+arr)",    1, ""),
    70:  ("Source signal vitesse",                   1, ""),
    72:  ("Frequence porteuse PWM",                100, "kHz"),
    141: ("Tension nominale moteur",                10, "V"),
    142: ("Courant nominal moteur",                 10, "A"),
    143: ("Nombre de poles moteur",                  1, ""),
    144: ("Vitesse nominale a 50Hz",                 1, "tr/min"),
    163: ("Adresse communication",                   1, ""),
    164: ("Baud rate (0=1200..4=19200)",             1, ""),
    165: ("Format donnees (3=8N1 RTU)",              1, ""),
}


def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc.to_bytes(2, 'little')


def lire_pd(ser, pd):
    """Lit un parametre PD via HYComm. Retourne la valeur brute ou None.

    Format de reponse HYComm :
      [addr][0x01][len][PD_echo][valeur...][CRC16]
    ou 'len' = nombre d'octets entre len et le CRC (PD_echo + valeur) :
      len=0x03 -> 1 octet PD_echo + 2 octets valeur
      len=0x02 -> 1 octet PD_echo + 1 octet valeur
    On valide la reponse en verifiant que PD_echo == pd demande.
    """
    corps = bytes([ADRESSE, 0x01, 0x03, pd & 0xFF, 0x00, 0x00])
    trame = corps + crc16(corps)
    ser.reset_input_buffer()
    ser.write(trame)
    ser.flush()
    time.sleep(0.12)
    rep = ser.read(16)
    if not rep or len(rep) < 6:
        return None
    if crc16(rep[:-2]) != rep[-2:]:
        return None
    longueur = rep[2]
    pd_echo = rep[3]
    # Le numero de PD renvoye doit correspondre a la demande
    if pd_echo != (pd & 0xFF):
        return None
    if longueur == 0x03:
        # PD_echo + 2 octets de valeur
        return int.from_bytes(rep[4:6], 'big')
    elif longueur == 0x02:
        # PD_echo + 1 octet de valeur
        return rep[4]
    return None


def main():
    print("=" * 64)
    print("Lecture des parametres VFD HuangYang via HYComm (RS485)")
    print(f"Port: {PORT}  Adresse: {ADRESSE}  Baud: {BAUD}")
    print("=" * 64)
    print("LinuxCNC doit etre ARRETE (sinon le port est occupe).")
    print()

    try:
        ser = serial.Serial(PORT, BAUD, bytesize=8, parity='N',
                            stopbits=1, timeout=1)
    except Exception as e:
        print(f"Erreur ouverture du port {PORT} : {e}")
        sys.exit(1)

    resultats = {}
    print(f"{'Param':7} {'Brut':8} {'Valeur':16} Description")
    print("-" * 64)

    for pd in range(0, 190):
        val = lire_pd(ser, pd)
        if val is None:
            continue
        resultats[pd] = val
        if pd in INFOS:
            desc, div, unite = INFOS[pd]
            affiche = (f"{val/div:g} {unite}".strip() if div != 1
                      else f"{val} {unite}".strip())
            print(f"PD{pd:03d}   {val:<8} {affiche:<16} {desc}")
        elif val != 0:
            print(f"PD{pd:03d}   {val:<8} {'':<16} (non documente)")
        time.sleep(0.05)

    ser.close()
    print("-" * 64)
    print(f"{len(resultats)} parametres lus")

    with open(FICHIER_OUT, 'w', encoding='utf-8') as f:
        f.write("Parametres VFD HuangYang - Atelier du Verdier\n")
        f.write("Lus via HYComm sur RS485\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"{'Param':7} {'Brut':8} {'Valeur':16} Description\n")
        f.write("-" * 64 + "\n")
        for pd, val in resultats.items():
            if pd in INFOS:
                desc, div, unite = INFOS[pd]
                affiche = (f"{val/div:g} {unite}".strip() if div != 1
                          else f"{val} {unite}".strip())
                f.write(f"PD{pd:03d}   {val:<8} {affiche:<16} {desc}\n")
            elif val != 0:
                f.write(f"PD{pd:03d}   {val:<8} {'':<16} (non documente)\n")

    print(f"\nResultats sauvegardes dans : {FICHIER_OUT}")
    print("Envoie ce fichier pour l'integrer dans la documentation !")


if __name__ == '__main__':
    main()
