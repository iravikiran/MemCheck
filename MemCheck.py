"""
    Memory Check for Bandwidth Analysis..
    ->  Create a Thread (T1) for executing the process separately.
    ->  Starts a new thread for checking memory consumption of the T1 process.
    ->  Continuously keeps monitoring the system memory usages of Thread (T1) by creating an new Thread T2.

    Author - Ravi Kiran
    GitHub - iravikiran (https://ravi-kiran.me)

TODOs/Changelog:
    -> Process Handler for each threads. - done..
    -> Max to Min Memory tracings. - done..
    -> Thread ID & Thread wise execution status - done..
    -> STDOUT to file buff over Console. - done..
    -> Log threads and memory usages - done..
    -> kmalloc info traces for driver memory usages. - TODO
        -> To add traces for Slabinfo - TODO
    -> Thread Logging - TODO

"""

import subprocess
import threading
import time
import logging as log

log_file = "debug_" + str(time.time()) + ".log"

log.basicConfig(filename=log_file, level=log.DEBUG, format='%(levelname)s (%(threadName)-9s) %(message)s', filemode="w")

MemTotal = "/proc/meminfo | grep MemTotal:"
MemFree = "/proc/meminfo | grep MemFree:"
MemAvailable = "/proc/meminfo | grep MemAvailable:"
MemUsage = []


#
#   Function implementation for checking Initial Memory value before execution
#       of the process threads.
#           Accepts - None.
#           returns - Memory value: (*int)
#
def InitMemInfo():
    """
        Function to check for Initial Memory available on Entry.
            -> This Memory value is called at the start of process execution (T1).
    """
    try:
        InitMemAvail = subprocess.check_output('cat ' + MemAvailable, shell=True).decode('utf-8')
        log.debug("(InitMemInfo): Available Memory on Entry: {0}" .format(InitMemAvail.split(" ")[-2] + " kB"))
        return int(InitMemAvail.split(" ")[-2])
    except subprocess.CalledProcessError:
        log.debug("(InitMemInfo): Unable to get Initial Memory Info. Exit (-1)")
        exit(-1)


#
#   Function implementation for checking Exit Memory value after execution
#       of the process threads.
#           Accepts - None.
#           returns - Memory value: (*int)
#
def ExitMemInfo():
    """
        Function to check for Exit Memory available on Entry.
            -> This Memory value is called at the End of process execution (T1).
    """
    try:
        ExitMemAvail = subprocess.check_output('cat ' + MemAvailable, shell=True).decode('utf-8')
        log.debug("(ExitMemInfo): Available Memory on Exit: {0}" .format(ExitMemAvail.split(" ")[-2] + " kB"))
        return int(ExitMemAvail.split(" ")[-2])
    except subprocess.CalledProcessError:
        log.debug("(ExitMemInfo): Unable to get Initial Memory Info. Exit (-2)")
        exit(-2)


#
#   Function implementation for checking Memory value while in process execution
#       of the threads.
#           Accepts - None.
#           returns - Memory value: (*int)
#
def ProcessMemInfo():
    """
        Function to check for Memory consumed while in process execution.
            -> This Memory value is called by creating a T2 and monitoring the Memory status of
                process at T1 .
    """
    try:
        ProcessMem = subprocess.check_output('cat ' + MemAvailable, shell=True).decode('utf-8')
        log.debug("(ProcessMemInfo): Memory Consumption while in Process: {0} kB" .format(ProcessMem.split(" ")[-2]))
        return int(ProcessMem.split(" ")[-2])
    except subprocess.CalledProcessError:
        log.debug("(ProcessMemInfo): Unable to get TearDown Memory Info. Exit (-2)")
        exit(-3)


#
#   Function implementation for checking Memory value while in process execution
#       of the threads, and logs the value in MB/kB.
#           Accepts - Initial Memory Value: (*int), Peak Memory Value: (*int).
#
def GetMemoryConsumption(InitMem, PeakMem):
    """
            Function to check for Memory consumed while in process execution.
                -> This Memory value is called by creating a T2 and monitoring the Memory status of
                    process at process Threads.
    """
    MemoryConsumption = InitMem - PeakMem
    log.debug("(GetMemoryConsumption): Overall Memory Consumption: {0} MB, ({1} kB)"
              .format(MemoryConsumption / 1000, str(MemoryConsumption)))
    print("(GetMemoryConsumption): Overall Memory Consumption: {0} MB, ({1} kB)"
              .format(MemoryConsumption / 1000, str(MemoryConsumption)))


#
#   Function implementation for checking Memory value while in process execution
#       of the threads.
#           Accepts - execution commands for each process: (*string)
#
def ExecuteMain(exec_cmd):
    """
            Function to handle the process execution, with a separate Thread (T1).
                -> Executes as a new process and logs the execution time for that process.
    """
    file = open(str(threading.currentThread().ident) + ".log", "w")
    start_time = time.time()
    exec_process = subprocess.Popen(exec_cmd, shell=True, stdout=file, stderr=file)
    log.debug("(ExecuteMain): Execution started for thread: {0} and with Process ID (PID): {1}"
              .format(threading.currentThread().ident, exec_process.pid))
    exec_process.wait()
    end_time = time.time()
    log.debug("(ExecuteMain): Total Execution time for thread: {0}, {1} secs" .format(threading.currentThread().ident,
                                                                                      int(end_time - start_time)))
    if exec_process.returncode == 0:
        log.debug("(ExecuteMain): Execution Success for thread {0}:" .format(threading.currentThread().ident))
    else:
        log.debug("(ExecuteMain): Error, Executing the test program. Exit(-4) - {0}"
                  .format(threading.currentThread().ident))
        exit(-4)
    file.close()


#
#   Function implementation for checking Memory value while in process execution
#       of the threads.
#           Accepts - execution commands for each process: (*string)
#
def CheckMem(InitMem):
    """
            Function to handle the process execution, with a separate Thread (T1).
                -> Executes as a new process and logs the execution time for that process.
    """
    PeakMem = InitMem
    while 1:
        if threading.activeCount() > 2:
            log.debug("(CheckMem): Checking Memory usage..")
            time.sleep(1)
            # PsAux = subprocess.check_output("ps -aux | grep " + "'" + str(mem_cmd) + "'" + " | sed -n 2p ",
            #                                shell=True).decode('utf-8')
            # MemUsage.append(PsAux.split(" ")[7:10])
            # print(MemUsage)
            MemVal = ProcessMemInfo()
            if MemVal <= PeakMem:
                log.debug("(CheckMem): Peak Memory Value: {0} kB" .format(MemVal))
                PeakMem = MemVal
            else:
                pass
            log.debug("(CheckMem): Highest Peak Memory: {0} kB" .format(PeakMem))
            GetMemoryConsumption(InitMem, PeakMem)
        else:
            log.debug("(CheckMem): Process is complete, Exiting CheckMem (0)..")
            exit(0)


"""
    Main function call.
"""
if __name__ == '__main__':

    process = ["lsusb", "dmesg"]

    threads = []

    InitMem = InitMemInfo()

    for cmd in process:
        t1 = threading.Thread(target=ExecuteMain, args=(cmd,))
        threads.append(t1)

    t2 = threading.Thread(target=CheckMem, args=(InitMem,))

    log.debug("(Main): Starting all the threads..")
    for thread in threads:
        thread.start()

    log.debug("(Main): Threads Initiated - {0}" .format(threading.enumerate()[1:]))

    t2.start()

    log.debug("(Main): Joining Thread-1 & Thread-2.")
    for thread in threads:
        thread.join()

    t2.join()
    log.debug("(Main): All Threads are executed!")
