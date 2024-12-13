# TARS - Terminal Assistant with Gemini

This Python script, `tars.py`, is a terminal assistant that uses the Gemini API to interpret user commands and execute them in a Linux environment. It provides a limited set of allowed commands for safety and control.

## How to Use

1.  **Set the API Key:**
    Before running the script, you need to set the `GEMINI_API_KEY` environment variable with your Gemini API key. You can do this by running the following command in your terminal:
    ```bash
    export GEMINI_API_KEY="your_gemini_api_key"
    ```
    Replace `"your_gemini_api_key"` with your actual Gemini API key.

2.  **Run the Script:**
    Execute the script using the following command:
    ```bash
    ./tars.py
    ```

3.  **Interact with the Assistant:**
    The script will prompt you with `>`. You can then enter Linux commands, and the assistant will execute them using the `execute_command` function.

4.  **Exit the Assistant:**
    Type `exit` to close the assistant.

## Allowed Commands

The following Linux commands are allowed:

-   `ls`: List directory contents
-   `cd`: Change directory (only to `/home/rp/Desktop` or `/home/rp/Documents`)
-   `pwd`: Print working directory
-   `cp`: Copy files or directories
-   `mv`: Move files or directories
-   `rm`: Remove files or directories
-   `mkdir`: Create directories
-   `find`: Search for files in a directory
-   `grep`: Search for patterns in files
-   `df`: Display disk space usage
-   `du`: Display file space usage

## Important Notes

-   The assistant uses the `gemini-2.0-flash-exp` model.
-   The assistant will always use the full path when navigating to `Desktop` or `Documents`.
-   The assistant will not explain the commands, it will execute them directly.
-   The `ls` command will use `-la` when you want to show details.
-   The assistant uses the current directory (`.`) if no path is specified.

## Libraries Used

-   `os`: Used for interacting with the operating system, specifically for accessing environment variables.
-   `google.generativeai`: The core library for interacting with the Gemini API.
-   `subprocess`: Used for executing Linux commands.
-   `json`: Used for handling JSON data when interacting with the Gemini API's tool calling feature.

## Tool Calling

The script uses the Gemini API's tool calling feature to execute Linux commands. The `process_input` function defines a function declaration for `execute_command` which specifies the parameters that the Gemini model can use. When the model determines that a command needs to be executed, it will return a function call with the appropriate parameters. The `process_input` function then extracts these parameters and calls the `execute_command` function to execute the command.

## Code Structure

-   `execute_command(command, flags=None, args=None, requires_sudo=False)`: Executes a given Linux command with optional flags and arguments.
-   `process_input(user_input)`: Processes the user input using the Gemini API and executes the command if a valid command is detected.
-   `main()`: The main function that starts the assistant and handles user input.
