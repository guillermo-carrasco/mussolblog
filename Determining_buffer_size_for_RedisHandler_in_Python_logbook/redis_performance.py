import json
import time
import logbook
import redis
import threading
import matplotlib.pyplot as plt

from matplotlib.pyplot import *
from collections import OrderedDict
from logbook.queues import RedisHandler


if __name__ == "__main__":

    MESSAGE = "This is message num {num}"
    KEY = 'redis'
    EXECUTIONS = 3

    #Set up Redis
    r = redis.Redis()

    #Set up logging
    l = logbook.Logger()

    #We want to try a buffer of 128, 256, 512 and 1024 messages
    buffer_sizes = [128, 256, 512, 1024]

    #And want to try rushes of
    rushes = [100, 1000, 10000, 100000, 1000000]

    results = OrderedDict()
    results['buffering'] = OrderedDict()
    results['no_buffering'] = OrderedDict()

    #Construct the results dict
    for buffer_size in buffer_sizes:
        results['buffering'][str(buffer_size)] = OrderedDict()
        for rush in rushes:
            results['no_buffering'][str(rush)] = {}
            results['buffering'][str(buffer_size)][str(rush)] = {}

    #########################
    #                       #
    #  Tests with buffering #
    #                       #
    #########################

    for buffer_size in buffer_sizes:
        h = RedisHandler(flush_threshold=buffer_size)
        for rush in rushes:
            for execution in range(EXECUTIONS):
                with h:
                    t_start = time.time()
                    for i in range(rush):
                        l.info(MESSAGE.format(num=str(i)))
                    t_end = time.time()

                    results.get('buffering').get(str(buffer_size)).get(str(rush))[str(execution)] = \
                            str(t_end - t_start)

                #Clean up redis
                while r.keys():
                    r.blpop(KEY)


    ############################
    #                          #
    #  Tests without buffering #
    #                          #
    ############################

    for rush in rushes:
        h = RedisHandler()
        h.disable_buffering()
        for execution in range(EXECUTIONS):
            with h:
                t_start = time.time()
                for i in range(rush):
                     l.info(MESSAGE.format(num=str(i)))
                t_end = time.time()

                results.get('no_buffering').get(str(rush))[str(execution)] = str(t_end - t_start)

            #Clean up redis
            while r.keys():
                r.blpop(KEY)

    #Plot the results and save the plot
    plt.xlabel("Messages")
    plt.ylabel('Insertion time')
    plt.xscale('log')

    b_results = results.get('buffering')
    nb_results = results.get('no_buffering')

    plts = []
    legends = []

    for buff_size in b_results:
        legends.append("Buffer size %s" % buff_size)
        msgs = []
        times = []
        for n_msg, tries in b_results.get(buff_size).iteritems():
            msgs.append(int(n_msg))
            times.append(sum([float(v) for k, v in tries.iteritems()]))
        p, = plt.plot(msgs, times)
        plts.append(p)

    msgs = []
    times = []
    legends.append('No buffering')
    for n_msg, tries in nb_results.iteritems():
        msgs.append(int(n_msg))
        times.append(sum([float(v) for k, v in tries.iteritems()]))
    p, = plt.plot(msgs, times)
    plts.append(p)

    legend(plts, legends, loc=2)
    plt.show()


    #Write down the results
    with open('performance.json', 'w') as f:
        json.dump(results, f)
