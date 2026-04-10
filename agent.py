import time
from ai_brain import ask_ai
from logger import log

# =========================
# CONFIG
# =========================
MIN_CONFIDENCE = 0.4
STEP_DELAY = 0.4
MAX_RETRIES = 2
ENABLE_SELF_HEAL = True

# =========================
# AGENT LOOP
# =========================
def run_agent(user_input, executor, permission_callback=None):
    log.info(f"[AGENT START] {user_input}")

    results = ask_ai(user_input)

    if not results:
        print("❌ No actions generated")
        return

    for i, step in enumerate(results, start=1):
        action = step.get("action")
        params = step.get("params", {})
        danger = step.get("danger", False)
        confidence = step.get("confidence", 0)

        print(f"\n[JARVIS ⚙️] Step {i}: {action} | confidence={confidence:.2f}")

        # =========================
        # CONFIDENCE FILTER
        # =========================
        if confidence < MIN_CONFIDENCE:
            print("⚠️ Low confidence → skipped")
            log.warning(f"Skipped {action} due to low confidence")
            continue

        # =========================
        # SAFETY CHECK
        # =========================
        if danger:
            print(f"⚠️ Dangerous action detected: {action}")

            if permission_callback:
                allowed = permission_callback(action, params)
            else:
                allowed = input("Allow? (yes/no): ").strip().lower() == "yes"

            if not allowed:
                print("❌ Blocked by user")
                log.warning(f"Blocked {action}")
                continue

        # =========================
        # EXECUTION (WITH RETRY)
        # =========================
        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # ✅ FIX: executor is FUNCTION, not class
                result = executor(action, params)

                log.info(f"[EXECUTED] {action} → {result}")
                print(f"✅ Done: {action}")

                success = True
                break

            except Exception as e:
                log.error(f"[ERROR] {action} attempt {attempt}: {e}")
                print(f"❌ Error: {e}")
                time.sleep(0.5)

        # =========================
        # SELF-HEALING (AI FIX)
        # =========================
        if not success and ENABLE_SELF_HEAL:
            print(f"❌ Failed after {MAX_RETRIES} attempts: {action}")
            log.warning(f"Failed action: {action}")

            try:
                print("🧠 Asking AI to fix...")

                fix_prompt = f"""
The following action failed:

Action: {action}
Params: {params}

Suggest a corrected action in JSON format.
"""

                new_steps = ask_ai(fix_prompt)

                if not new_steps:
                    print("❌ AI could not fix the issue")
                    continue

                print(f"🔧 AI suggested fix: {new_steps}")

                # Execute fixed steps (ONLY ONCE)
                for fix_step in new_steps:
                    fix_action = fix_step.get("action")
                    fix_params = fix_step.get("params", {})
                    fix_danger = fix_step.get("danger", False)

                    print(f"🔄 Retrying with: {fix_action}")

                    # Safety check again
                    if fix_danger:
                        confirm = input(f"⚠️ Allow fixed action {fix_action}? (yes/no): ").strip().lower()
                        if confirm != "yes":
                            print("❌ Fixed action blocked")
                            continue

                    try:
                        result = executor(fix_action, fix_params)

                        log.info(f"[FIXED] {fix_action} → {result}")
                        print(f"✅ Fixed successfully: {fix_action}")

                    except Exception as e:
                        log.error(f"[FIX FAILED] {fix_action}: {e}")
                        print(f"❌ Fix failed: {e}")

            except Exception as e:
                log.error(f"AI fix error: {e}")
                print("❌ AI fix system crashed")

            continue

        # =========================
        # FINAL FAIL (NO SELF HEAL)
        # =========================
        if not success:
            print(f"❌ Failed after {MAX_RETRIES} attempts: {action}")
            continue

        # =========================
        # STEP DELAY
        # =========================
        time.sleep(STEP_DELAY)