#!/bin/bash

case "$SSH_ORIGINAL_COMMAND" in
    "pictures")
        cd /home/aiy/Pictures/Booth/
        rsync -avP --remove-source-files pi@192.168.0.248:/home/pi/aiy/Pictures/ ./
        killall eog
        killall totem
        fname="$(ls | tail -n 1)"
        DISPLAY=:0 busctl --user set-property org.gnome.Mutter.DisplayConfig /org/gnome/Mutter/DisplayConfig org.gnome.Mutter.DisplayConfig PowerSaveMode i 0
        DISPLAY=:0 gnome-screensaver-command -d
        DISPLAY=:0 eog "$fname" > /dev/null 2>&1 &
        ;;
    "videos")
        cd /home/aiy/Videos/Booth 
        rsync -avP --remove-source-files pi@192.168.0.248:/home/pi/aiy/Videos/ ./
        killall eog
        killall totem
        fname="$(ls | tail -n 1)"
        ffmpeg -i "$fname" -vcodec copy -an "${fname%.*}.mp4" -y && rm "$fname"
        DISPLAY=:0 busctl --user set-property org.gnome.Mutter.DisplayConfig /org/gnome/Mutter/DisplayConfig org.gnome.Mutter.DisplayConfig PowerSaveMode i 0
        DISPLAY=:0 gnome-screensaver-command -d
        DISPLAY=:0 totem "${fname%.*}.mp4" > /dev/null 2>&1 &
        ;;
    *)
        echo "no!"
        exit 1
        ;;
esac
