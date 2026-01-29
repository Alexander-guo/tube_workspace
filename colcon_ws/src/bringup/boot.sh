#!/bin/bash


source /opt/ros/jazzy/setup.bash
source /home/afrl/tube_workspace/colcon_ws/install/setup.bash


## commenting out sonar launch for now
# bash /home/afrl/tube_workspace/companion/scripts/start_sonar_3d.sh &

ros2 launch bringup bringup.launch.py &
BRINGUP_PID=$!
ros2 launch bringup logger.launch.py &
LOGGER_PID=$!

cleanup() {
	kill -INT "$BRINGUP_PID" "$LOGGER_PID" 2>/dev/null
	for _ in {1..10}; do
		if ! kill -0 "$BRINGUP_PID" 2>/dev/null && ! kill -0 "$LOGGER_PID" 2>/dev/null; then
			return
		fi
		sleep 1
	done
	kill -TERM "$BRINGUP_PID" "$LOGGER_PID" 2>/dev/null
	for _ in {1..5}; do
		if ! kill -0 "$BRINGUP_PID" 2>/dev/null && ! kill -0 "$LOGGER_PID" 2>/dev/null; then
			return
		fi
		sleep 1
	done
	kill -KILL "$BRINGUP_PID" "$LOGGER_PID" 2>/dev/null
}

trap cleanup INT TERM

wait "$BRINGUP_PID" "$LOGGER_PID"

