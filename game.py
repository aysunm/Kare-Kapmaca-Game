import RPi.GPIO as GPIO
import time
import sys

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

GPIO.setmode(GPIO.BCM)

COL = [6, 13, 19, 26]
ROW = [5, 22, 27, 17]

# hardware SPI config #
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

# Hardware SPI usage #
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

# Initialize library #
disp.begin(contrast=0)

# Clear display #
disp.clear()
disp.display()

# Create image buffer #
# 83x47#
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

draw = ImageDraw.Draw(image)

font = ImageFont.load_default()
big_font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 20)

# setup ports #
for j in range(4):
    GPIO.setup(COL[j], GPIO.OUT)
    GPIO.output(COL[j], 1)

for i in range(4):
    GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# button matrix #
MATRIX = [  [ "1", "2", "3", "K" ],
            [ "4", "5", "6", "G" ],
            [ "7", "8", "9", "D" ],
            [ "0", "0", "0", "B" ] ]


def sayi_al(min, max):
    sayi = int(input())
    if sayi < min or sayi > max:
        print("Hatali giris! Lutfen gecerli bir sayi giriniz.")
        sayi = sayi_al(min, max)
    return sayi


def hamle_al(oyun_alani, satir_sinir, sutun_sinir):
    #hamle_str = input("Hamle giriniz: ")
    #hamle_split = hamle_str.split()
    #while len(hamle_split) != 3 or len(hamle_split[1]) != 1:
    #    hamle_str = input("Hamle giriniz: ")
    #    hamle_split = hamle_str.split()

    hamle_split = ["0", "0", "0"]
    inputs = 0
    while inputs != 3:
        for j in range(4):
            GPIO.output(COL[j], 0)
            for i in range(4):
                # if key is down #
                if GPIO.input(ROW[i]) == 0:
                    print(MATRIX[i][j])
                    hamle_split[inputs] = MATRIX[i][j]
                    inputs = inputs + 1
                    time.sleep(0.5)
            GPIO.output(COL[j], 1)

    satir = int(hamle_split[0])
    sutun = int(hamle_split[1])
    yon = -1
    if hamle_split[2] == "G":
        yon = 0
    elif hamle_split[2] == "D":
        yon = 1
    elif hamle_split[2] == "K":
        yon = 0
        satir = satir - 1
    elif hamle_split[2] == "B":
        yon = 1
        sutun = sutun - 1
    print(satir, sutun, yon)
    while sutun < 1 or satir < 1 or satir > satir_sinir or sutun > sutun_sinir or yon == -1 or oyun_alani[satir][sutun][yon] == 1:
        inputs = 0
        while inputs != 3:
            for j in range(4):
                GPIO.output(COL[j], 0)
                for i in range(4):
                    # if key is down #
                    if GPIO.input(ROW[i]) == 0:
                        print(MATRIX[i][j])
                        hamle_split[inputs] = MATRIX[i][j]
                        inputs = inputs + 1
                        time.sleep(0.5)
                GPIO.output(COL[j], 1)

        satir = int(hamle_split[0])
        sutun = int(hamle_split[1])
        yon = -1
        if hamle_split[2] == "G":
            yon = 0
        elif hamle_split[2] == "D":
            yon = 1
        elif hamle_split[2] == "K":
            yon = 0
            satir = satir - 1
        elif hamle_split[2] == "B":
            yon = 1
            sutun = sutun - 1

    return satir, sutun, yon


