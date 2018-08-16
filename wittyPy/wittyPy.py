import os
import subprocess as sp
import datetime
from calendar import monthrange
from shutil import copyfile

class WittyPi():
    ''' Central instance to run functions on the wittyPy.

    :param path:
        Path to your wittyPi folder (Where "wittyPi.sh", "utilities.sh", "daemon.sh" can be found).
    :type path: ``str``
    :param next_start:
        WittyTime object, if a startup is set, else None.
    :type next_start: ``WittyTime``
    :param next_shutdown:
        WittyTime object, if a shutdown is set, else None.
    :type next_shutdown: ``WittyTime``
    :param available_schedules:
        List of available schedules.
    :type available_schedules: ``list``
    :param timedelta:
        Difference between system time and Realtime Clock time. If positive, system time is ahead of the RTC and vice versa.
    :type timedelta: ``float``

    '''
    required_files = ["wittyPi.sh", "utilities.sh", "daemon.sh"]
    def __init__(self, path):
        self.path = path
        self.next_start = None
        self.next_shutdown = None
        self.timedelta = None
        self.available_schedules = []
        self._initial_check()

    def __repr__(self):
        return "WittyPi2(State: {}, {}, {}, Available Schedules: {})".format(self.path, self.next_start, self.next_shutdown, self.available_schedules)

    def __run_util_function(self, function, *args):
        connection = sp.run(["sudo", "bash","-c", "source "+ self.path +"utilities.sh && " + function + " "+" ".join([str(arg) for arg in args])], stdout=sp.PIPE)
        return (connection.returncode, connection.stdout.decode("UTF-8"))

    def _initial_check(self):
        for f in self.required_files:
           if not os.path.isfile(self.path+f):
              raise Exception("Requirement Error: WittyPi Software '{}' not in '{}'.".format(f, self.path))
        if self.__run_util_function("is_rtc_connected")[0] == 1:
           raise Exception("Requirement Error: WittyPi2 Hardware not correctly connected.")
        self._get_startup()
        self._get_shutdown()
        self._list_schedules()
        self._compare_times()

    def _split_date_str(self, date_str):
        return date_str.replace('\n', '').replace(":", " ").split(" ")

    def _get_startup(self):
        t = self.__run_util_function("get_startup_time")
        local_t = self.__run_util_function("get_local_date_time", "'{}'".format(t[1].replace("\n", "")))
        if len(local_t[1]) < 5:
            self.next_start = WittyTime(name = "boot")
        else:
            self.next_start = WittyTime(*self._split_date_str(local_t[1]), name="boot")

    def _get_shutdown(self):
        t = self.__run_util_function("get_shutdown_time")
        local_t = self.__run_util_function("get_local_date_time", "'{}'".format(t[1].replace("\n", "")))
        if len(local_t[1]) < 5:
            self.next_shutdown = WittyTime(name = "shutdown")
        else:
            self.next_shutdown = WittyTime(*self._split_date_str(local_t[1]), name="shutdown")

    def _list_schedules(self):
        tmpls = []
        for f in os.listdir(self.path+"schedules"):
           if f.endswith(".wpi"):
               tmpls.append(f)
        self.available_schedules = sorted(tmpls)

    def activate_schedule(self, index):
        '''Activates a WittyPi schedule, chosen by their index in self.available_schedules.'''
        if index -1 > len(self.available_schedules):
           raise Exception("Index Error: No schedule at index {} of self.available_schedules.".format(index))
        copyfile(self.path + "schedules/" + self.available_schedules[index], self.path + "/schedule.wpi")
        sp.run(["sudo", "bash","-c", "source "+ self.path +"runScript.sh"], stdout=sp.PIPE)
        self._get_startup()
        self._get_shutdown()

    def set_startup(self, *args):
        '''Set startup for the WittyPi. Takes up to four \*args.

        :param \*args:
            1. Day (``int`` or ``str``): Either integer between 1-31 or "??" for wildcard.
            2. Hour (``int`` or ``str``): Either integer between 0-23 or "??" for wildcard.
            3. Minute (``int``): Integer between 0-59.
            4. Second (``int``): Integer between 0-59.

        '''
        new_time = WittyTime(*args)
        when = self.__run_util_function("get_utc_date_time", new_time.day, new_time.hour, new_time.minute, new_time.second)
        self.__run_util_function("set_startup_time", *self._split_date_str(when[1]))
        self._get_startup()

    def set_shutdown(self, *args):
        '''Set shutdown for the WittyPi. Takes up to three \*args.

        :param \*args:
            1. Day (``int`` or ``str``): Either integer between 1-31 or "??" for wildcard.
            2. Hour (``int`` or ``str``): Either integer between 0-23 or "??" for wildcard.
            3. Minute (``int``): Integer between 0-59.

        '''
        new_time = WittyTime(*args)
        when = self.__run_util_function("get_utc_date_time", new_time.day, new_time.hour, new_time.minute, new_time.second)
        self.__run_util_function("set_shutdown_time", *self._split_date_str(when[1]))
        self._get_shutdown()

    def reset(self, option):
        '''Resets the WittyPi according to options

        :param option:
            Options: startup, shutdown, script, all.
        :type options: ``str``

        '''
        options = ["startup", "shutdown", "schedule", "all"]
        if option not in options:
            raise Exception('Error: Chose one of these options: "startup", "shutdown", "schedule", "all"')
        if option != "shutdown":
            self.__run_util_function("clear_startup_time")
        if option != "startup":
            self.__run_util_function("clear_shutdown_time")
        if option in ["schedule", "all"]:
            try:
                os.remove(self.path + "/schedule.wpi")
            except:
                pass
        self._get_startup()
        self._get_shutdown()

    def _compare_times(self):
        '''Compare RTC time with system time. Positive self.timdelta means your system time is ahead of the RTC and vice versa.'''
        rtc = self.__run_util_function("get_rtc_time")[1].replace("\n", "")
        sys_time = datetime.datetime.now()
        self.timedelta = (sys_time - datetime.datetime.strptime(rtc, "%a %d %b %Y %H:%M:%S %Z")).total_seconds()


