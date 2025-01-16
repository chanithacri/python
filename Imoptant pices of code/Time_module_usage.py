import time  # Import the liprary
time_stmp = time.time()  # Not readable by us
print(time.ctime(time_stmp))  # Convert it to a readable format
# Note: If runnning on a sever the time will be the time in the sever
print(time.localtime(time_stmp))  # local time in time stamp format 
print(time.gmtime(time_stmp))  # UTC time in time stamp format 

local_time = time.localtime()  # Get local time
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)  # Convertion 
print("Formatted Time:", formatted_time)  # Print the formatted time 