def ciz(draw, oyun_alani, satir, sutun, sahiplik, oyuncu1, oyuncu2):
    global disp
    sutun_isimleri = " ABCDEFGHIJKLMNOPRST"
    for i in range(satir + 1):
        for k in range(3):
            if k == 1 and i > 0:
                print(i, end="")
            for j in range(sutun + 1):
                if i == 0 and k == 1:
                    if j == 1:
                        print(sutun_isimleri[j], end="")
                    else:
                        print("\b", sutun_isimleri[j], end="", sep="")

                if k == 2 and oyun_alani[i][j][0] == 1:
                    print("___", end="")
                else:
                    if k == 1 and i > 0 and j == 0:
                        print("  ", end="")
                    else:
                        if k == 1 and i > 0 and j > 0 and sahiplik[i - 1][j - 1] != 0:
                            if sahiplik[i - 1][j - 1] == 1:
                                print(" ", oyuncu1, " ", end="", sep="")
                            else:
                                print(" ", oyuncu2, " ", end="", sep="")
                        else:
                            print("   ", end="")
                if oyun_alani[i][j][1] == 1:
                    print("|", end="")
                else:
                    print(" ", end="")

            print("")
        draw.rectangle((0, 0, 83, 47), outline=255, fill=255)
        #draw.rectangle((0, 0, 83, 47), outline=0, fill=255)
        for j in range(6):
            for i in range(8):
                #if i > 0 and j > 0:
                if oyun_alani[j][i][0] == 1:
                    draw.line(((i - 1) * 11.5 + 3, j * 9.5, (i) * 11.5 - 1, j * 9.5), fill=0)
                if oyun_alani[j][i][1] == 1:
                    draw.line((i * 11.5 + 1, (j - 1) * 9.5, i * 11.5 + 1, (j) * 9.5 - 2), fill=0)
                    if i > 0 and j > 0 and sahiplik[j - 1][i - 1] != 0:
                        if sahiplik[j - 1][i - 1] == 1:
                            draw.text(((i - 1) * 11.5 + 5.75, (j - 1) * 9.5 - 1), oyuncu1, font=font)
                        else:
                            draw.text(((i - 1) * 11.5 + 5.75, (j - 1) * 9.5 - 1), oyuncu2, font=font)

        disp.image(image)
        disp.display()


