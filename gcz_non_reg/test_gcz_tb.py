import unittest
import time
import numpy
import datetime
import sys
from gcz_tb import Device


class Test_nonReg(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.device = device
        self.now = now
        self.timelife = timelife
        self.timeline = timeline

    def test_01_elapsedTimeAfterPlug(self):
        elapsed = self.timelife
        print(
            "\n\n\tElapsed time = " + str(round(elapsed / ((60*60)*24), 1))
            + " day[s]", end="\n")
        self.assertGreaterEqual(elapsed, ((60*60)*24)*2)

    def test_02_monitoring_count(self):
        # Test monitoring metronomy
        monitoringMsg = [
            x for x in self.timeline
            if x['type'] == 0 and x['message'].find("Monitoring") != -1]
        print("\n\n\tMonitoring count = " + str(len(monitoringMsg)), end="\n")
        if (fw_frozen == "true"):
            self.assertEqual(len(monitoringMsg), 0)
        else:
            self.assertGreaterEqual(len(monitoringMsg), int((self.timelife/(((60*60)*24))*2) - 1))

    def test_03_reset_count(self):
        # Test if device rebootMsg
        rebootMsg = [
            x for x in self.timeline
            if x['type'] == 0 and x['message'].find("reboot") != -1
            and x['message'].find("Sanity") == -1
            and x['timestamp'] != self.device.last_plug]
        print("\n\n\tReset count = " + str(len(rebootMsg)), end="\n")
        self.assertLess(len(rebootMsg), 1)

    def test_04_sanity_reboot(self):
        # Test sanity metronomy
        SanityMsg = [
            x for x in self.timeline
            if x['type'] == 0 and x['message'].find("Sanity") != - 1]
        print("\n\n\tSanity reboot count = " + str(len(SanityMsg)), end="\n")
        self.assertGreaterEqual(
            len(SanityMsg), int((self.timelife/((60*60)*24))/2))

    def test_05_report_freq(self):
        # Test report metronomy
        reportMsg = [x for x in self.timeline if x['type'] == 1]
        print("\n\n\tRepport message count = " + str(len(reportMsg)), end="\n")
        self.assertGreaterEqual(
            len(reportMsg), int((self.timelife/((60*60)*24))*144) - 10)

    def test_06_firmware_version(self):
        # Test firmwareVersion
        print(
            "\n\n\tFirmware version = "
            + self.device.metadata['firmwareVersion'], end="\n")
        self.assertTrue(self.device.metadata['firmwareVersion'] == fw_version)

    def test_56_TEMP_HUM_PIR_LIGHT_CO2(self):
        co2 = []
        pir = []
        for x in self.timeline:
            if x['type'] == 1:
                co2.append(x['co2_air'])
                pir.append(x['pir_mouvement_counter'])
        self.assertGreater(numpy.std(co2), 1)
        self.assertGreater(numpy.std(pir), 1)
        self.assertLessEqual(numpy.min(co2), 490)

    def test_56_TEMP_HUM_LIGHT_CO2(self):
        co2 = []
        light = []
        for x in self.timeline:
            if x['type'] == 1:
                co2.append(x['co2_air'])
                light.append(x['light'])
        self.assertGreater(numpy.std(co2), 1)
        self.assertGreater(numpy.std(light), 1)
        self.assertLessEqual(numpy.min(co2), 490)

    def test_41_EXT_TEMP_HUM_RAINGAUGE(self):
        temp = []
        pluvio = []
        for x in self.timeline:
            if x['type'] == 1:
                temp.append(x['deci_temperature_air_hdc1000'])
                pluvio.append(x['deci_pluvio'])
        self.assertGreater(numpy.std(temp), 1)
        self.assertGreater(numpy.std(pluvio), 1)
        self.assertGreaterEqual(numpy.min(temp), 150)
        self.assertLessEqual(numpy.min(temp), 350)

    def test_16_MAXBOTIX_RS232(self):
        dist = []
        derive = 2
        for x in self.timeline:
            if x['type'] == 1:
                dist.append(x['distance_maxbotix'])
        self.assertLessEqual(numpy.std(dist), derive)
        self.assertGreaterEqual(numpy.min(dist), 66 - derive)
        self.assertLessEqual(numpy.min(dist), 66 + derive)

    def test_99_US_4_BLIND_ZONES(self):
        dist = []
        derive = 2
        for x in self.timeline:
            if x['type'] == 1:
                dist.append(x['distance_bz25'])
        std_dev = numpy.std(dist)
        range = numpy.max(dist) - numpy.min(dist)
        ave = numpy.average(dist)
        print("\n\n\tStd deviation = " + str(std_dev), end=" ")
        print("\n\tDistance (max - min) = " + str(range), end=" ")
        print("\n\tDistance = " + str(ave), end="\n")
        self.assertLessEqual(std_dev, derive)
        self.assertLessEqual(range, 10)

    def test_75_ECU_HR_MAX_MED(self):
        dist = []
        derive = 1.5
        for x in self.timeline:
            if x['type'] == 1:
                dist.append(x['distance_max'])
        std_dev = numpy.std(dist)
        range = numpy.max(dist) - numpy.min(dist)
        print("\n\n\tStd deviation = " + str(std_dev), end=" ")
        print("\n\tDistance (max - min) = " + str(range), end="\n")
        self.assertLessEqual(std_dev, derive)
        self.assertLessEqual(range, 10)


test_cases = [
    "test_01_elapsedTimeAfterPlug",
    "test_02_monitoring_count",
    "test_03_reset_count",
    "test_04_sanity_reboot",
    "test_05_report_freq",
    "test_06_firmware_version"]


def suite():
    suite = unittest.TestSuite()
    for test_class in test_cases:
        suite.addTest(Test_nonReg(test_class))
    suite.addTest(Test_nonReg('test_'+device.metadata['type']))
    return suite


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Please give parameter : python test_gcz_tb.py DEVICE_ID FW_VERSION FROZEN(true/false) [LEN]")
    else:
        device_id = sys.argv[1]
        fw_version = sys.argv[2]
        fw_frozen = sys.argv[3]
        device = Device(device_id)
        now = time.time() - (time.altzone)
        if (len(sys.argv) == 4):
            timelife = (now - device.last_plug)
            timeline = device.getPeriod_mixed(device.last_plug)
        else:
            numberOfDays = int(sys.argv[4])
            timelife = ((60*60)*24)*numberOfDays
            timeline = device.getPeriod_mixed(
                now - (((60*60)*24)*numberOfDays))
        print("\n\n\t" + str(datetime.datetime.now().strftime("%A %d. %B %Y"))  + "\n\n" + "Device :\t" + sys.argv[1] + "\nProvider :\t" + device.metadata["network_provider"] + "\nSensor_set :\t" + device.metadata['type'] + "\nFrozen :\t" + fw_frozen)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite())
