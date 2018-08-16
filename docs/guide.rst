.. currentmodule:: wittyPy

*****
Guide
*****

Before using wittyPy, make sure your Witty-Pi and the according software works propperly on your Raspberry Pi.

Initialising
************

To use the wittyPy functionality, you first have to instatiate wittyPy and connect it to your wittyPi. As the only argument it takes the path to your wittyPi software directory::

   import wittyPy
   witty = wittyPy.WittyPi('/home/user/wittyPi')

Current State
=============

After instatiating, :class:`WittyPi` searches for the required files and reads the current state of your Witty-Pi. You can access them using::

   print(witty.next_startup)
   print(witty.next_shutdown)
   print(witty.available_schedules)
   print(witty.timedelta)


* ``witty.next_startup`` and ``witty.next_shutdown`` are :class:`WittyTime` objects and store the next scheduled boot/shutdown. 
* ``witty.available_schedules```is a list of the schedules in your ``../wittyPi/schedules`` folder. 
* ``witty.timedelta`` is the difference in seconds between your system time and your RTC time.

Set Startup or Shutdown
***********************

To set a startup or shutdown, run :meth:`wittyPy.set_startup` or :meth:`wittyPy.set_shutdown`. The startup methods takes up to four arguments (day, hour, minute, second) and the shutdown method three (day, hour, minute). Running these functions will create a :class:`WittyTime`. This includes a validation of the argzuments. Use integers (day: 1-31; hour: 0-23; minute & second: 0-59). For day and hour you can also use ``"??"`` as a wildcard. If you set a wildcard for the hour, the Witty Pi expects that you also set a wildcard for the day::

   witty.set_startup('??', 10, 30)
   witty.set_shutdown(11, 12, 13)

Set Schedule
************

To activate a schedule use :meth:`wittyPy.activate_schedule`. This method expects the index of the desired schedule in the ``witty.available_schedules`` list::

   witty.activate_schedule(1)

To reset startup, shutdown or schedule, simply overwrite it with a new one, or use the :meth:`wittyPy.reset` method. This method takes ``"startup"``,``"shutdown"``,``"schedule"`` or ``"all"`` as an option::

   witty.reset("all")

Check time left
***************

To check the time left until next startup or shutdown, use the :meth:`wittyTime.t_left` method::

   witty.next_startup.t_left()



