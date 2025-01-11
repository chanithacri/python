from multiprocessing import Process, Queue

def sum_even_numbers(numbers, q):
   even_sum = sum(num for num in numbers if num % 2 == 0)
   q.put(even_sum)

def sum_odd_numbers(numbers, q):
   odd_sum = sum(num for num in numbers if num % 2 != 0)
   q.put(odd_sum)

def calculate_total_sum(numbers):
   q = Queue()
   even_process = Process(target=sum_even_numbers, args=(numbers, q))
   odd_process = Process(target=sum_odd_numbers, args=(numbers, q))
   
   even_process.start()
   odd_process.start()
   
   even_process.join()
   odd_process.join()
   
   even_sum = q.get()
   odd_sum = q.get()
   
   total_sum = even_sum + odd_sum
   print("Total sum is", total_sum)


if __name__ == "__main__":
   numbers = list(map(int, input().split()))
   calculate_total_sum(numbers)
