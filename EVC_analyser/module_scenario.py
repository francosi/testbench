import json
from datetime import datetime


def get_scenario(filename):
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
            json_file.close()
    except(FileNotFoundError, json.decoder.JSONDecodeError):
        return None
    return data


def check_scenario_duration_keys(duration):
    if len(duration) != 4:
        return False
    return True


def check_scenario_ev_keys(ev):
    if len(ev) != 4:
        return False
    return True


def check_scenario_days_keys(days):
    if all(conf_k not in days for conf_k in(
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday')):
        print('bad')
        return False
    return True


def check_scenario_member_keys(member):
    if all(member_k not in member for member_k in (
            'test_name', 'device_model', 'actuation_config')):
        return False
    return True


def check_scenario_actuation_config_keys(act_config):
    if all(config_k not in act_config for config_k in(
            'provisioning_at', 'get_data_at', 'config')):
        return False
    return True


def check_scenario_config_keys(config):
    if all(conf_k not in config for conf_k in(
            'actuation1',
            'actuation2',
            'mode',
            'serial',
            'disengage',
            'duration',
            'ev',
            'days')):
        return False
    return True


def check_scenario_keys(scenario):
    for key in scenario:
        if 'member' not in scenario[key]:
            return False
        if not check_scenario_member_keys(scenario[key]['member']):
            return False
        if not check_scenario_actuation_config_keys(
                scenario[key]['member']['actuation_config']):
            return False
        if not check_scenario_config_keys(
                scenario[key]['member']['actuation_config']['config']):
            return False
        if not check_scenario_duration_keys(
                scenario[key]['member']['actuation_config']['config']['duration']):
            return False
        if not check_scenario_ev_keys(
                scenario[key]['member']['actuation_config']['config']['ev']):
            return False
        if not check_scenario_days_keys(
                scenario[key]['member']['actuation_config']['config']['days']):
            return False
    return True


def update_scenario_time_event(scenario, starting_point):
    now = datetime.timestamp(datetime.now())
    # print('now :' + str(now), flush=True)
    for key in scenario:
        provision_sec = scenario[key]['member']['actuation_config']['provisioning_at']
        tmp = provision_sec.split(':')
        scenario[key]['member']['actuation_config']['provisioning_at'] = (float(tmp[0]) * (60 * 60)) + (float(tmp[1]) * 60) + starting_point
        # print('provisioning_at ' + str(scenario[key]['member']['actuation_config']['provisioning_at']), flush=True)
        if (scenario[key]['member']['actuation_config']['provisioning_at'] < now):
            return None
        get_data_sec = scenario[key]['member']['actuation_config']['get_data_at']
        tmp = get_data_sec.split(':')
        scenario[key]['member']['actuation_config']['get_data_at'] = (float(tmp[0]) * (60 * 60)) + (float(tmp[1]) * 60) + starting_point
        # print('get_data_at ' + str(scenario[key]['member']['actuation_config']['get_data_at']), flush=True)
        if (scenario[key]['member']['actuation_config']['get_data_at'] < now):
            return None
        actuation1_sec = scenario[key]['member']['actuation_config']['config']['actuation1']
        tmp = actuation1_sec.split(':')
        scenario[key]['member']['actuation_config']['config']['actuation1'] = (float(tmp[0]) * (60 * 60)) + (float(tmp[1]) * 60) + starting_point
        # print('actuation 1 ' + str(scenario[key]['member']['actuation_config']['config']['actuation1']), flush=True)
        if (scenario[key]['member']['actuation_config']['config']['actuation1'] < now):
            return None
        actuation2_sec = scenario[key]['member']['actuation_config']['config']['actuation2']
        tmp = actuation2_sec.split(':')
        scenario[key]['member']['actuation_config']['config']['actuation2'] = (float(tmp[0]) * (60 * 60)) + (float(tmp[1]) * 60) + starting_point
        # print('actuation 2 ' + str(scenario[key]['member']['actuation_config']['config']['actuation2']), flush=True)
        if(scenario[key]['member']['actuation_config']['config']['actuation2'] < now or scenario[key]['member']['actuation_config']['config']['actuation2'] < scenario[key]['member']['actuation_config']['config']['actuation1']):
            return None
    return scenario


def update_config(scenario, config):
    if(scenario['member']['actuation_config']['config']['mode'] == 'agenda'):
        config['actuatorConfig']['mode'] = "agenda"
        config['actuatorConfig']['agenda']['duration'] = str(scenario['member']['actuation_config']['config']['duration'][0])
        new_days = []
        for key in scenario['member']['actuation_config']['config']['days']:
            if scenario['member']['actuation_config']['config']['days'][key] == 'true':
                new_days.append(key)
        config['actuatorConfig']['agenda']['days'] = new_days
        if (scenario['member']['actuation_config']['config']['ev'][0] == 'true'):
            config['meta_data_ev_1'] = True
        else:
            config['meta_data_ev_1'] = False
        if (scenario['member']['actuation_config']['config']['ev'][1] == 'true'):
            config['meta_data_ev_2'] = True
        else:
            config['meta_data_ev_2'] = False
        if (scenario['member']['actuation_config']['config']['ev'][2] == 'true'):
            config['meta_data_ev_3'] = True
        else:
            config['meta_data_ev_3'] = False
        if (scenario['member']['actuation_config']['config']['ev'][3] == 'true'):
            config['meta_data_ev_4'] = True
        else:
            config['meta_data_ev_4'] = False
        dt_actuation1 = datetime.fromtimestamp(scenario['member']['actuation_config']['config']['actuation1'])
        dt_actuation2 = datetime.fromtimestamp(scenario['member']['actuation_config']['config']['actuation2'])
        del config['actuatorConfig']['agenda']['startTimes'][:]
        config['actuatorConfig']['agenda']['startTimes'].append(str(dt_actuation1.hour) + ':' + str(dt_actuation1.minute))
        # if (len(config['actuatorConfig']['agenda']['startTimes'][0]) != 2):
        config['actuatorConfig']['agenda']['startTimes'].append(str(dt_actuation2.hour) + ':' + str(dt_actuation2.minute))
        # else:
        # config['actuatorConfig']['agenda']['startTimes'][1] = str(dt_actuation2.hour) + ':' + str(dt_actuation2.minute)
        # print(dt_actuation1, flush=True)
        # print(dt_actuation2, flush=True)
        if (scenario['member']['actuation_config']['config']['serial'] == 'true'):
            config['actuatorConfig']['serialActuation'] = True
        else:
            if('serialActuation' in config['actuatorConfig']):
                del config['actuatorConfig']['serialActuation']
        if 'pauseInfo' in config['actuatorConfig']:
            del config['actuatorConfig']['pauseInfo']
        if scenario['member']['actuation_config']['config']['disengage'] == "true":
            config['actuatorConfig']['pauseInfo'] = {"activated": True}
        else :
            config['actuatorConfig']['pauseInfo'] = {"activated": False}
        return config
