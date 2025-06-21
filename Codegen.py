import re
from ai import call_gpt

def clean_html_input(raw_html):
    # Remove <script>...</script> tags
    cleaned = re.sub(r'<script.*?>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)

    # Remove <link ...> tags
    cleaned = re.sub(r'<link[^>]*?>', '', cleaned, flags=re.IGNORECASE)

    # Remove <style> blocks with @import or external refs
    def style_filter(match):
        content = match.group(0)
        return '' if '@import' in content else content
    cleaned = re.sub(r'<style.*?>.*?</style>', style_filter, cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Remove inline JS attributes like onclick, onload, etc.
    cleaned = re.sub(r'\son\w+="[^"]*"', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\son\w+='[^']*'", '', cleaned, flags=re.IGNORECASE)

    return cleaned.strip()

def save_user_input_to_file():
    print("Paste your homepage HTML/CSS/JS code below.\nType `END` on a new line when finished:")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    full_code = "\n".join(lines)

    # Clean the HTML/CSS and remove JS/unwanted links
    cleaned_code = clean_html_input(full_code)

    # Save cleaned code to input.txt
    with open("input.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_code)

    return cleaned_code

def main():
    # Step 1: Get and clean user input
    reference_code = save_user_input_to_file()

    # Step 2: Construct the prompt
    prompt = (
        "Analyze the following homepage code and generate a new chatbot interface "
        "that visually matches its style, color theme, and layout aesthetics. "
        "Include chat bubbles, an input field, and a send button. Use clean, modern code "
        "practices with HTML, CSS, or React + TailwindCSS.\n\n"
        "Format the output exactly like this:\n```html\n<!-- Your code here -->\n```\n\n"
        f"Reference Code:\n```html\n{reference_code}\n```"
    )

    # Step 3: Get GPT response
    response = call_gpt(prompt)

    # Step 4: Print and save the result
    print("\nGenerated Chatbot UI Code:\n")
    print(response)

    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(response)

    # Step 5: Clear input.txt
    with open("input.txt", "w", encoding="utf-8") as file:
        file.write("")

if __name__ == "__main__":
    main()
