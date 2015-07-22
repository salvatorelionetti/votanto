python votanto.py &
pkill blueman-applet
pkill tail
echo -n > blueagent.log
tail -f blueagent.log &
sudo nohup python -u blueagent4.py > blueagent.log