def oyun(draw):
    draw.rectangle((0, 0, 83, 47), outline=255, fill=255)

    draw.text((15, 5), "KARE", fill=0, font=big_font)
    draw.text((0, 20), "KAPMACA", fill=0, font=big_font)

    disp.image(image)
    disp.display()
    time.sleep(3)

    oyun_satir = 5
    oyun_sutun = 7

    oyun_alani = [[[0, 0] for i in range(oyun_sutun + 1)] for j in
                  range(oyun_satir + 1)]  # oyun gorselinin sayisal ifadesi
    kare_sahip = [[0 for i in range(oyun_sutun)] for j in range(oyun_satir)]  # karelerin kime ait olduğu

    # sinirlari olustur
    for i in range(oyun_satir):
        oyun_alani[i + 1][0][1] = 1
        oyun_alani[i + 1][oyun_sutun][1] = 1

    for j in range(oyun_sutun):
        oyun_alani[0][j + 1][0] = 1
        oyun_alani[oyun_satir][j + 1][0] = 1

    oyuncu1 = "A"
    oyuncu2 = "B"

    print("")
    print("Hamlenizi satir numarasi, sutun harfi ve kenarin(yon) bas harfini girerek oynayiniz. (or: 1 A D)")

    tur = 0
    cizilen_cizgi = 0
    max_cizilebilen_alan = ((oyun_sutun - 1) * 2 + 1) * (oyun_satir - 1) + (oyun_sutun - 1)  # max bos cizgileri hesapla
    while cizilen_cizgi < max_cizilebilen_alan:
        draw.rectangle((0, 0, 83, 47), outline=255, fill=255)
        draw.text((8, 0), "OYUNCU", fill=0, font=big_font)
        if tur % 2 == 0:
            print("------OYUNCU", oyuncu1, "HAMLESİ------")
            draw.text((35, 15), oyuncu1, fill=0, font=big_font)
        else:
            print("------OYUNCU", oyuncu2, "HAMLESİ------")
            draw.text((35, 15), oyuncu2, fill=0, font=big_font)
            
        draw.text((0, 30), "HAMLESI", fill=0, font=big_font)
        disp.image(image)
        disp.display()
        time.sleep(1)
        ciz(draw, oyun_alani, oyun_satir, oyun_sutun, kare_sahip, oyuncu1, oyuncu2)

        kare_olustu = True
        while kare_olustu:
            kare_olustu = False
            satir, sutun, yon = hamle_al(oyun_alani, oyun_satir, oyun_sutun)
            oyun_alani[satir][sutun][yon] = 1

            # kare olustu mu kontrol et
            if yon == 1:
                if sutun < oyun_sutun and oyun_alani[satir - 1][sutun + 1][0] == 1 and oyun_alani[satir][sutun + 1][0] == 1:
                    if oyun_alani[satir][sutun + 1][1] == 1:
                        kare_sahip[satir - 1][sutun] = tur % 2 + 1  # sahiplik ver
                        kare_olustu = True

                if oyun_alani[satir - 1][sutun][0] == 1 and oyun_alani[satir][sutun][0] == 1:
                    if oyun_alani[satir][sutun - 1][1] == 1:
                        kare_sahip[satir - 1][sutun - 1] = tur % 2 + 1  # sahiplik ver
                        kare_olustu = True

            if yon == 0:
                if oyun_alani[satir][sutun][1] == 1 and oyun_alani[satir][sutun - 1][1] == 1:
                    if oyun_alani[satir - 1][sutun][0] == 1:
                        kare_sahip[satir - 1][sutun - 1] = tur % 2 + 1  # sahiplik ver
                        kare_olustu = True

                if satir < oyun_satir and oyun_alani[satir + 1][sutun - 1][1] == 1 and oyun_alani[satir + 1][sutun][
                    1] == 1:
                    if oyun_alani[satir + 1][sutun][0] == 1:
                        kare_sahip[satir][sutun - 1] = tur % 2 + 1  # sahiplik ver
                        kare_olustu = True

            cizilen_cizgi += 1

            ciz(draw, oyun_alani, oyun_satir, oyun_sutun, kare_sahip, oyuncu1, oyuncu2)
            if cizilen_cizgi >= max_cizilebilen_alan:
                break
            time.sleep(1)
        tur += 1

    oyuncu1_skor = 0
    oyuncu2_skor = 0

    for i in range(oyun_satir):
        for j in range(oyun_sutun):
            if kare_sahip[i][j] == 1:
                oyuncu1_skor += 1
            else:
                oyuncu2_skor += 1

    print("Oyuncu ", oyuncu1, "'e ait karelerin sayisi: ", oyuncu1_skor, sep="")
    print("Oyuncu ", oyuncu2, "'e ait karelerin sayisi: ", oyuncu2_skor, sep="")

    while True:
        draw.rectangle((0, 0, 83, 47), outline=255, fill=255)

        if oyuncu1_skor > oyuncu2_skor:
            print(oyuncu1, "KAZANDI")
            draw.text((8, 0), "OYUNCU", fill=0, font=big_font)
            draw.text((35, 15), oyuncu1, fill=0, font=big_font)
            draw.text((0, 30), "KAZANDI", fill=0, font=big_font)
        elif oyuncu2_skor > oyuncu1_skor:
            print(oyuncu2, "KAZANDI")
            draw.text((8, 0), "OYUNCU", fill=0, font=big_font)
            draw.text((35, 15), oyuncu2, fill=0, font=big_font)
            draw.text((0, 30), "KAZANDI", fill=0, font=big_font)
        else:
            print("OYUN BERABERE")
            draw.text((12, 0), "OYUN", fill=0, font=big_font)
            draw.text((4, 15), "BERABERE", fill=0, font=big_font)

        disp.image(image)
        disp.display()
        time.sleep(0.5)
        draw.rectangle((0, 0, 83, 47), outline=255, fill=255)
        disp.image(image)
        disp.display()
        time.sleep(0.5)

devam = "e"
while devam in ["e", "E"]:
    oyun(draw)
    devam = input("Tekrar oynamak ister misiniz? (E/H): ")
