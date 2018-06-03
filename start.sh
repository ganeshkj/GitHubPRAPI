#!/bin/sh
if [ $(id -u) -ne 0 ]
  then echo "Current User is $(id -u). Please run the script as root"
  exit
fi

if [ $# -eq 0 ]; then
    echo "run script with ./start.sh start|reload|stop"
    exit
fi

mkdir -p /var/run/uwsgi/
mkdir -p /var/log/uwsgi/

echo "Running GitHubPRAPI at /var/www/GitHubPRAPI/"
echo "Log File at /var/log/uwsgi/GitHubPRAPI.log"


case $1 in

    start)
        /usr/local/bin/uwsgi --ini GitHubPRAPI.ini
        if [ $? -eq 0 ];then
           echo "Server Started"
        else
           echo "Unable to start server"
        fi
        ;;
    reload)
        touch /var/www/GitHubPRAPI/reload
        if [ $? -eq 0 ];then
           echo "Server reStarted"
        else
           echo "Unable to restart server"
        fi
        ;;
    stop)
        /usr/local/bin/uwsgi --stop /var/run/uwsgi/GitHubPRAPI-master.pid
        if [ $? -eq 0 ];then
           echo "Server Stopped"
        else
           echo "Error stopping server"
        fi
        ;;

    *)
        echo "run script with ./start.sh start|reload|stop"
esac



