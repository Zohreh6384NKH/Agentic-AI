import re
import json

# Step 1: Define the function to calculate the square of a number
def calculate_square(number):
    """
    A simple function that returns the square of a number.
    """
    return number * number

# Step 2: Function to parse the AI's response for function calls
def parse_function_call(response_content):
    """
    Extract function call and arguments from Llama3's response using regex.
    """
    function_pattern = r"<function=(\w+)>(.*?)</function>"
    match = re.search(function_pattern, response_content)
    if match:
        function_name = match.group(1)
        arguments = json.loads(match.group(2))
        return function_name, arguments
    return None, None

# Simulated response from Llama3
response_content = "<function=calculate_square>{\"number\": \"5\"}</function>"

# Step 3: Parse the response
function_name, arguments = parse_function_call(response_content)

# Step 4: Check if the function name matches and call the function
if function_name == "calculate_square":
    # Extract the argument "number" and convert it to an integer
    number = int(arguments.get("number"))
    # Call the calculate_square function with the extracted argument
    result = calculate_square(number)
    print(f"Function Output: {result}")  # Output the result of the function
else:
    print("Llama's Response:", response_content)