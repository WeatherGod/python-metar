#
#  Python classes to represent dimensioned quantities used in weather reports
#
#  Copyright 2004  Tom Pollard
# 
import re

## exceptions

class UnitsError(Exception):
  """Exception raised when unrecognized units are used."""
  pass

## regexp to match fractions (used by distance class)

FRACTION_RE = re.compile(r"^((?P<int>\d+)\s+)?(?P<num>\d+)/(?P<den>\d+)$")
  
## classes representing dimensioned values in METAR reports
    
class temperature:
  """A class representing a temperature value."""
  legal_units = [ "F", "C", "K" ]
  
  def __init__( self, value, units="C" ):
    if not units.upper() in temperature.legal_units:
      raise UnitsError("unknown temperature unit: "+units)
    self._units = units.upper()
    try:
      self._value = float(value)
    except ValueError:
      if value.startswith('M'):
        self._value = -float(value[1:])
    
  def value( self, units=None ):
    """Return the temperature in the specified units."""
    if units == None:
      return self._value
    else:
      if not units.upper() in temperature.legal_units:
        raise UnitsError("unknown temperature unit: "+units)
      units = units.upper()
    if self._units == "C":
      celsius_value = self._value
    elif self._units == "F":
      celsius_value = (self._value-32.0)/1.8
    elif self._units == "K":
      celsius_value = self._value-273.15
    if units == "C":
        return celsius_value
    elif units == "K":
        return 273.15+celsius_value
    elif units == "F":
      return 32.0+celsius_value*1.8
      
  def string( self, units=None ):
    """Return a string representation of the temperature, using the given units."""
    if units == None:
      units = self._units
    else:
      if not units.upper() in temperature.legal_units:
        raise UnitsError("unknown temperature unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "C":
      return "%.1f C" % val
    elif units == "F":
      return "%.1f F" % val
    elif units == "K":
      return "%.1f K" % val

class pressure:
  """A class representing a barometric pressure value."""
  legal_units = [ "MB", "HPA", "IN" ]
  
  def __init__( self, value, units="MB" ):
    if not units.upper() in pressure.legal_units:
      raise UnitsError("unknown pressure unit: "+units)
    self._value = float(value)
    self._units = units.upper()
    
  def value( self, units=None ):
    """Return the pressure in the specified units."""
    if units == None:
      return self._value
    else:
      if not units.upper() in pressure.legal_units:
        raise UnitsError("unknown pressure unit: "+units)
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "IN":
      mb_value = self._value*33.86398
    else:
      mb_value = self._value
    if units == "MB" or units == "HPA":
      return mb_value
    elif units == "IN":
        return mb_value/33.86398
    else:
      raise UnitsError("unknown pressure unit: "+units)
      
  def string( self, units=None ):
    """Return a string representation of the pressure, using the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in pressure.legal_units:
        raise UnitsError("unknown pressure unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "MB":
      return "%.1f mb" % val
    elif units == "HPA":
      return "%.1f hPa" % val
    elif units == "IN":
      return "%.2f inches" % val

class speed:
  """A class representing a wind speed value."""
  legal_units = [ "KT", "MPS", "KMH", "MPH" ]
  legal_gtlt = [ ">", "<" ]
  
  def __init__( self, value, units=None, gtlt=None ):
    if not units:
      self._units = "MPS"
    else:
      if not units.upper() in speed.legal_units:
        raise UnitsError("unknown speed unit: "+units)
      self._units = units.upper()
    if gtlt and not gtlt in speed.legal_gtlt:
      raise ValueError("unrecognized gtlt value: "+gtlt)
    self._gtlt = gtlt
    self._value = float(value)
    
  def value( self, units=None ):
    """Return the pressure in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in speed.legal_units:
        raise UnitsError("unknown speed unit: "+units)
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "KMH":
      mps_value = self._units/3.6
    elif self._units == "KT":
      mps_value = self._value*0.514444
    elif self._units == "MPH":
      mbs_value = self._value*0.447000
    else:
      mps_value = self._value
    if units == "KMH":
      return mps_value*3.6
    elif units == "KT":
      return mps_value/0.514444
    elif units == "MPH":
      return mps_value/0.447000
    elif units == "MPS":
      return mps_value
      
  def string( self, units=None ):
    """Return a string representation of the speed in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in speed.legal_units:
        raise UnitsError("unknown speed unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "KMH":
      text = "%.0f km/h" % val
    elif units == "KT":
      text = "%.0f knots" % val
    elif units == "MPH":
      text = "%.0f mph" % val
    elif units == "MPS":
      text = "%.1f mps" % val
    if self._gtlt == ">":
      text = "greater than "+text
    elif self._gtlt == "<":
      text = "less than "+text
    return text

class distance:
  """A class representing a distance value."""
  legal_units = [ "SM", "MI", "M", "KM", "FT" ]
  legal_gtlt = [ ">", "<" ]
  
  def __init__( self, value, units=None, gtlt=None ):
    if not units:
      self._units = "M"
    else:
      if not units.upper() in distance.legal_units:
        raise UnitsError("unknown distance unit: "+units)
      self._units = units.upper()
    
    try:
      if value.startswith('M'):
        value = value[1:]
        gtlt = "<"
      elif value.startswith('P'):
        value = value[1:]
        gtlt = ">"
    except:
      pass
    if gtlt and not gtlt in distance.legal_gtlt:
      raise ValueError("unrecognized gtlt value: "+gtlt)
    self._gtlt = gtlt
    try:
      self._value = float(value)
      self._num = None
      self._den = None
    except ValueError:
      mf = FRACTION_RE.match(value)
      if not mf:
        raise ValueError("not parseable as a number: "+value)
      df = mf.groupdict()
      self._num = int(df['num'])
      self._den = int(df['den'])
      self._value = float(self._num)/float(self._den)
      if df['int']:
        self._value += float(df['int'])
    
  def value( self, units=None ):
    """Return the distance in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in distance.legal_units:
        raise UnitsError("unknown distance unit: "+units)
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "SM" or self._units == "MI":
      m_value = self._value*1609.344
    elif self._units == "FT":
      m_value = self._value/3.28084
    elif self._units == "KM":
      m_value = self._value*1000
    else:
      m_value = self._value
    if units == "SM" or units == "MI":
      return m_value/1609.344
    elif units == "FT":
      return m_value*3.28084
    elif units == "KM":
      return m_value/1000
    elif units == "M":
      return m_value
      
  def string( self, units=None ):
    """Return a string representation of the distance in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in distance.legal_units:
        raise UnitsError("unknown distance unit: "+units)
      units = units.upper()
    if self._num and self._den and units == self._units:
      val = int(self._value - self._num/self._den)
      if val:
        text = "%d %d/%d" % (val, self._num, self._den)
      else:
        text = "%d/%d" % (self._num, self._den)
    else:
      if units == "KM":
        text = "%.1f" % self.value(units)
      else:
        text = "%.0f" % self.value(units)
    if units == "SM" or units == "MI":
      text += " miles"
    elif units == "M":
      text += " meters"
    elif units == "KM":
      text += " km"
    elif units == "FT":
      text += " feet"
    if self._gtlt == ">":
      text = "greater than "+text
    elif self._gtlt == "<":
      text = "less than "+text
    return text


class direction:
  """A class representing a compass direction."""
  
  compass_dirs = { "N":  0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5, 
                   "E": 90.0, "ESE":112.5, "SE":135.0, "SSE":157.5,
                   "S":180.0, "SSW":202.5, "SW":225.0, "WSW":247.5,
                   "W":270.0, "WNW":292.5, "NW":315.0, "NNW":337.5 }

  def __init__( self, d ):
    if direction.compass_dirs.has_key(d):
      self._compass = d
      self._degrees = direction.compass_dirs[d]
    else:
      self._compass = None
      value = float(d)
      if value < 0.0 or value > 360.0:
        raise ValueError
      self._degrees = value
      
  def value( self ):
    """Return the numerical direction, in degrees."""
    return self._degrees
    
  def string( self ):
    """Return a string representation of the numerical direction."""
    return "%.0f degrees" % self._degrees
    
  def compass( self ):
    """Return the compass direction, e.g., "N", "ESE", etc.)."""
    if not self._compass:
      degrees = 22.5 * round(self._degrees/22.5)
      if degrees == 360.0:
        self._compass = "N"
      else:
        for name, d in direction.compass_dirs.iteritems():
          if d == degrees:
            self._compass = name
            break
    return self._compass

