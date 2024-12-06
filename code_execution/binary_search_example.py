# filename: binary_search_example.py

def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        guess = arr[mid]

        if guess == target:
            return mid
        elif guess > target:
            high = mid - 1
        else:
            low = mid + 1
            
    return None  # Target is not in the list


# Example usage
if __name__ == "__main__":
    sorted_list = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    target = 7

    result = binary_search(sorted_list, target)

    if result is not None:
        print(f"Target {target} found at index {result}.")
    else:
        print(f"Target {target} not found in the list.")