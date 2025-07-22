import os
import datetime
from ai import call_gpt  # You must implement this function

# === Utilities ===

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

def ensure_dirs():
    os.makedirs("contexts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def save_file(content: str, folder: str, prefix: str, extension: str = "html") -> str:
    ensure_dirs()
    timestamp = get_timestamp()
    filepath = os.path.join(folder, f"{prefix}_{timestamp}.{extension}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

def log_event(message: str):
    ensure_dirs()
    log_file = os.path.join("logs", f"log_{datetime.date.today()}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{get_timestamp()}] {message}\n")

# === User Input ===

def get_user_context():
    print("🔷 What type of website would you like to generate? (e.g., blog, e-commerce, portfolio):")
    site_type = input("Website type: ").strip()
    return site_type or "general"

# === Agent 1: Planner ===

def planner_agent(site_type: str) -> str:
    prompt = (
        f"You are a UI Planner Agent. The user wants to build a **{site_type}** website from scratch.\n\n"
        "Create a planning document in Markdown format. Include:\n"
        "1. Suggested Page Layout\n"
        "2. Key UI Components (navbar, hero, chatbox, footer, etc.)\n"
        "3. Theme and Color Palette\n"
        "4. Technology Stack (e.g., HTML/CSS, or React + TailwindCSS)\n"
        "5. Where a chatbot interface should be placed (floating, fixed, embedded?)"
    )
    log_event("Planner Agent: Creating website and chatbot layout plan")
    return call_gpt(prompt)

# === Agent 2: Coder ===

def coder_agent(plan: str) -> str:
    prompt = (
        "You are a Coder Agent. Based on the following plan, generate a complete homepage code "
        "with a chatbot interface. Include a chatbot UI (chat window, input box, send button).\n\n"
        "Use the recommended technologies (e.g., HTML/CSS or React + TailwindCSS).\n\n"
        f"Plan:\n{plan}\n\n"
        "Output only code inside:\n```html\n<!-- code here -->\n```"
    )
    log_event("Coder Agent: Generating code from planning document")
    return call_gpt(prompt)

# === Agent 3: Debugger ===

def debugger_agent(code: str) -> str:
    prompt = (
        "You are a Debugger Agent. Review the following chatbot website code. "
        "Fix any bugs, improve formatting, and ensure it's clean and modern. "
        "Don't change design intention. Return ONLY the cleaned-up code inside:\n\n"
        "```html\n<!-- code here -->\n```\n\n"
        f"{code}"
    )
    log_event("Debugger Agent: Cleaning and fixing code")
    return call_gpt(prompt)

# === Main Orchestrator ===

def main():
    ensure_dirs()

    # Step 1: Get user site type
    site_type = get_user_context()
    log_event(f"User request: Generate {site_type} website with chatbot")

    # Step 2: Planning
    try:
        plan = planner_agent(site_type)
        plan_path = save_file(plan, "outputs", "planner_notes", "md")
        print("\n🧠 Planner Agent Output:\n")
        print(plan)
        log_event(f"Planner notes saved → {plan_path}")
    except Exception as e:
        log_event(f"ERROR: Planner Agent failed: {str(e)}")
        return

    # Step 3: Code Generation
    try:
        generated_code = coder_agent(plan)
        code_path = save_file(generated_code, "outputs", "raw_code")
        print("\n💻 Coder Agent Output:\n")
        print(generated_code)
        log_event(f"Raw code saved → {code_path}")
    except Exception as e:
        log_event(f"ERROR: Coder Agent failed: {str(e)}")
        return

    # Step 4: Debugging
    try:
        debugged_code = debugger_agent(generated_code)
        final_path = save_file(debugged_code, "outputs", "final_debugged_code")
        print("\n🛠️ Debugger Agent Output:\n")
        print(debugged_code)
        log_event(f"Final debugged code saved → {final_path}")
    except Exception as e:
        log_event(f"ERROR: Debugger Agent failed: {str(e)}")

if __name__ == "__main__":
    main()
