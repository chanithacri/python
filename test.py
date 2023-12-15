from multiprocessing import Process
import os

def calculate_square(numbers):
    print(f"Square process PID: {os.getpid()}")
    result = 0
    for n in numbers:
        result += n * n
    print(f"Sum of squares: {result}")

def calculate_cube(numbers):
    print(f"Cube process PID: {os.getpid()}")
    result = 0
    for n in numbers:
        result += n * n * n
    print(f"Sum of cubes: {result}")

if __name__ == "__main__":
    numbers = [1, 2, 3, 4]
    
    # Create two processes
    p1 = Process(target=calculate_square, args=(numbers,))
    p2 = Process(target=calculate_cube, args=(numbers,))
    
    # Start the processes
    p1.start()
    p2.start()
    
    # Wait for both processes to finish
    p1.join()
    p2.join()
    
    print(f"Main program PID: {os.getpid()}")
