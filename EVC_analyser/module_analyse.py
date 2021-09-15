from datetime import datetime


def analyse_frequency(config, measures, scenario, log_file):
    start = scenario['provisioning_at']
    now = datetime.timestamp(datetime.now())
    time_elapsed = now - start
    frequency = config['collectionFrequency'] * 60
    count_actuation_confirm = 1
    supressed_report = 0
    if scenario['config']['actuation1'] < now and scenario['config']['actuation1'] > scenario['provisioning_at'] + (config['collectionFrequency'] * 60):
        count_actuation_confirm += 1
        if (scenario['config']['serial'] == 'true'):
            ev_count = 0
            for item in scenario['config']['ev']:
                if item == 'true':
                    ev_count += 1
            supressed_report += (int((int(scenario['config']['duration'][0]) * ev_count) * 60) / frequency)
        else:
            supressed_report += int((int(scenario['config']['duration'][0]) * 60) / frequency)
    if scenario['config']['actuation2'] < now and scenario['config']['actuation2'] > scenario['provisioning_at'] + (config['collectionFrequency'] * 60):
        count_actuation_confirm += 1
        if (scenario['config']['serial'] == 'true'):
            ev_count = 0
            for item in scenario['config']['ev']:
                if item == 'true':
                    ev_count += 1
            supressed_report += (int((int(scenario['config']['duration'][0]) * ev_count) * 60) / frequency)
        else:
            supressed_report += int((int(scenario['config']['duration'][0]) * 60) / frequency)
    total_message_expected_max = int(time_elapsed / frequency) + count_actuation_confirm
    total_message_expected_min = int(total_message_expected_max - (1 + supressed_report) - 2)
    count_msg = 0
    for item in measures:
        if item['timestamp'] > start and item['message_code'] == 16:
            count_msg = count_msg + 1
    print("\tFrequency analyse : expected : >= " + str(total_message_expected_min) + " <= " + str(total_message_expected_max) + ' found : ' + str(count_msg), flush=True, end='')
    file = open(log_file,"a")
    file.write("\tFrequency analyse : expected : >= " + str(total_message_expected_min) + " <= " + str(total_message_expected_max) + ' found : ' + str(count_msg))
    file.close()
    if count_msg >= total_message_expected_min:
        print(' \033[92mPASS\033[0m\n', flush=True)
        file = open(log_file,"a")
        file.write(" PASS\n")
        file.close()
        return True
    else:
        print(' \033[91mFAIL\033[0m\n', flush=True)
        file = open(log_file,"a")
        file.write(" FAIL\n")
        file.close()
        return False


