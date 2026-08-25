from addonHandler import getAvailableAddons as getAddon

addon = next(getAddon(filterFunc=lambda addon: addon.name == "subtitle_reader_fork"), None)
version = addon.version
