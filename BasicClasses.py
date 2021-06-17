class Object(object):

  def abort(self):
    exit()

  def type_name(self):
    return Stringg(str(self.__class__))

  def copy(self):
    return self.copy()

class Stringg(Object, str):

  def __new__(cls, content):
      return super().__new__(cls, content.strip('"').replace('\\n','\n'))

  def length(self):
    return Int(len(self))

  def concat(self, s):

    return Stringg(self + s)

  def substr(self, i, l):
    return Stringg(self[i:i+l])

class IO(Object):

  def out_string(self, x):
    print(x, end='')

  def out_int(self, x):
    print(x, end='')

  def in_string(self):
    return Stringg(input())

  def in_int(self):
    return Int(int(input()))

class Int(Object, int):
  pass

class Bool(Object, int):
  pass