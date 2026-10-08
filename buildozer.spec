[app]
title = Black Horse
package.name = blackhorse
package.domain = org.blackhorse
source.dir = .
source.include_exts = py,db
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
