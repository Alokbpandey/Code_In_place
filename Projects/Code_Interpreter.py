from ai import call_gpt

def main():
    print("=== Enhanced Python Code Explainer ===")
    print("Paste your Python code (you can paste all at once, keep indentation if possible).")
    print("Type END on a new line to finish:\n")

    code_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        # attempt to split on semicolon (;) or comment blocks if needed
        if ";" in line:
            split_lines = line.split(";")
            code_lines.extend([s.strip() for s in split_lines if s.strip()])
        else:
            code_lines.append(line)

    code = "\n".join(code_lines)

    print("\n📄 Your code:\n")
    print(code)

    print("\n🔍 General Explanation of the Code:\n")
    general_explanation = call_gpt(f"Explain this Python code:\n{code}")
    print(f"👉 {general_explanation}\n")

    print("🔎 Line-by-Line Explanation:\n")
    for i in range(len(code_lines)):
        line = code_lines[i]
        if line.strip() != "":
            print(f"🔹 Line {i+1}: {line}")
            line_explanation = call_gpt(f"Explain this line of Python code: {line}")
            print(f"👉 {line_explanation}")
        print()

    print("🛠️ Checking for possible issues or improvements:\n")
    suggestions = call_gpt(f"Analyze this code and suggest improvements or point out any issues:\n{code}")
    print(f"👉 {suggestions}")

    print("\n✅ Done.")

if __name__ == '__main__':
    main()
