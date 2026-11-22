[app]

title = BP Tracker
package.name = bptracker
package.domain = org.workineh

source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = develop
[buildozer]

log_level = 2
warn_on_root = 1
