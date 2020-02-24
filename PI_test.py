import os
import serial
import time
import libs.MAPS_mcu as mcu
import libs.MAPS_pi as pi
from datetime import datetime

import requests

#import current file's config, by getting the script name with '.py' replace by '_confg'
#ex: import "maps_V6_general.py" > "maps_V6_general_config" as Conf
PATH_OF_CONFIG = str(os.path.basename(__file__)[:-3] + "_config")
Conf = __import__(PATH_OF_CONFIG)

#temperary value
do_condition = 1
loop = 0
#

try:
    print("START")
    print("========================")

    print("open port & init mcu")
    #mcu.ser=serial.Serial("COM57",115200,timeout=1)
    mcu.ser=serial.Serial("/dev/ttyS0",115200,timeout=1) #for PI (not ttyAMA0)(use /dev/ttyS0)
    time.sleep(5)
    print("mcu ok\n")
    print("------------------------")

    print("CHECK")
    print("========================")
    print("CHECK INTERNET")

    print("------------------------")
    print("CHECK TIME")
    #TODO
    current_mcu_time = mcu.GET_RTC_DATE_TIME()
    print(current_mcu_time)
    #get PI time
    #and sync time


    print("------------------------")
    print("CHECK PI VERSION")
    #TODO

    print("CHECK MCU VERSION")

    current_mcu_version = mcu.GET_INFO_VERSION()
    print(current_mcu_version)
    if (current_mcu_version < Conf.latest_mcu_version):
        #need update
        print("please update mcu")
    else:
        print("newest version")

    print("------------------------")
    print("SET SENSOR")

    mcu.SET_POLLING_SENSOR(Conf.POLL_TEMP,Conf.POLL_CO2,Conf.POLL_TVOC,Conf.POLL_LIGHT,Conf.POLL_PMS,Conf.POLL_RTC)

    print("CHECK SENSOR")
    print(mcu.GET_INFO_SENSOR_POR())


    print("------------------------")
    print("CHECK STORAGE")
    path = pi.GET_STORAGE_PATH()
    print(path)

    print("CHECK read/write")
    #TODO

    print("------------------------")
    print("set upload")
    #if need to do

    print("------------------------")


    #close the fan
    mcu.SET_PIN_FAN_ALL(0)

    while (do_condition):
        print("START GET DATA (loop:" + str(loop) + ")")
        print("========================")

        print("GET ALL DATA")
        data_list = mcu.GET_SENSOR_ALL()

        TEMP        = data_list[0]
        HUM         = data_list[1]
        CO2         = data_list[2]
        TVOC        = data_list[4]
        Illuminance = data_list[10]
        PM1_AE      = data_list[16]
        PM25_AE     = data_list[17]
        PM10_AE     = data_list[18]

        print("TEMP:" +str(TEMP))
        print("HUM:" +str(HUM))
        print("CO2:" +str(CO2))
        print("TVOC:" +str(TVOC))
        print("Illuminance:" +str(Illuminance))
        print("PM1_AE:" +str(PM1_AE))
        print("PM25_AE:" +str(PM25_AE))
        print("PM10_AE:" +str(PM10_AE))
        print("------------------------")
        print("storage data")
        #format to ['device_id', 'date', 'time', 'Tmp',  'RH',   'PM2.5','PM10', 'PM1.0','Lux',  'CO2',  'TVOC']
        pairs = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S").split(" ")
        format_data_list = [Conf.DEVICE_ID,pairs[0],pairs[1],TEMP,HUM,PM25_AE,PM1_AE,PM10_AE,Illuminance,CO2,TVOC]
        pi.save_data(path,format_data_list)

        print("------------------------")
        print("upload data")
        #url = Conf.Restful_URL +
        msg = "|gps_lat=25.1933|s_t0=" + str(TEMP) + "|app=MAPS6|date=" + pairs[0] + "|s_d2=" + str(PM1_AE) + "|s_d0=" + str(PM25_AE) + "|s_d1=" + str(PM10_AE) + "|s_h0=" + str(HUM) + "|device_id=" + Conf.DEVICE_ID +"|s_g8=" + str(CO2) + "|gps_lon=121.787|ver_app=0.0.1|time=" + pairs[1]
        print(msg)
        restful_str = Conf.Restful_URL + "topic=" + Conf.APP_ID + "&device_id=" + Conf.DEVICE_ID + "&key=" + Conf.SecureKey + "&msg=" + msg
        r = requests.get(restful_str)
        print("------------------------")

        loop = loop + 1
        time.sleep(60)
        print("========================")

except KeyboardInterrupt:
    mcu.ser.close()
    pass


##mcu.SET_PIN_FAN_ALL(0)
##time.sleep(3)
##
##mcu.SET_PIN_FAN_ALL(1)
##time.sleep(3)
##
##mcu.SET_PIN_FAN_ALL(0)
##time.sleep(3)

mcu.ser.close()

print("exit OK")
