def quick_sort_simple(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quick_sort_simple(left) + [pivot] + quick_sort_simple(right)

# Example Usage:
my_list = [3, 6, 8, 10, 1, 2, 1]
sorted_list = quick_sort_simple(my_list)
print(f"Original list: {my_list}")
print(f"Sorted list: {sorted_list}")
