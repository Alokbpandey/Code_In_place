from ai import call_gpt

# coordinate_utils.py


AI_MODES = ["reflective", "creative", "critical", "skeptical", "pragmatic", "visionary"]
REASONING_MODALITIES = ["deductive", "inductive", "abductive", "analogical", "causal", "statistical"]

def main():
    print("Available AI Modes:", ", ".join(AI_MODES))
    ai_mode = input("Choose AI mode: ").strip().lower()
    if ai_mode not in AI_MODES:
        ai_mode = "reflective"
    print("Available Reasoning Modalities:", ", ".join(REASONING_MODALITIES))
    reasoning_modality = input("Choose reasoning modality: ").strip().lower()
    if reasoning_modality not in REASONING_MODALITIES:
        reasoning_modality = "deductive"
    user_prompt = input("Drop your main query here: ")
    multi_step = input("Enable multi-step reasoning? (y/n): ").strip().lower() == "y"
    show_summary = input("Show summary at each step? (y/n): ").strip().lower() == "y"
    think_aloud = input("Enable think-aloud mode? (y/n): ").strip().lower() == "y"
    self_prompting = input("Enable self-prompting? (y/n): ").strip().lower() == "y"
    depth = input("How many reasoning depths? (default 3): ").strip()
    try:
        depth = int(depth)
    except:
        depth = 3
    deep_thought_loop(
        user_prompt, ai_mode, reasoning_modality, depth=depth,
        multi_step=multi_step, show_summary=show_summary, think_aloud=think_aloud,
        self_prompting=self_prompting
    )

def deep_thought_loop(problem, ai_mode, reasoning_modality, depth=3, multi_step=False, show_summary=False, think_aloud=False, self_prompting=False):
    history = []
    for i in range(depth):
        print(f"\n====== DEPTH {i + 1} ======")
        print(f"AI Mode: {ai_mode} | Reasoning: {reasoning_modality}")

        sub_topics = task_what(problem, ai_mode, reasoning_modality, multi_step, think_aloud)
        reflections = task_introspect_each(problem, sub_topics, ai_mode, reasoning_modality, multi_step, think_aloud)
        best_topic = decide_best_topic(reflections, sub_topics, ai_mode, reasoning_modality, multi_step, think_aloud)

        why = task_why(best_topic, ai_mode, reasoning_modality, multi_step, think_aloud)
        how = task_how(why, ai_mode, reasoning_modality, multi_step, think_aloud)
        risks = task_risks(best_topic, ai_mode, reasoning_modality, multi_step, think_aloud)
        alternatives = task_alternatives(best_topic, ai_mode, reasoning_modality, multi_step, think_aloud)

        solution = generate_solution(
            best_topic, sub_topics, why, how, ai_mode, reasoning_modality, multi_step, risks, alternatives, think_aloud
        )

        history.append({
            "depth": i + 1,
            "topic": best_topic,
            "why": why,
            "how": how,
            "risks": risks,
            "alternatives": alternatives,
            "solution": solution
        })

        if show_summary:
            print("\n📋 SUMMARY:")
            print(f"Topic: {best_topic}\nWhy: {why}\nHow: {how}\nRisks: {risks}\nAlternatives: {alternatives}\n")

        if self_prompting:
            problem = generate_next_problem(best_topic, why, how, ai_mode, reasoning_modality, multi_step, think_aloud)
        else:
            problem = input("\nEnter the next problem to explore (or press Enter to stop): ").strip()
            if not problem:
                break

    print("\n=== FULL HISTORY ===")
    for entry in history:
        print(f"\n--- Depth {entry['depth']} ---")
        print(f"Topic: {entry['topic']}\nWhy: {entry['why']}\nHow: {entry['how']}\nRisks: {entry['risks']}\nAlternatives: {entry['alternatives']}\nSolution: {entry['solution']}")

def add_think_aloud(prompt, think_aloud):
    if think_aloud:
        prompt += "\nThink aloud step by step. Explain your reasoning at each step."
    return prompt

def task_what(problem, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Think about this user request:\n\"{problem}\"\n"
        f"Break it into 4–6 possible interpretations or sub-questions the user might want answered.\n"
        f"Keep each under 20 words. Use a numbered list."
    )
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🟨 WHAT:\n", response)
    return [
        line.split('.', 1)[-1].strip()
        for line in response.splitlines()
        if line.strip() and line[0].isdigit()
    ]

def task_introspect_each(user_problem, sub_topics, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    reflections = []
    for i, sub in enumerate(sub_topics):
        prompt = (
            f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
            f"The user asked: '{user_problem}'\n"
            f"Possible interpretation: '{sub}'\n\n"
            f"Step-by-step: What will happen if I answer this? What will the output look like? Would that satisfy user intent?\n"
            f"Answer thoughtfully."
        )
        if multi_step:
            prompt += "\nReason step by step."
        prompt = add_think_aloud(prompt, think_aloud)
        result = call_gpt(prompt)
        print(f"\n🧠 INTROSPECT [{i + 1}]: {sub}\n{result}")
        reflections.append(result)
    return reflections

def decide_best_topic(reflections, sub_topics, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        "You are a self-aware AI. Based on the following introspections, choose the one that best matches what the user likely wants.\n\n"
    )
    for i, (topic, reflection) in enumerate(zip(sub_topics, reflections)):
        prompt += f"{i+1}. Topic: {topic}\nReflection: {reflection}\n\n"
    prompt += "Return only the number of the best topic."
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    try:
        index = int(response.strip()) - 1
        return sub_topics[index]
    except:
        return sub_topics[0]

def task_why(sub_topic, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Explain why this is important or worth solving:\n{sub_topic}"
    )
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🟦 WHY:\n", response)
    return response

def task_how(why_text, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Given the importance:\n{why_text}\n\n"
        f"List short, specific ways to address it. Use a numbered list (≤20 words each)."
    )
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🟩 HOW:\n", response)
    return response

def task_risks(sub_topic, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Identify 2-3 key risks or challenges in addressing:\n{sub_topic}\n"
        f"Use a numbered list."
    )
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🟥 RISKS:\n", response)
    return response

def task_alternatives(sub_topic, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Suggest 2 alternative approaches to:\n{sub_topic}\n"
        f"Use a numbered list."
    )
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🟪 ALTERNATIVES:\n", response)
    return response

def generate_solution(topic, what, why, how, ai_mode, reasoning_modality, multi_step=False, risks=None, alternatives=None, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Given the chosen topic: {topic}\n\n"
        f"WHY it matters:\n{why}\n\n"
        f"HOW to address it:\n{how}\n"
    )
    if risks:
        prompt += f"\nRISKS:\n{risks}\n"
    if alternatives:
        prompt += f"\nALTERNATIVES:\n{alternatives}\n"
    prompt += "Write a clear, useful response. Code if needed. Keep it user-focused."
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🎯 SOLUTION:\n", response)
    return response

def generate_next_problem(topic, why, how, ai_mode, reasoning_modality, multi_step=False, think_aloud=False):
    prompt = (
        f"AI Mode: {ai_mode}. Reasoning: {reasoning_modality}.\n"
        f"Based on solving: '{topic}'\n\n"
        f"WHY: {why}\n\nHOW: {how}\n\n"
        f"Suggest one deeper or related question to explore next."
    )
    if multi_step:
        prompt += "\nReason step by step."
    prompt = add_think_aloud(prompt, think_aloud)
    response = call_gpt(prompt)
    print("\n🔁 NEXT PROBLEM:\n", response)
    return response.strip()

if __name__ == "__main__":
    main()
