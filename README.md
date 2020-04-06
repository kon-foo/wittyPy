# wittyPy
#### A Python Wrapper for the [WittyPi 2](http://www.uugear.com/product/wittypi2/) Realtime Clock for the RaspberryPi.

## Example
```python
   import wittyPy

   witty = wittyPy.WittyPi('path/to/wittyPi/Software')

   print(witty.next_start)
   witty.set_startup(10,9,8,7)
   print(witty.next_start)
   witty.reset('startup')
   print(witty.next_start)
```
Output:
```
   >>> WittyTime(type="boot", day="unset", hour="unset", minute="unset", second="unset", as_date="unset")
   >>> WittyTime(type="boot", day=10, hour=9, minute=8, second=7, as_date="2018-08-10 09:08:07")
   >>> WittyTime(type="boot", day="unset", hour="unset", minute="unset", second="unset", as_date="unset")
```

## Installation

To install wittyPy, simply use pip:
```
   pip install wittyPy
```

## Documentation

You can find the documentation on [docs.elpunkt.eu](http://docs.elpunkt.eu/wittyPy/).


## How to contribute:
1. Test wittyPy and open an issue to report a bug or discuss a feature idea.
2. Give general feedback on the code and the package structure.
3. Fork the repository and make your changes.


