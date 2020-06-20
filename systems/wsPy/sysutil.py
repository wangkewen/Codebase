import collections
import os
import subprocess
import sys
import time
import math
from collections import defaultdict
from collections import namedtuple


def open_binary(filename, **kwargs):
    return open(filename, "rb", **kwargs)

PROC_PATH = "/proc"
CLOCK_TICKS = os.sysconf("SC_CLK_TCK")

_timer = getattr(time, 'monotonic', time.time)
#global statcpu

class Process(object):
    def __init__(self, pid=None):
        self._pid = pid
        if not pid:
            self._pid = os.getpid()
        self._name = None
        self._exe = None
        self._create_time = None
        self._proc = None

    def _is_exists_pid(self):
        return os.path.exists("%s/%s" % (PROC_PATH, self._pid))

    def _parse_stat_file(self):
	"parse /proc/{pid}/stat file"
        if not self._is_exists_pid():
            return None
        with open_binary("%s/%s/stat" % (PROC_PATH, self._pid)) as f:
            data = f.read()
        # '()' contains process name
        rp = data.rfind(b')')
        name = data[data.find(b'(') + 1:rp]
        fields = data[rp + 2:].split()
      
        values = {}
        values['name'] = name
        # status: R, S, D, Z, T      
        values['status'] = fields[0]
        values['ppid'] = fields[1]
        # controlling terminal of the proces (device number)
        values['ttynr'] = fields[4]
        # kernel flags word of the process
        values['flags'] = fields[6]
        # user mode time
        values['utime'] = fields[11]
        # kernel mode time
        values['stime'] = fields[12]
        values['children_utime'] = fields[13]
        values['children_stime'] = fields[14]
        values['priority'] = fields[15]
        values['nice'] = fields[16]
        values['num_threads'] = fields[17]
        values['create_time'] = fields[19]
        # CPU number last executed on
        values['cpu_num'] = fields[36]
        values['rt_priority'] = fields[37]
        values['exit_code'] = fields[49]
        return values
    
    def _read_status_file(self):
        if not self._is_exists_pid():
            return None
        with open_binary("%s/%s/status" %(PROC_PATH, self._pid)) as f:
            return f.read()

    def cpu_times(self, percpu=False):
        if not self._is_exists_pid():
            return None
        values = self._parse_stat_file()
        utime = float(values['utime']) / CLOCK_TICKS
        stime = float(values['stime']) / CLOCK_TICKS
        children_utime = float(values['children_utime']) / CLOCK_TICKS
        children_stime = float(values['children_stime']) / CLOCK_TICKS
        return namedtuple('pstat', ['user', 'system', 
           'children_user', 'children_system'])(utime, stime, children_utime, children_stime)

    def cpu_percent(self, interval=None):
        #cpu util of current process
        blocking = interval is not None and interval > 0.0
        if interval is not None and interval < 0:
            raise ValueError("interval should be positive")
        cpusnum = cpu_count() or 1
        def timer():
            return _timer() * cpusnum
        if blocking:
            start = timer()
            process_t1 = self.cpu_times()
            time.sleep(interval)
            end = timer()
            process_t2 = self.cpu_times()
            if not process_t1 or not process_t2:
                return 0.0
        else:
            return 0.0
        processtime = process_t2.user + process_t2.system \
                      - process_t1.user - process_t1.system
        alltime = end - start
        try:
            cpuper = cpusnum * (processtime / alltime) * 100
        except ZeroDivisionError:
            return 0.0
        else:
            if cpuper <= 0:
                cpuper = 0.0
            return round(cpuper, 1)
            

def cpu_count():
    #obtain number of logical cpus
    try:
	return os.sysconf('SC_NPROCESSORS_ONLN')
    except ValueError:
	cpunum = 0
	with open_binary('%s/cpuinfo' % PROC_PATH) as f:
	    for line in f:
		if line.lower().startswith(b'processor'):
		    cpunum += 1
	if cpunum == 0:
	    with open_binary('%s/stat' % PROC_PATH) as f:
		for line in f:
		    if re.compile(r'cpu\d').match(line.split()[0]):
			cpunum += 1
	if cpunum == 0:
	    return None
	return cpunum

def set_cpu_fieldname():
    global statcpu
    fields = ['user', 'nice', 'system', 'idle', 'iowait', 
	      'irq', 'softirq']
    newfields = ['steal', 'guest', 'guest_nice']
    fields += newfields
    statcpu = namedtuple('statcpu', fields)
    return fields 

def stat_cpu_times():
    set_cpu_fieldname()
    with open_binary("%s/stat" % PROC_PATH) as f:
	values = f.readline().split()[1:]
    values =[float(x) / CLOCK_TICKS for x in values]
    return statcpu(*values)

def per_cpu_times():
    #parse proc/stat file
    set_cpu_fieldname()
    allcpus = []
    with open_binary("%s/stat" % PROC_PATH) as f:
	f.readline()
	for line in f:
	    values = line.split()[1:]
	    values = [float(x) / CLOCK_TICKS for x in values]
	    allcpus.append(statcpu(*values))
    return allcpus

def loadavg():
    #tuple(0,0,0)
    #number of processes in the system run queue avg over the last 1,5,15 minutes
    if hasattr(os, "getloadavg"):
	return os.getloadavg()
    else:
	return None