class WittyTime():
    '''WittyTime object to validate and store times for the WittyPi.

    :param name:
        Type of time. Shutdown or Boot.
    :type name: ``str``
    :param as_date:
        WittyTime as datetime object.
    :type as_date: ``datetime``
    :param day:
    :type day: ``int`` or ``str``
    :param hour:
    :type hour: ``int`` or ``str``
    :param minute:
    :type minute: ``int`` or ``str``
    :param second:
    :type second: ``int`` or ``str``

    '''
    def __init__(self, *args, name=None):
        self.name = name
        self.day = "unset"
        self.hour = "unset"
        self.minute = "unset"
        self.second = "unset"
        self.as_date = "unset"
        self.__validate(*args)

    def __validate(self, *args):
        self.__check_format(args)
        self.__to_datetime()

    def __check_format(self, args):
        args = [arg for arg in args]
        if len(args) == 0:
            return
        for var in args:
            try:
               args[args.index(var)] = int(var)
            except:
               pass
        if args[0] == 0:
            return
        elif args[0] not in range(1, 32) and args[0] != "??":
            raise Exception("Format Error: Day must be an integer between 1-31 or '??' for wildcard.")
        else:
            self.day = args[0]
        if len(args) == 1:
            self.hour = 00
            self.minute = 00
            self.second = 00
            return
        elif args[1] in range(24):
            self.hour = args[1]
        elif args[1] == "??":
            if not self.day == "??":
                raise Exception("Format Error: Wildcards must be used from left to right.")
            else:
                self.hour = args[1]
        else:
            raise Exception("Format Error: Hour must be an integer between 0-24 or '??' for wildcard.")
        if len(args) == 2:
            self.minute = 00
            self.second = 00
            return
        elif args[2] in range(60):
            self.minute = args[2]
        elif args[2] == "??":
            raise Exception("Format Error: Wildcards should only be used for Days and Hours. Not for Minutes")
        else:
            raise Exception("Format Error: Minute must be integer between 0-59.")
        if len(args) == 3:
            self.second = 00
        elif args[3] in range(60):
            self.second = args[3]
        elif args[3] == "??":
            raise Exception("Format Error: Wildcards should only be used for Days and Hours. Not for Seconds")
        else:
            raise Exception("Format Error: Second must be integer between 0-59.")
        return

    def __to_datetime(self):
        if self.day == 'unset':
            return
        now = datetime.datetime.now()
        next = {'year':now.year, 'month': now.month, 'minute': self.minute, 'second':self.second}
        extramonth = False
        if self.hour == '??':
            if self.minute < now.minute:
                next['hour'] = now.hour + 1
                if next['hour'] > 23:
                    next['hour'] = 0
            else:
                next['hour'] = now.hour
        else:
            next['hour'] = self.hour
        if self.day == '??':
            if next['hour'] < now.hour or next['hour'] == now.hour and next['minute'] < now.minute:
                next['day'] = now.day + 1
                if next['day'] > monthrange(now.year, now.month)[1]:
                    next['day'] = 1
                    extramonth = True
            else:
                next['day'] = now.day
        else:
            next['day'] = self.day
        if extramonth:
            next['month'] = now.month +1
            if next['month'] == 13:
                next['month'] = 1
                next['year'] = now.year +1
        next = '{}-{}-{} {}:{}:{}'.format(next['year'], next['month'], next['day'], next['hour'], next['minute'], next['second'])
        self.as_date = datetime.datetime.strptime(next, "%Y-%m-%d %H:%M:%S")

    def t_left(self):
        '''Returns time in seconds between WittyTime and system time.'''
        if self.as_date == 'unset':
            return "{} is unset.".format(self.name)
        return self.as_date - datetime.datetime.now()

    def __str__(self):
        if self.name in ['boot', 'shutdown']:
            return "Next {} at {}".format(self.name, self.as_date)
        else:
            return "WittyTime: {}".format(self.as_date)


    def __repr__(self):
        return "WittyTime(type={}, day={}, hour={}, minute={}, second={}, as_date={})".format(self.name, self.day, self.hour, self.minute, self.second, self.as_date)
