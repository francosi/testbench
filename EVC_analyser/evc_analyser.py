import sys
from datetime import datetime
import time
from module_request import (get_log, get_start, get_config, change_config, get_bearer, get_measure)
from module_scenario import (update_config, get_scenario, check_scenario_keys, update_scenario_time_event)
from module_analyse import (analyse_frequency, analyse_actuation)


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd, flush=True)
    # Print New Line on Complete
    if iteration == total:
        print(flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage : python avc_analyser.py DEVICE_ID SCENARIO")
        exit(2)
    device = sys.argv[1]
    scenario_file = sys.argv[2]

    scenario = get_scenario(scenario_file)
    if scenario is None or check_scenario_keys(scenario) is False:
        print('Something goes wrong with scenario file')
        exit(2)

    bearer = get_bearer('bearer.txt')
    if bearer is None:
        print('Something goes wrong with bearer file')
        exit(2)

    log = get_log(device, bearer)
    if log is None:
        print('Something goes wrong with app to get log')
        exit(2)

    start_point = get_start(log)
    if start_point is None:
        print('Unable to get starting point in log')
        exit(2)

    config = get_config(device, bearer)
    if config is None:
        print('Unable to get config')
        exit(2)

    # DEBUG
    # now = datetime.now()
    # start_point = datetime.timestamp(now)
    # END DEBUG

    scenario = update_scenario_time_event(scenario, start_point)
    if (scenario is None):
        print('Please rewiew scenario : waiting time exceeded\n Or restart the device by push button')
        exit(2)

    event_iterator = 0
    total_scenario = len(scenario)
    task1 = False
    print('\nStarting : ' + list(scenario.keys())[0] + ' contain ' + str(total_scenario) + ' task and ' + str(total_scenario * 2) + " event will be generated\n", flush=True)
    lenbar = scenario[list(scenario.keys())[total_scenario - 1]]['member']['actuation_config']['get_data_at'] - start_point
    printProgressBar(0, lenbar, prefix='Progress:', suffix='Complete', length=50, fill='#')
    while event_iterator < total_scenario:
        if task1 is False and datetime.timestamp(datetime.now()) >= scenario[list(scenario.keys())[event_iterator]]['member']['actuation_config']['provisioning_at']:
            print('\033[Kexectute provisioning task for ' + ' : ' + scenario[list(scenario.keys())[event_iterator]]['member']['test_name'] + '\n', flush=True)
            config = get_config(device, bearer)
            if config is None:
                print('Unable to get config')
                exit(2)
            new_config = update_config(scenario[list(scenario.keys())[event_iterator]], config)
            change_config(device, bearer, new_config)
            task1 = True
        if task1 is True and datetime.timestamp(datetime.now()) >= scenario[list(scenario.keys())[event_iterator]]['member']['actuation_config']['get_data_at']:
            print('\033[Kexectute analyse data for ' + ' : ' + scenario[list(scenario.keys())[event_iterator]]['member']['test_name'] + '\n', flush=True)
            config = get_config(device, bearer)
            if config is None:
                print('Unable to get config')
                exit(2)
            measures = get_measure(device, bearer)
            if measures is None:
                print('Unable to get measures')
                exit(2)
            log = get_log(device, bearer)
            if log is None:
                print('Something goes wrong with app to get log')
                exit(2)
            analyse_frequency(config, measures, scenario[list(scenario.keys())[event_iterator]]['member']['actuation_config'])
            analyse_actuation(config, measures, scenario[list(scenario.keys())[event_iterator]]['member']['actuation_config'])
            event_iterator = event_iterator + 1
            task1 = False
        time.sleep(0.1)
        # Update Progress Bar
        printProgressBar(datetime.timestamp(datetime.now()) - start_point, lenbar, prefix='Progress:', suffix='Complete', length=50, fill='#')
