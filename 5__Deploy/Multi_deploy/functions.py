
def get_line(file_name_, line_number):
    try:
        with open(file_name_, 'r') as f:
            for current_line, content in enumerate(f, start=1):
                if current_line == line_number:
                    return content.strip()
        # If the function hasn't returned yet, the line was not found
        print(f"Line {line_number} not found.")
        return None
    except OSError as e:  # handle file-related exceptions
        # print_plus(f"OS error: {e}", False, f'{file_name}_output.txt', True)
        print(f"OS error: {e}")
        return None
    