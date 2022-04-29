import requests
import json
import time

class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.url = "https://server.humm-box.com/api/devices/" + device_id
        self.query_metadata = {'context':'admin'}
        self.query_measures = {'sort[created_at]':'desc','skip':0,'limit':1000}
        self.header = {'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2h1bW0tc2VydmVyLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MjRhYjM3ZDRjZWQ5NjAwNmFjZDAxMDQiLCJhdWQiOiJMTEllQ2F6SFRKUzhvZFVtZGhyRzJlbld3UGlucmo1MSIsImlhdCI6MTY0OTA2Mjg5MCwiZXhwIjoxNjUyNjYyODkwLCJhdF9oYXNoIjoiWDRkWmZ3MnNZeTBoS3ROeEVFYVFKdyIsIm5vbmNlIjoiM3ZTNUVJX3ptbmpLS0lZcHVZaHhyeU1nb0JyWHB1UFUifQ.JF6wyPCyqyvbfnjQ2wS0yGEmuWJ1SjzgikixCJcA5G4",
            'User-Agent': "PostmanRuntime/7.15.2",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "server.humm-box.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"}
        self.metadata = None
        self.sensor_alert = None
        self.logs = None
        self.last_plug = None
        self.first_start = None
        self.last_start = None
        self.count = 0
        self.measures = []
        self.first_measure = ""
        self.last_measure = ""
        self.update()

    def update_metadata(self):
        res = requests.request("GET", self.url, headers=self.header, params=self.query_metadata)
        self.metadata = json.loads(res.content)
        # print(json.dumps(self.metadata, sort_keys=True, indent=4))
        self.sensor_alert = self.metadata['sensors']
        del self.metadata['sensors']
        res = requests.request("GET", self.url + "/logs", headers=self.header, params=self.query_metadata)
        self.logs = json.loads(res.content)
        for x in self.logs:
            x['type'] = 0
            if (len(self.device_id) > 8):
                time_obj = time.strptime(x['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                time_obj = time.strptime(x['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            x['timestamp'] = time.mktime(time_obj) - (time.altzone * 2)
            if x['message'].find("Battery plu") != -1  and self.last_plug == None:
                self.last_plug = x['timestamp']
            elif x['message'].find("Startup Message") != -1:
                self.first_start = x['timestamp']
                if self.last_start == None:
                    self.last_start = x['timestamp']

    def update_measures(self):
        query = self.query_measures
        while 42:
            res = requests.request("GET", self.url + '/measures', headers=self.header, params=query)
            # print(res.status_code)
            res_json = json.loads(res.content)
            res_json_len = len(res_json)
            if res_json_len == 0:
                break
            for x in res_json:
                x['type'] = 1
                if (len(self.device_id) > 8):
                    if(len(x['created_at'])< 21):
                        tmpTime = x['created_at'].replace("Z", ".000000Z")
                    elif(len(x['created_at']) > 25):
                        tmpTime = x['created_at'][0:25] + "Z"
                    else:
                        tmpTime = x['created_at']
                    time_obj = time.strptime(tmpTime, '%Y-%m-%dT%H:%M:%S.%fZ')
                else:
                    time_obj = time.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                x['timestamp'] = time.mktime(time_obj) - (time.altzone * 2)
            self.measures+=res_json
            self.count += res_json_len
            query = {'sort[created_at]':'desc','skip':0,'limit':1000,'selector[created_at][$lt]':res_json[-1]['created_at']}
        self.first_measure = self.measures[-1]['created_at']
        self.last_measure = self.measures[0]['created_at']

    def update(self):
        self.update_measures()
        self.update_metadata()

    def getPeriod_logs(self, from_timestamp):
        return [x for x in self.logs if x['timestamp'] >= from_timestamp]

    def getPeriod_measure(self, from_timestamp):
        return [x for x in self.measures if x['timestamp'] >= from_timestamp]

    def getPeriod_mixed(self, from_timestamp):
        return sorted(self.getPeriod_logs(from_timestamp) + self.getPeriod_measure(from_timestamp), key=lambda item:item['timestamp'], reverse=True)

    def printAll_metadata(self):
        print(json.dumps(self.sensor_alert, sort_keys=True, indent=4))
        print(json.dumps(self.logs, sort_keys=True, indent=4))
        print(json.dumps(self.metadata, sort_keys=True, indent=4))

    def printAll_measure(self):
        print(json.dumps(self.measures, sort_keys=True, indent=4))

# d1 = Device("206C57")
# d1.update()
# timeline = d1.getPeriod_mixed(d1.last_plug)
# print json.dumps(timeline, sort_keys=True, indent=4)