def processData():
    data = []
    # out.txt pr2g vm
    # whole.txt pr2g 
    f = open("out.txt", "r")
    for e in f.readlines():
        item = float(e)
        data.append(item)
    print(data)
    grid(data)

##########################################
#  design a controller
##########################################

def grid(data):
    """grid search for optimal parameters
       for adaptive controller
    """

    start, end = 10,500
    interval = 10
    arr_delta = [i for i in range(start, end + interval, interval)]
    start, end = 10, 100
    interval = 1
    arr_mult = [i * 0.1 for i in range(start, end + interval, interval)]
    print arr_mult
    opt_arr = []
    opt = []
    max_dis = len(data) * 4000 * 4000
    sum_data = sum(data)
    # arr_delta, arr_mult = [100], [2]
    # search for optimal parameters 
    for delta in arr_delta:
        for mult in arr_mult:
	    dis = 0
            base = delta
	    est = delta
	    estsum = 0
	    errsum = 0
	    est_arr = []
            isfalse = True
	    for i in range(len(data)):
		est_arr.append(est)
		dis += abs(data[i] - est) ** 2
                errsum += est - data[i]
                if errsum < 0:
                    isfalse = False
                estsum += est
                if est < data[i] + delta:
                    base *= mult
                else:
                    base = delta
                est = data[i] + base
                est = min(2000, est)
	    if dis < max_dis and isfalse:
		max_dis = dis
		opt = [delta, mult]
		opt_arr = est_arr    
    print(opt)
    print("sum_arr: %s" % sum(opt_arr))
    rs = ""
    for e in opt_arr:
        rs += " "+ str(e)
    print rs


def pid(data):
    """
    PID
    kp, ki, kd = 1, 1, 1
    # e_n = u - u_observ
    e_n = [0.1, 0.2, 0.5, -0.1]
    u = kp * e + ki * sum(e_n) + kd * (e_n[-1] - e_n[-2])
    """
    start, end = 0,3
    delta = [start + 0.1 * i for i in range(0, int(round((end-start)/0.1)))]
    #delta = range(start, end)
    print(delta)
    opt_arr = []
    max_dis = len(data) * 4000 * 4000 
    alpha = 1
    for kp in delta:
        for ki in delta:
            for alpha in [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
		dis = 0
		est = 0
		errSum = 0
		preErr = 0
		est_arr = []
		for i in range(len(data)):
		    est = max(0.0, est)
		    est = min(2000, est)
		    est_arr.append(int(math.floor(est)))
		    curErr = (est - data[i])
		    dis += abs(curErr) ** 2
		    errSum += curErr
		    #ut = kp * curErr + ki * errSum + kd * (curErr - preErr)
		    ut = kp * curErr + ki * errSum
		    est = alpha*est - ut
		    preErr = curErr
		if dis < max_dis:
		    max_dis = dis
		    opt = [kp, ki, alpha]
		    opt_arr = est_arr    
    print(opt)
    
    opt_arr = []
    est = 0
    errSum = 0
    for i in range(len(data)):
        est = min(2000, max(0.0, est))
        opt_arr.append(int(math.floor(est)))
        curErr = est - data[i]
        errSum += curErr
        ut = 0.5 * curErr + 0.0 * errSum
        est = 1.1 * est - ut
    
    rs = ""
    for e in opt_arr:
        e = int(math.floor(e))
        rs += " "+ str(e)
        print e
    print rs


def feedback():
    est = 0
    errSum = 0
    opt_arr = []
    kp, ki, alpha = 1.1, 0.2, 1.1
    while True:
        est = min(2000, max(0.0, est))
        opt_arr.append(int(math.floor(est)))
        curErr = est - data[i]
        errSum += curErr
        ut = kp * curErr + ki * errSum
        est = alpha * est - ut


def tcp_id(data):
    """
    TCP like
    """
    est = 0.0
    est_arr = [] 
    start, end = 0,5
    delta = [start + 0.1 * i for i in range(0, int(round(end/0.1)))]
    opt = [0,0]
    opt_arr = []
    max_dis = len(data) * 2000 * 2000
    for alpha_increase in delta:
        for alpha_decrease in delta:
            dis = 0
            pos = 0
            est = 0
            est_arr = []
	    for i in range(len(data)):
                est = max(0.0, est)
                est_arr.append(est)
                dis += abs(data[i]-est) ** 2
		if i == 0 or data[i] >= data[i-1]:
		    est = alpha_increase * est + (1 - alpha_increase) * data[i]
		else:
		    est = alpha_decrease * est + (1 - alpha_decrease) * data[i]
	    if dis < max_dis:
		max_dis = dis
                opt = [alpha_increase, alpha_decrease]
                opt_arr = est_arr    
    print(opt)
    rs = ""
    for e in opt_arr:
        e = int(math.floor(e))
        rs += " "+ str(e)
        print e
    print rs

def main():
    '''
    pid = int(sys.argv[1])
    interval = 1
    p = Process(pid)
    while True:
        if not p._is_exists_pid():
            break
        print(p.cpu_percent(interval))
    '''
    processData()
if __name__ == "__main__":
    main()
