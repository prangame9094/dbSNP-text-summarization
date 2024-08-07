import subprocess
import pandas as pd

input_file = "input2.txt"
output_file = "output_file.xlsx"

# Initialize a list to hold the results
results = []

with open(input_file, 'r') as file:
    lines = file.readlines()

for line in lines:
    my_input = line.strip()

    if not my_input:
        continue

    efilter_option = ""
    command = f"esearch -db pubmed -query \"{my_input}\" | efilter {efilter_option} | efetch -format medline"

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

        if result.stderr:
            output_text = f"Error Output:\n{result.stderr}"
        else:
            output_text = result.stdout

        # Append the input and output to the results list
        results.append({'Input': my_input, 'Information': output_text})

        print(f"Output for query '{my_input}' has been processed.")

    except subprocess.CalledProcessError as e:
        error_message = f"An error occurred while executing the command for query '{my_input}': {e}"
        results.append({'Input': my_input, 'Information': error_message})
        print(error_message)

# Convert the results list to a DataFrame
df = pd.DataFrame(results)

# Save the DataFrame to an Excel file
df.to_excel(output_file, index=False)

print(f"Results have been saved to '{output_file}'.")