def analyse_actuation(config, measures, scenario, log_file):
    start = scenario['provisioning_at']
    now = datetime.timestamp(datetime.now())
    # time_elapsed = now - start
    skiped = False
    disengage = False
    if scenario['config']['disengage'] == "true":
        disengage = True
    check_actuation_2 = False
    opening_count = 0
    closing_count = 0
    actuation1_opening_cpt = 0
    actuation2_opening_cpt = 0
    actuation1_closing_cpt = 0
    actuation2_closing_cpt = 0
    opening_closing_expected = 0
    ev_count = 0
    actuation1_start_min = int(scenario['config']['actuation1']) - 60
    actuation1_start_max = int(scenario['config']['actuation1']) + 60
    actuation1_stop_min = actuation1_start_min + (int(scenario['config']['duration'][0]) * 60)
    actuation1_stop_max = actuation1_start_max + (int(scenario['config']['duration'][0]) * 60)
    actuation2_start_min = int(scenario['config']['actuation2']) - 60
    actuation2_start_max = int(scenario['config']['actuation2']) + 60
    actuation2_stop_min = actuation2_start_min + (int(scenario['config']['duration'][0]) * 60)
    actuation2_stop_max = actuation2_start_max + (int(scenario['config']['duration'][0]) * 60)
    measures.reverse()
    for item in scenario['config']['ev']:
        if item == 'true':
            ev_count += 1
    if (actuation1_start_min > start and actuation1_stop_max < now):
        opening_closing_expected += 2
    if (actuation2_start_min > start and actuation2_stop_max < now):
        opening_closing_expected += 2
        check_actuation_2 = True

    if (scenario['config']['serial'] == 'false'):
        print("\tSerial : FALSE\n", flush=True)
        file = open(log_file,"a")
        file.write("\tSerial : FALSE\n")
        file.close()
        for item in measures:
            if item['timestamp'] > start and item['message_code'] == 21:
                if item['timestamp'] >= actuation1_start_min and item['timestamp'] <= actuation1_start_max:
                    opening_count += 1
                    actuation1_opening_cpt = int(item['pulse_cumulative'])
                    print("\topenening 1 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\topenening 1 : " + item['created_at'] + " PASS\n")
                    file.close()
                    if disengage == True and item['action_status'] == 6:
                        print("\tdisengage 1 :" + " \033[92mPASS\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 1 :" + " PASS\n")
                        file.close()
                        skiped = True
                    elif disengage == True and item['action_status'] != 6:
                        print("\tdisengage 1 :" + " \033[91mFAIL\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 1 :" + " FAIL\n")
                        file.close()
                elif item['timestamp'] >= actuation2_start_min and item['timestamp'] <= actuation2_start_max:
                    opening_count += 1
                    actuation2_opening_cpt = int(item['pulse_cumulative'])
                    print("\topenening 2 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\topenening 2 : " + item['created_at'] + " PASS\n")
                    file.close()
                    if disengage == True and item['action_status'] == 6:
                        print("\tdisengage 2 :" + " \033[92mPASS\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 2 :" + " PASS\n")
                        file.close()
                        skiped = True
                    elif disengage == True and item['action_status'] != 6:
                        print("\tdisengage 2 :" + " \033[91mFAIL\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 2 :" + " FAIL\n")
                        file.close()
                else:
                    print("\topenening Unwanted : " + item['created_at'] + " \033[91mFAIL\033[0m\n\t" + str(item['timestamp']) + " Needed >= " + str(actuation1_stop_min) + " <= " + str(actuation1_stop_max) + " OR >= " + str(actuation2_stop_min) + " <= " + str(actuation2_stop_max) + "\n" , flush=True)
                    file = open(log_file,"a")
                    file.write("\topenening Unwanted : " + item['created_at'] + " FAIL\n")
                    file.close()
            if item['timestamp'] > start and item['message_code'] == 25:
                if item['timestamp'] >= actuation1_stop_min and item['timestamp'] <= actuation1_stop_max:
                    closing_count += 1
                    actuation1_closing_cpt = int(item['pulse_cumulative'])
                    print("\tclosing 1 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\tclosing 1 : " + item['created_at'] + " PASS\n")
                    file.close()
                elif item['timestamp'] >= actuation2_stop_min and item['timestamp'] <= actuation2_stop_max:
                    closing_count += 1
                    actuation2_closing_cpt = int(item['pulse_cumulative'])
                    print("\tclosing 2 : " + item['created_at'] + " " + str(item['timestamp']) + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\tclosing 2 : " + item['created_at'] + " PASS\n")
                    file.close()
                else:
                    print("\tclosing Unwanted : " + item['created_at'] + " \033[91mFAIL\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\tclosing Unwanted : " + item['created_at'] + " FAIL\n")
                    file.close()

    else:
        print("\tSerial : TRUE\n", flush=True)
        file = open(log_file,"a")
        file.write("\tSerial : TRUE\n")
        file.close()
        actuation1_stop_min += ((int(scenario['config']['duration'][0]) * 60) * (ev_count - 1)) + (ev_count * 6) + (20 * ev_count)
        actuation1_stop_max += ((int(scenario['config']['duration'][0]) * 60) * (ev_count - 1)) + (ev_count * 6) + (20 * ev_count)
        actuation2_stop_min += ((int(scenario['config']['duration'][0]) * 60) * (ev_count - 1)) + (ev_count * 6) + (20 * ev_count)
        actuation2_stop_max += ((int(scenario['config']['duration'][0]) * 60) * (ev_count - 1)) + (ev_count * 6) + (20 * ev_count)
        if disengage == False:
            opening_closing_expected *= ev_count
        for item in measures:
            if item['timestamp'] >= start and item['message_code'] == 21:
                if item['timestamp'] >= actuation1_start_min and item['timestamp'] <= actuation1_start_max:
                    opening_count += 1
                    actuation1_opening_cpt = int(item['pulse_cumulative'])
                    print("\topenening 1 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\topenening 1 : " + item['created_at'] + " PASS\n")
                    file.close()
                    if disengage == True and item['action_status'] == 6:
                        print("\tdisengage 1 :" + " \033[92mPASS\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 1 :" + " PASS\n")
                        file.close()
                        skiped = True
                    elif disengage == True and item['action_status'] != 6:
                        print("\tdisengage 1 :" + " \033[91mFAIL\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 1 :" + " FAIL\n")
                        file.close()
                elif item['timestamp'] >= actuation2_start_min and item['timestamp'] <= actuation2_start_max:
                    opening_count += 1
                    actuation2_opening_cpt = int(item['pulse_cumulative'])
                    print("\topenening 2 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\topenening 2 : " + item['created_at'] + " PASS\n")
                    file.close()
                    if disengage == True and item['action_status'] == 6:
                        print("\tdisengage 2 :" + " \033[92mPASS\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 2 :" + " PASS\n")
                        file.close()
                        skiped = True
                    elif disengage == True and item['action_status'] != 6:
                        print("\tdisengage 2 :" + " \033[91mFAIL\033[0m\n", flush=True)
                        file = open(log_file,"a")
                        file.write("\tdisengage 2 :" + " FAIL\n")
                        file.close()
                elif item['timestamp'] >= actuation1_start_min and item['timestamp'] <= actuation1_stop_max:
                    opening_count += 1
                elif item['timestamp'] >= actuation2_start_min and item['timestamp'] <= actuation2_stop_max:
                    opening_count += 1
                else:
                    print("\topenening Unwanted : " + item['created_at'] + " \033[91mFAIL\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\topenening Unwanted : " + item['created_at'] + " FAIL\n")
                    file.close()
            if item['timestamp'] >= start and item['message_code'] == 25:
                if item['timestamp'] >= actuation1_stop_min and item['timestamp'] <= actuation1_stop_max:
                    closing_count += 1
                    actuation1_closing_cpt = int(item['pulse_cumulative'])
                    print("\tclosing 1 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\tclosing 1 : " + item['created_at'] + " PASS\n")
                    file.close()
                elif item['timestamp'] >= actuation2_stop_min and item['timestamp'] <= actuation2_stop_max:
                    closing_count += 1
                    actuation2_closing_cpt = int(item['pulse_cumulative'])
                    print("\tclosing 2 : " + item['created_at'] + " \033[92mPASS\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\tclosing 2 : " + item['created_at'] + " PASS\n")
                    file.close()
                elif item['timestamp'] >= actuation1_start_min and item['timestamp'] <= actuation1_stop_max:
                    opening_count += 1
                elif item['timestamp'] >= actuation2_start_min and item['timestamp'] <= actuation2_stop_max:
                    opening_count += 1
                else:
                    print("\tclosing Unwanted : " + item['created_at'] + " \033[91mFAIL\033[0m\n", flush=True)
                    file = open(log_file,"a")
                    file.write("\tclosing Unwanted : " + item['created_at'] + " FAIL\n")
                    file.close()

    if skiped == False :
        if opening_closing_expected == opening_count + closing_count:
            print("\tNb opening/closing : " + str(opening_count + closing_count) + " \033[92mPASS\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tNb opening/closing : " + str(opening_count + closing_count) + " PASS\n")
            file.close()
        else:
            print("\tNb opening/closing : " + str(opening_count + closing_count) + " \033[91mFAIL\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tNb opening/closing : " + str(opening_count + closing_count) + " FAIL\n")
            file.close()
        if (actuation1_closing_cpt - actuation1_opening_cpt == ev_count * 2):
            print("\tLoopback control actuation 1 : " + str(actuation1_closing_cpt - actuation1_opening_cpt) + " \033[92mPASS\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tLoopback control actuation 1 : " + str(actuation1_closing_cpt - actuation1_opening_cpt) + " PASS\n")
            file.close()
        else:
            print("\tLoopback control actuation 1 : \033[91mFAIL\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tLoopback control actuation 1 : " + str(actuation1_closing_cpt - actuation1_opening_cpt) + " FAIL\n")
            file.close()
        if (actuation2_closing_cpt - actuation2_opening_cpt == ev_count * 2 and check_actuation_2 is True):
            print("\tLoopback control actuation 2 : " + str(actuation2_closing_cpt - actuation2_opening_cpt) + " \033[92mPASS\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tLoopback control actuation 2 : " + str(actuation1_closing_cpt - actuation1_opening_cpt) + " PASS\n")
            file.close()
        elif check_actuation_2 is True:
            print("\tLoopback control actuation 2 : \033[91mFAIL\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tLoopback control actuation 2 : " + str(actuation1_closing_cpt - actuation1_opening_cpt) + " FAIL\n")
            file.close()
    else:
        if opening_closing_expected / 2 == opening_count:
            print("\tNb opening/closing : " + str(opening_count) + " \033[92mPASS\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tNb opening/closing : " + str(opening_count) + " PASS\n")
            file.close()
        else:
            print("\tNb opening/closing : " + str(opening_count) + " \033[91mFAIL\033[0m\n", flush=True)
            file = open(log_file,"a")
            file.write("\tNb opening/closing : " + str(opening_count) + " FAIL\n")
            file.close()


def analyse_reboot(start_point, log, actuation_max, log_file):
    now = datetime.timestamp(datetime.now())
    time_elapsed = (now - start_point) /60
    nb_sanity_req = int(time_elapsed / ((48*60) + actuation_max))
    sanity_found = 0
    unwanted_reboot = 0
    log.reverse()
    ret = True
    for item in log:
        if int(item['timestamp']) > int(start_point):
            if item['message'] == 'Device rebooted because of Sanity reboot':
                sanity_found += 1
                print("\tSanity executed at : " + item['time'] + "\n", flush=True)
                file = open(log_file,"a")
                file.write("\tSanity executed at : " + item['time'] + "\n")
                file.close()
            elif "rebooted" in item['message']:
                unwanted_reboot += 1
                print("\tUnwanted reboot at : " + item['time'] + '\n', flush=True)
                file = open(log_file,"a")
                file.write("\tUnwanted reboot at : " + item['time'] + '\n')
                file.close()
    # print("\tdebug sanity_found : " + str(sanity_found) + " req : " + str(nb_sanity_req) + "\n")
    if sanity_found < nb_sanity_req:
        print("\tSanity analyse \033[91mFAIL\033[0m\n")
        file = open(log_file,"a")
        file.write("\tSanity analyse FAIL\n")
        file.close()
        ret = False
    else :
        print("\tSanity analyse \033[92mPASS\033[0m\n")
        file = open(log_file,"a")
        file.write("\tSanity analyse PASS\n")
        file.close()
    if unwanted_reboot != 0:
        print("\tReboot analyse \033[91mFAIL\033[0m\n")
        file = open(log_file,"a")
        file.write("\tReboot analyse FAIL\n")
        file.close()
        ret = False
    else :
        print("\tReboot analyse \033[92mPASS\033[0m\n")
        file = open(log_file,"a")
        file.write("\tReboot analyse PASS\n")
        file.close()
    return ret
