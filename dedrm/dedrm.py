import os, time, sys
from k4mobidedrm import decryptBook

# while 1:
#   time.sleep(1)
#   devices = os.listdir ("/dev/disk/by-id")
#   for device in devices:
#   	if "Kindle" in device and "part1" in device:
#   		kindlePath = "/dev/disk/by-id/" + device
#   		break
#   if kindlePath:
#   	break

# print "FOUND KINDLE"
# print kindlePath

import gobject
import udiskie.automount
import udiskie.daemon
import udiskie.mount
import udiskie.prompt
import udiskie.udisks

def freeBooks(kindle, storage):
  print "Free BOOKS!"
  serial = raw_input("Kindle Serial Number: ") #B02415022487114Q
  kindle_path = kindle.mount_paths[0]
  storage_path = storage.mount_paths[0]
  path_to_freedom = storage_path+"/freed_books"
  books = os.listdir (kindle_path+"/documents")
  try:
    os.mkdir(path_to_freedom)
  except OSError:
    pass
  for book in books:
    if book.endswith(".azw3") or book.endswith(".mobi"):
      print book
      decryptBook(kindle_path+"/documents/"+book, path_to_freedom, [], [serial], [])
      # fetch DrmException
  storage.unmount()

  

class MountListener(object):
  def __init__(self):
    self.kindle = None
    self.storage = None
    pass

  def device_mounted(self, device):
    device_file = device.device_presentation
    print "device mounted"
    print device_file
    for idName in device.property.DeviceFileById:
      if "/dev/disk/by-id/" in idName:
        if "Kindle" in idName:
          print "ITS A KINDLE"
          self.kindle = device
        else:
          print "ITS NOT A KINDLE"
          self.storage = device
    if self.kindle is not None and self.storage is not None:
      freeBooks(self.kindle, self.storage)
    else:
      print "not enough devices"

  def device_removed(self, device):
    if str(device) == str(self.kindle):
      print "IT WAS A KINDLE"
      self.kindle = None
    elif str(device) == str(self.storage):
      print "IT WAS STORAGE"
      self.storage = None

# for now: just use the default udisks
import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
udisks = udiskie.udisks.Udisks.create(bus)

# create daemon
daemon = udiskie.daemon.Daemon(udisks=udisks)
mainloop = gobject.MainLoop()

# create a mounter

mounter = udiskie.mount.Mounter(udisks=udisks)

# automounter
automount = udiskie.automount.AutoMounter(mounter)
listener = MountListener()
import udiskie.notify
try:
    import notify2 as notify_service
except ImportError:
    import pynotify as notify_service
notify_service.init('udiskie.mount')
notify = udiskie.notify.Notify(notify_service)
daemon.connect(notify)
daemon.connect(automount)
daemon.connect(listener)



#mounter.mount_all()
try:
  mainloop.run()
except KeyboardInterrupt:
  sys.exit()


#decryptBook("../The Atrocity Archives (A LAUNDRY FILES NOVEL)_B000OIZUIA.azw3", "..", [], ["B02415022487114Q"], [])