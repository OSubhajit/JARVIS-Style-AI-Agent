# executor.py — JARVIS V4 Master Action Router (150+ actions)
import os, webbrowser
from datetime import datetime
from logger import log
from memory import remember, forget, recall_all_fmt
from database import hist_get, mem_clear

# ── Plugin imports ────────────────────────────────────────────────────────────
from plugins.web_tools import (get_weather,search_wikipedia,get_news,get_crypto_price,
    get_stock_price,translate_text,check_website,download_file,speed_test,
    ip_geolocation,dns_lookup,whois_lookup,check_breach,get_wifi_passwords,scrape_url)
from plugins.file_tools import (create_file,delete_file,read_file,write_to_file,
    rename_file,copy_file,move_file,list_files,search_file,get_file_info,
    zip_files,unzip_file,open_file,ocr_image,pdf_merge,pdf_split,pdf_to_text,
    find_duplicates,batch_rename,organize_downloads,text_diff,image_resize,
    image_convert,extract_metadata)
from plugins.system_tools import (get_cpu,get_ram,get_disk,get_battery,get_gpu,
    get_temp,system_report,flush_memory,boot_analyzer,list_processes,kill_process,
    list_services,start_service,stop_service,power_plan,show_ip,show_wifi,
    ping_host,scan_ports,arp_scan,network_speed,get_startup_apps,add_to_startup,
    remove_from_startup,clear_temp,empty_recycle_bin,list_windows,focus_window,
    minimize_window,maximize_window,close_window,git_status,git_pull,git_push,
    git_log,git_diff,git_commit,file_integrity_check,shred_file,check_password_strength)
from plugins.productivity import (set_reminder,show_reminders,delete_reminder,
    set_alarm,start_timer,stop_timer,start_pomodoro,stop_pomodoro,pomodoro_status,
    calculate,convert_units,generate_qr,send_email,read_emails,add_alias,
    list_aliases,remove_alias,generate_password,tell_joke,daily_briefing,
    track_habit,show_habits,log_mood,show_mood,add_task,list_tasks,complete_task,
    delete_task,log_expense,show_expenses,vault_store,vault_retrieve,vault_list_all,
    vault_remove,vault_wipe,totp_add_key,totp_get_code,encrypt_file,decrypt_file,
    start_focus,stop_focus)
from plugins.media_tools import (play_pause,next_track,prev_track,volume_mute,
    volume_up,volume_down,volume_set,show_clipboard,copy_to_clipboard,
    clear_clipboard,show_clipboard_history,take_screenshot,download_youtube,shazam)
from plugins.vision_tools import (webcam_snapshot,motion_detect,face_recognize,
    scan_qr_webcam,object_detect,color_picker,read_screen,intruder_alert,
    screen_record)
from plugins.automation import (record_macro,stop_recording,play_macro,list_macros,
    schedule_job,list_jobs,cancel_job,backup_folder,restore_backup,
    file_watcher_start,add_rule,list_rules,send_notification,wake_on_lan)
from plugins.dev_tools import (run_code,http_request,format_json,validate_yaml,
    regex_test,encode_base64,decode_base64,hash_text,serve_folder,stop_server,
    docker_ps,docker_start,docker_stop,docker_logs,analyze_deps,generate_readme,
    generate_tests,git_commit_message,install_package)
from plugins.mobile_remote import (adb_devices,adb_screenshot,adb_install,
    telegram_send,send_push_notification,mqtt_publish,mqtt_subscribe,ha_toggle,ha_state)


def execute(action, params={}, speak_fn=None):
    p=params; result=""
    try:
        if   action=="unknown": result="I didn't understand that. Type 'help'."
        elif action=="chat":    result=p.get("reply","...")

        # ── Web ──────────────────────────────────────────────────────────────
        elif action=="search_google":    webbrowser.open(f"https://www.google.com/search?q={p.get('query','').replace(' ','+')}"); result=f"Google: {p.get('query')}"
        elif action=="search_youtube":   webbrowser.open(f"https://www.youtube.com/results?search_query={p.get('query','').replace(' ','+')}"); result=f"YouTube: {p.get('query')}"
        elif action=="search_wikipedia": result=search_wikipedia(p.get("query",""))
        elif action=="search_github":    webbrowser.open(f"https://github.com/search?q={p.get('query','').replace(' ','+')}"); result=f"GitHub: {p.get('query')}"
        elif action=="open_url":         url=p.get("url",""); webbrowser.open(url); result=f"Opened: {url}"
        elif action=="get_weather":      result=get_weather(p.get("city",""))
        elif action=="get_news":         result=get_news(int(p.get("limit",6)))
        elif action=="get_crypto_price": result=get_crypto_price(p.get("symbol","BTC"))
        elif action=="get_stock_price":  result=get_stock_price(p.get("symbol","AAPL"))
        elif action=="translate_text":   result=translate_text(p.get("text",""),p.get("target","hi"))
        elif action=="check_website":    result=check_website(p.get("url",""))
        elif action=="download_file":    result=download_file(p.get("url",""))
        elif action=="speed_test":       result=speed_test()
        elif action=="ip_geolocation":   result=ip_geolocation(p.get("ip",""))
        elif action=="dns_lookup":       result=dns_lookup(p.get("domain",""))
        elif action=="whois_lookup":     result=whois_lookup(p.get("domain",""))
        elif action=="check_breach":     result=check_breach(p.get("email",""))
        elif action=="wifi_passwords":   result=get_wifi_passwords()
        elif action=="scrape_url":       result=scrape_url(p.get("url",""),p.get("selector",""))

        # ── Files ────────────────────────────────────────────────────────────
        elif action=="create_file":      result=create_file(p.get("filename","new.txt"),p.get("content",""))
        elif action=="delete_file":      result=delete_file(p.get("filename",""))
        elif action=="read_file":        result=read_file(p.get("filename",""))
        elif action=="write_to_file":    result=write_to_file(p.get("filename",""),p.get("content",""))
        elif action=="rename_file":      result=rename_file(p.get("old",""),p.get("new",""))
        elif action=="copy_file":        result=copy_file(p.get("src",""),p.get("dst",""))
        elif action=="move_file":        result=move_file(p.get("src",""),p.get("dst",""))
        elif action=="list_files":       result=list_files(p.get("path","."))
        elif action=="search_file":      result=search_file(p.get("query",""))
        elif action=="get_file_info":    result=get_file_info(p.get("filename",""))
        elif action=="zip_files":        result=zip_files(p.get("files",[]),p.get("output","archive.zip"))
        elif action=="unzip_file":       result=unzip_file(p.get("filename",""),p.get("dest","."))
        elif action=="open_file":        result=open_file(p.get("filename",""))
        elif action=="ocr_image":
            result=ocr_image(p.get("filename",""))
            if not result:
                result="OCR returned no text. Check the file exists and is a valid image."
        elif action=="pdf_merge":        result=pdf_merge(p.get("files",[]),p.get("output","merged.pdf"))
        elif action=="pdf_split":        result=pdf_split(p.get("filename",""),p.get("output_dir","."))
        elif action=="pdf_to_text":      result=pdf_to_text(p.get("filename",""))
        elif action=="find_duplicates":  result=find_duplicates(p.get("path","."))
        elif action=="batch_rename":     result=batch_rename(p.get("path","."),p.get("pattern",""),p.get("replacement",""))
        elif action=="organize_downloads":result=organize_downloads(p.get("path","."))
        elif action=="text_diff":        result=text_diff(p.get("file1",""),p.get("file2",""))
        elif action=="image_resize":     result=image_resize(p.get("filename",""),p.get("width",800),p.get("height",600))
        elif action=="image_convert":    result=image_convert(p.get("filename",""),p.get("format","png"))
        elif action=="extract_metadata": result=extract_metadata(p.get("filename",""))

        # ── System ───────────────────────────────────────────────────────────
        elif action=="show_cpu":          result=f"CPU: {get_cpu()}"
        elif action=="show_ram":          result=f"RAM: {get_ram()}"
        elif action=="show_disk":         result=f"Disk: {get_disk()}"
        elif action=="show_battery":      result=f"Battery: {get_battery()}"
        elif action=="show_gpu":          result=f"GPU: {get_gpu()}"
        elif action=="show_temp":         result=get_temp()
        elif action=="system_report":     result=system_report()
        elif action=="flush_memory":      result=flush_memory()
        elif action=="boot_analyzer":     result=boot_analyzer()
        elif action=="list_processes":    result=list_processes()
        elif action=="kill_process":      result=kill_process(p.get("process",""))
        elif action=="list_services":     result=list_services()
        elif action=="start_service":     result=start_service(p.get("name",""))
        elif action=="stop_service":      result=stop_service(p.get("name",""))
        elif action=="power_plan":        result=power_plan(p.get("plan","balanced"))
        elif action=="show_ip":           result=show_ip()
        elif action=="show_wifi":         result=show_wifi()
        elif action=="ping_host":         result=ping_host(p.get("host","google.com"))
        elif action=="scan_ports":        result=scan_ports(p.get("host","localhost"),p.get("ports","1-1024"))
        elif action=="arp_scan":          result=arp_scan()
        elif action=="network_speed":     result=network_speed()
        elif action=="get_startup_apps":  result=get_startup_apps()
        elif action=="add_to_startup":    result=add_to_startup(p.get("name",""),p.get("path",""))
        elif action=="remove_from_startup":result=remove_from_startup(p.get("name",""))
        elif action=="clear_temp":        result=clear_temp()
        elif action=="empty_recycle_bin": result=empty_recycle_bin()
        elif action=="take_screenshot":   result=take_screenshot(p.get("filename","screenshot.png"))
        elif action=="screen_record":     result=screen_record(int(p.get("duration",10)))
        elif action=="list_windows":      result=list_windows()
        elif action=="focus_window":      result=focus_window(p.get("title",""))
        elif action=="minimize_window":   result=minimize_window(p.get("title",""))
        elif action=="maximize_window":   result=maximize_window(p.get("title",""))
        elif action=="close_window":      result=close_window(p.get("title",""))

        # ── Media ────────────────────────────────────────────────────────────
        elif action=="play_pause":          result=play_pause()
        elif action=="next_track":          result=next_track()
        elif action=="prev_track":          result=prev_track()
        elif action=="volume_mute":         result=volume_mute()
        elif action=="volume_up":           result=volume_up(int(p.get("amount",10)) if str(p.get("amount",10)).isdigit() else 10)
        elif action=="volume_down":         result=volume_down(int(p.get("amount",10)) if str(p.get("amount",10)).isdigit() else 10)
        elif action=="volume_set":          result=volume_set(int(p.get("level",50)) if str(p.get("level",50)).isdigit() else 50)
        elif action=="show_clipboard":      result=show_clipboard()
        elif action=="copy_to_clipboard":   result=copy_to_clipboard(p.get("text",""))
        elif action=="clear_clipboard":     result=clear_clipboard()
        elif action=="clipboard_history":   result=show_clipboard_history()
        elif action=="download_youtube":    result=download_youtube(p.get("url",""),bool(p.get("audio_only",False)))
        elif action=="shazam":              result=shazam(p.get("filename",""))

        # ── Vision ───────────────────────────────────────────────────────────
        elif action=="webcam_snapshot":    result=webcam_snapshot()
        elif action=="motion_detect":      result=motion_detect(int(p.get("duration",10)))
        elif action=="face_recognize":     result=face_recognize()
        elif action=="scan_qr_webcam":     result=scan_qr_webcam()
        elif action=="object_detect":      result=object_detect(p.get("filename",""))
        elif action=="color_picker":       result=color_picker(p.get("x",0),p.get("y",0))
        elif action=="read_screen":        result=read_screen()
        elif action=="intruder_alert":     result=intruder_alert(int(p.get("duration",30)),speak_fn)

        # ── Productivity ─────────────────────────────────────────────────────
        elif action=="set_reminder":    result=set_reminder(p.get("message","Reminder"),int(p.get("minutes",10)),speak_fn)
        elif action=="show_reminders":  result=show_reminders()
        elif action=="delete_reminder": result=delete_reminder(p.get("id",0))
        elif action=="set_alarm":       result=set_alarm(p.get("message","Alarm"),p.get("time","07:00"),speak_fn)
        elif action=="start_timer":     result=start_timer(p.get("label","default"))
        elif action=="stop_timer":      result=stop_timer(p.get("id",1))
        elif action=="start_pomodoro":  result=start_pomodoro(p.get("task","Focus"),speak_fn)
        elif action=="stop_pomodoro":   result=stop_pomodoro()
        elif action=="pomodoro_status": result=pomodoro_status()
        elif action=="calculate":       result=calculate(p.get("expression","0"))
        elif action=="convert_units":   result=convert_units(float(p.get("value",0)),p.get("from","km"),p.get("to","miles"))
        elif action=="generate_qr":     result=generate_qr(p.get("text",""),p.get("filename","qrcode.png"))
        elif action=="send_email":      result=send_email(p.get("to",""),p.get("subject",""),p.get("body",""))
        elif action=="read_emails":     result=read_emails(int(p.get("limit",5)))
        elif action=="add_alias":       result=add_alias(p.get("alias",""),p.get("command",""))
        elif action=="list_aliases":    result=list_aliases()
        elif action=="remove_alias":    result=remove_alias(p.get("alias",""))
        elif action=="generate_password":result=generate_password(int(p.get("length",16)),bool(p.get("symbols",True)))
        elif action=="tell_joke":        result=tell_joke()
        elif action=="daily_briefing":   result=daily_briefing(speak_fn)
        elif action=="get_time":         result=f"Time: {datetime.now().strftime('%I:%M:%S %p')}"
        elif action=="get_date":         result=f"Date: {datetime.now().strftime('%A, %B %d, %Y')}"
        elif action=="add_task":         result=add_task(p.get("title",""),p.get("priority","medium"))
        elif action=="list_tasks":       result=list_tasks(p.get("status"))
        elif action=="complete_task":    result=complete_task(p.get("id",0))
        elif action=="delete_task":      result=delete_task(p.get("id",0))
        elif action=="habit_track":      result=track_habit(p.get("name",""))
        elif action=="habit_show":       result=show_habits()
        elif action=="mood_log":         result=log_mood(p.get("mood",""),p.get("note",""))
        elif action=="mood_show":        result=show_mood()
        elif action=="log_expense":      result=log_expense(p.get("amount",0),p.get("category","general"),p.get("note",""))
        elif action=="show_expenses":    result=show_expenses()
        elif action=="start_focus":      result=start_focus(p.get("minutes",25),speak_fn)
        elif action=="stop_focus":       result=stop_focus()

        # ── Vault ────────────────────────────────────────────────────────────
        elif action=="vault_add":    result=vault_store(p.get("label",""),p.get("password",""))
        elif action=="vault_get":    result=vault_retrieve(p.get("label",""))
        elif action=="vault_list":   result=vault_list_all()
        elif action=="vault_delete": result=vault_remove(p.get("label",""))
        elif action=="clear_vault":  result=vault_wipe()
        elif action=="totp_add":     result=totp_add_key(p.get("label",""),p.get("secret",""))
        elif action=="totp_get":     result=totp_get_code(p.get("label",""))
        elif action=="encrypt_file": result=encrypt_file(p.get("filename",""))
        elif action=="decrypt_file": result=decrypt_file(p.get("filename",""))
        elif action=="shred_file":   result=shred_file(p.get("filename",""),int(p.get("passes",3)))
        elif action=="check_password_strength": result=check_password_strength(p.get("password",""))
        elif action=="file_integrity_check":    result=file_integrity_check(p.get("filepath","check"))

        # ── Dev ──────────────────────────────────────────────────────────────
        elif action=="validate_yaml":     result=validate_yaml(p.get("text","{}"))
        elif action=="stop_server":       result=stop_server()
        elif action=="git_commit_message":result=git_commit_message(p.get("diff",""))
        elif action=="run_code":          result=run_code(p.get("code",""),p.get("language","python"))
        elif action=="http_request":      result=http_request(p.get("method","GET"),p.get("url",""),p.get("headers"),p.get("body"))
        elif action=="format_json":       result=format_json(p.get("text","{}"))
        elif action=="regex_test":        result=regex_test(p.get("pattern",""),p.get("text",""))
        elif action=="encode_base64":     result=encode_base64(p.get("text",""))
        elif action=="decode_base64":     result=decode_base64(p.get("text",""))
        elif action=="hash_text":         result=hash_text(p.get("text",""),p.get("algo","sha256"))
        elif action=="serve_folder":      result=serve_folder(p.get("path","."),int(p.get("port",8080)))
        elif action=="docker_ps":         result=docker_ps()
        elif action=="docker_start":      result=docker_start(p.get("name",""))
        elif action=="docker_stop":       result=docker_stop(p.get("name",""))
        elif action=="docker_logs":       result=docker_logs(p.get("name",""))
        elif action=="analyze_deps":      result=analyze_deps()
        elif action=="generate_readme":   result=generate_readme(p.get("path","."))
        elif action=="generate_tests":    result=generate_tests(p.get("filename",""))
        elif action=="git_commit":        result=git_commit(p.get("msg",""),p.get("path","."))
        elif action=="install_package":   result=install_package(p.get("package",""))

        # ── Git ──────────────────────────────────────────────────────────────
        elif action=="git_status": result=git_status(p.get("path","."))
        elif action=="git_pull":   result=git_pull(p.get("path","."))
        elif action=="git_push":   result=git_push(p.get("path","."))
        elif action=="git_log":    result=git_log(p.get("path","."))
        elif action=="git_diff":   result=git_diff(p.get("path","."))

        # ── Automation ───────────────────────────────────────────────────────
        elif action=="record_macro":       result=record_macro(p.get("name","macro"))
        elif action=="play_macro":         result=play_macro(p.get("name",""),execute)
        elif action=="list_macros":        result=list_macros()
        elif action=="schedule_job":       result=schedule_job(p.get("name",""),p.get("command",""),int(p.get("interval_sec",3600)))
        elif action=="list_jobs":          result=list_jobs()
        elif action=="cancel_job":         result=cancel_job(p.get("name",""))
        elif action=="backup_folder":      result=backup_folder(p.get("source","./data"),p.get("dest","./backups"))
        elif action=="restore_backup":     result=restore_backup(p.get("backup_file",""),p.get("dest","."))
        elif action=="file_watcher_start": result=file_watcher_start(p.get("filepath",""),speak_fn)
        elif action=="rules_add":          result=add_rule(p.get("condition",""),p.get("action",""))
        elif action=="rules_list":         result=list_rules()
        elif action=="send_notification":  result=send_notification(p.get("title","JARVIS"),p.get("body",""))
        elif action=="wake_on_lan":        result=wake_on_lan(p.get("mac",""))

        # ── Mobile / Remote ──────────────────────────────────────────────────
        elif action=="adb_devices":    result=adb_devices()
        elif action=="adb_screenshot": result=adb_screenshot()
        elif action=="adb_install":    result=adb_install(p.get("apk",""))
        elif action=="telegram_send":  result=telegram_send(p.get("message",""))
        elif action=="send_push_notification": result=send_push_notification(p.get("title",""),p.get("message",""),p.get("token",""))
        elif action=="mqtt_publish":   result=mqtt_publish(p.get("topic",""),p.get("message",""))
        elif action=="mqtt_subscribe": result=mqtt_subscribe(p.get("topic","#"))
        elif action=="ha_toggle":      result=ha_toggle(p.get("entity_id",""))
        elif action=="ha_state":       result=ha_state(p.get("entity_id",""))

        # ── Memory ───────────────────────────────────────────────────────────
        elif action=="remember_this":      remember(p.get("key","note"),p.get("value","")); result=f"Remembered: {p.get('key')} = {p.get('value')}"
        elif action=="what_do_you_know":   result=recall_all_fmt() or "Nothing stored yet."
        elif action=="forget_this":        forget(p.get("key","")); result=f"Forgotten: {p.get('key')}"
        elif action=="forget_everything":  mem_clear(); result="All memories cleared."
        elif action=="show_history":
            rows=hist_get(int(p.get("limit",15)))
            result="History:\n"+"\n".join(f"  [{r['timestamp'][:16]}] {r['input']}" for r in rows) if rows else "No history."
        elif action in ("summarize_text","explain_topic"):
            # Delegate to execute_v41 which has proper advanced_ai implementations
            v41_result = execute_v41(action, params, speak_fn)
            if v41_result:
                return v41_result
            # Fallback to basic _ai if v41 fails
            text=p.get("text","") or p.get("topic","")
            result=_ai(f"{'Summarize briefly' if action=='summarize_text' else 'Explain simply'}: {text}")

        # ── Standard OS ──────────────────────────────────────────────────────
        else:
            # Try V4.1 extended actions first
            v41_result = execute_v41(action, params, speak_fn)
            if v41_result:
                return v41_result
            # Try V4.2 actions (finance, study, content, lifestyle, science, etc.)
            v42_result = execute_v42(action, params, speak_fn)
            if v42_result:
                return v42_result
            from config import COMMANDS
            cmd=COMMANDS.get(action)
            if cmd: os.system(cmd); result=f"{action.replace('_',' ').title()} ✓"
            else:   result=f"No handler: {action}"

    except Exception as e:
        result=f"Error: {e}"; log.error(f"Execute [{action}]: {e}")

    if result:
        print(f"\n\033[96m[JARVIS]\033[0m {result}")
        log.info(f"[{action}] → {result[:80]}")
    return result

def _ai(prompt):
    try:
        import requests
        from config import OLLAMA_URL,MODEL_NAME,AI_TIMEOUT
        r=requests.post(OLLAMA_URL,json={"model":MODEL_NAME,"prompt":prompt,"stream":False},timeout=AI_TIMEOUT)
        return r.json().get("response","").strip()
    except: return "AI unavailable."

# ═══════════════════════════════════════════════════════════════════════════
# V4.1 PATCH — 150+ new actions appended to execute()
# ═══════════════════════════════════════════════════════════════════════════

def execute_v41(action, params={}, speak_fn=None):
    """Handles all new V4.1 actions. Called from execute() as fallback."""
    p = params
    result = ""

    # ── Imports (lazy) ──────────────────────────────────────────────────────
    from plugins.text_tools import (
        word_count, case_upper, case_lower, case_title, case_camel, case_snake,
        case_kebab, case_pascal, case_reverse, case_alternate, remove_duplicates,
        sort_lines, remove_empty_lines, trim_whitespace, add_line_numbers,
        find_replace, extract_emails, extract_urls, extract_phones, extract_numbers,
        count_words_freq, rot13, morse_encode, morse_decode, binary_encode,
        binary_decode, hex_encode, hex_decode, lorem_ipsum, random_sentence,
        random_quote, random_name, random_color, random_number, flip_coin, roll_dice,
        readability_score, detect_language, palindrome_check, anagram_check
    )
    from plugins.health_tools import (
        bmi_calculate, calories_needed, ideal_weight, water_goal,
        log_water, show_water_today, log_sleep, show_sleep_week,
        log_workout, show_workouts, workout_streak, personal_records,
        log_weight, show_weight_history, log_calories, show_calories_today,
        health_tip, breathing_exercise
    )
    from plugins.network_advanced import (
        ssl_check, traceroute, subdomain_scan, mac_lookup, network_interfaces,
        open_connections, bandwidth_monitor, firewall_status, shared_folders,
        check_port_open, dns_records, http_headers, find_my_public_ip,
        reverse_dns, port_to_service, vpn_check
    )
    from plugins.advanced_ai import (
        code_review, explain_code, fix_code, translate_code, generate_code,
        optimize_code, add_docstrings, write_email, improve_writing, write_essay,
        write_linkedin_post, write_tweet, debate_topic, pros_cons, fact_check,
        what_if, interview_prep, study_plan, rag_index_file, rag_query,
        daily_word, eli5, summarize_text, explain_topic
    )
    from plugins.analytics import (
        command_stats, productivity_report, weekly_summary, mood_trends,
        habit_analytics, expense_breakdown, sleep_analytics,
        ascii_bar_chart, generate_report, disk_usage_breakdown
    )
    from plugins.creative_tools import (
        ascii_banner, ascii_art_from_image, draw_box, progress_bar,
        random_color_palette, generate_username, generate_api_key, generate_uuid,
        story_generator, meme_text, rhyme_words, haiku_generator, acronym_generator,
        number_facts, prime_check, fibonacci, factorize, base_convert,
        statistics_calc, countdown_timer, stopwatch_lap, world_clock
    )

    # ── Text Tools ────────────────────────────────────────────────────────
    if   action=="word_count":        result=word_count(p.get("text",""))
    elif action=="case_upper":        result=case_upper(p.get("text",""))
    elif action=="case_lower":        result=case_lower(p.get("text",""))
    elif action=="case_title":        result=case_title(p.get("text",""))
    elif action=="case_camel":        result=case_camel(p.get("text",""))
    elif action=="case_snake":        result=case_snake(p.get("text",""))
    elif action=="case_kebab":        result=case_kebab(p.get("text",""))
    elif action=="case_pascal":       result=case_pascal(p.get("text",""))
    elif action=="case_reverse":      result=case_reverse(p.get("text",""))
    elif action=="case_alternate":    result=case_alternate(p.get("text",""))
    elif action=="remove_duplicates": result=remove_duplicates(p.get("text",""))
    elif action=="sort_lines":        result=sort_lines(p.get("text",""),bool(p.get("reverse",False)))
    elif action=="remove_empty_lines":result=remove_empty_lines(p.get("text",""))
    elif action=="trim_whitespace":   result=trim_whitespace(p.get("text",""))
    elif action=="add_line_numbers":  result=add_line_numbers(p.get("text",""))
    elif action=="find_replace":      result=find_replace(p.get("text",""),p.get("find",""),p.get("replace",""))[1]
    elif action=="extract_emails":    result=extract_emails(p.get("text",""))
    elif action=="extract_urls":      result=extract_urls(p.get("text",""))
    elif action=="extract_phones":    result=extract_phones(p.get("text",""))
    elif action=="extract_numbers":   result=extract_numbers(p.get("text",""))
    elif action=="count_words_freq":  result=count_words_freq(p.get("text",""))
    elif action=="rot13":             result=rot13(p.get("text",""))
    elif action=="morse_encode":      result=morse_encode(p.get("text",""))
    elif action=="morse_decode":      result=morse_decode(p.get("text",""))
    elif action=="binary_encode":     result=binary_encode(p.get("text",""))
    elif action=="binary_decode":     result=binary_decode(p.get("text",""))
    elif action=="hex_encode":        result=hex_encode(p.get("text",""))
    elif action=="hex_decode":        result=hex_decode(p.get("text",""))
    elif action=="lorem_ipsum":       result=lorem_ipsum(int(p.get("words",50)))
    elif action=="random_sentence":   result=random_sentence()
    elif action=="random_quote":      result=random_quote()
    elif action=="random_name":       result=random_name()
    elif action=="random_color":      result=random_color()
    elif action=="random_number":     result=random_number(p.get("min",1),p.get("max",100))
    elif action=="flip_coin":         result=flip_coin()
    elif action=="roll_dice":         result=roll_dice(p.get("sides",6))
    elif action=="readability_score": result=readability_score(p.get("text",""))
    elif action=="detect_language":   result=detect_language(p.get("text",""))
    elif action=="palindrome_check":  result=palindrome_check(p.get("text",""))
    elif action=="anagram_check":     result=anagram_check(p.get("text1",""),p.get("text2",""))

    # ── Health ────────────────────────────────────────────────────────────
    elif action=="bmi_calculate":     result=bmi_calculate(p.get("weight",70),p.get("height",170))
    elif action=="calories_needed":   result=calories_needed(p.get("weight",70),p.get("height",170),p.get("age",25),p.get("gender","male"),p.get("activity","moderate"))
    elif action=="ideal_weight":      result=ideal_weight(p.get("height",170),p.get("gender","male"))
    elif action=="water_goal":        result=water_goal(p.get("weight",70))
    elif action=="log_water":         result=log_water(int(p.get("ml",250)))
    elif action=="show_water_today":  result=show_water_today()
    elif action=="log_sleep":         result=log_sleep(p.get("hours",7),p.get("quality","good"),p.get("note",""))
    elif action=="show_sleep_week":   result=show_sleep_week()
    elif action=="log_workout":       result=log_workout(p.get("exercise",""),p.get("sets",3),p.get("reps",10),p.get("weight",0),p.get("duration",0))
    elif action=="show_workouts":     result=show_workouts(int(p.get("days",7)))
    elif action=="workout_streak":    result=workout_streak()
    elif action=="personal_records":  result=personal_records()
    elif action=="log_weight":        result=log_weight(p.get("weight",70))
    elif action=="show_weight_history":result=show_weight_history()
    elif action=="log_calories":      result=log_calories(p.get("food",""),p.get("calories",0),p.get("meal","snack"))
    elif action=="show_calories_today":result=show_calories_today()
    elif action=="health_tip":        result=health_tip()
    elif action=="breathing_exercise":result=breathing_exercise(p.get("technique","4-7-8"))

    # ── Network Advanced ──────────────────────────────────────────────────
    elif action=="ssl_check":         result=ssl_check(p.get("host",""),int(p.get("port",443)))
    elif action=="traceroute":        result=traceroute(p.get("host","google.com"))
    elif action=="subdomain_scan":    result=subdomain_scan(p.get("domain",""))
    elif action=="mac_lookup":        result=mac_lookup(p.get("mac",""))
    elif action=="network_interfaces":result=network_interfaces()
    elif action=="open_connections":  result=open_connections()
    elif action=="bandwidth_monitor": result=bandwidth_monitor(int(p.get("duration",5)))
    elif action=="firewall_status":   result=firewall_status()
    elif action=="shared_folders":    result=shared_folders()
    elif action=="check_port_open":   result=check_port_open(p.get("host","localhost"),p.get("port",80))
    elif action=="dns_records":       result=dns_records(p.get("domain",""))
    elif action=="http_headers":      result=http_headers(p.get("url",""))
    elif action=="find_my_public_ip": result=find_my_public_ip()
    elif action=="reverse_dns":       result=reverse_dns(p.get("ip",""))
    elif action=="port_to_service":   result=port_to_service(p.get("port",80))
    elif action=="vpn_check":         result=vpn_check()

    # ── Advanced AI ───────────────────────────────────────────────────────
    elif action=="code_review":       result=code_review(p.get("code",""),p.get("language","python"))
    elif action=="explain_code":      result=explain_code(p.get("code",""),p.get("language","python"))
    elif action=="fix_code":          result=fix_code(p.get("code",""),p.get("error",""))
    elif action=="translate_code":    result=translate_code(p.get("code",""),p.get("from","python"),p.get("to","javascript"))
    elif action=="generate_code":     result=generate_code(p.get("description",""),p.get("language","python"))
    elif action=="optimize_code":     result=optimize_code(p.get("code",""),p.get("language","python"))
    elif action=="add_docstrings":    result=add_docstrings(p.get("code",""),p.get("language","python"))
    elif action=="write_email":       result=write_email(p.get("context",""),p.get("tone","professional"))
    elif action=="improve_writing":   result=improve_writing(p.get("text",""))
    elif action=="write_essay":       result=write_essay(p.get("topic",""),int(p.get("words",300)))
    elif action=="write_linkedin_post":result=write_linkedin_post(p.get("topic",""))
    elif action=="write_tweet":       result=write_tweet(p.get("topic",""))
    elif action=="summarize_text":    result=summarize_text(p.get("text",""),int(p.get("sentences",3)))
    elif action=="explain_topic":     result=explain_topic(p.get("topic",""),p.get("level","beginner"))
    elif action=="debate_topic":      result=debate_topic(p.get("topic",""))
    elif action=="pros_cons":         result=pros_cons(p.get("topic",""))
    elif action=="fact_check":        result=fact_check(p.get("claim",""))
    elif action=="what_if":           result=what_if(p.get("scenario",""))
    elif action=="interview_prep":    result=interview_prep(p.get("role",""),p.get("question",""))
    elif action=="study_plan":        result=study_plan(p.get("topic",""),int(p.get("days",7)))
    elif action=="rag_index_file":    result=rag_index_file(p.get("filepath",""))
    elif action=="rag_query":         result=rag_query(p.get("question",""),p.get("filepath"))
    elif action=="daily_word":        result=daily_word()
    elif action=="eli5":              result=eli5(p.get("topic",""))

    # ── Analytics ────────────────────────────────────────────────────────
    elif action=="command_stats":         result=command_stats()
    elif action=="productivity_report":   result=productivity_report()
    elif action=="weekly_summary":        result=weekly_summary()
    elif action=="mood_trends":           result=mood_trends()
    elif action=="habit_analytics":       result=habit_analytics()
    elif action=="expense_breakdown":     result=expense_breakdown()
    elif action=="sleep_analytics":       result=sleep_analytics()
    elif action=="generate_report":       result=generate_report(p.get("type","daily"))
    elif action=="disk_usage_breakdown":  result=disk_usage_breakdown()
    elif action=="ascii_bar_chart":       result=ascii_bar_chart(p.get("data",{}),p.get("title","Chart"))

    # ── Creative ──────────────────────────────────────────────────────────
    elif action=="ascii_banner":       result=ascii_banner(p.get("text","JARVIS"),p.get("style","block"))
    elif action=="ascii_art_from_image":result=ascii_art_from_image(p.get("filename",""))
    elif action=="draw_box":           result=draw_box(p.get("text",""),p.get("style","double"))
    elif action=="progress_bar":       result=progress_bar(int(p.get("value",0)),int(p.get("total",100)),p.get("label","Progress"))
    elif action=="random_color_palette":result=random_color_palette(int(p.get("count",5)))
    elif action=="generate_username":  result=generate_username(p.get("style","tech"))
    elif action=="generate_api_key":   result=generate_api_key(int(p.get("length",32)))
    elif action=="generate_uuid":      result=generate_uuid()
    elif action=="story_generator":    result=story_generator(p.get("genre","sci-fi"),int(p.get("words",100)))
    elif action=="meme_text":          result=meme_text(p.get("top",""),p.get("bottom",""))
    elif action=="rhyme_words":        result=rhyme_words(p.get("word",""))
    elif action=="haiku_generator":    result=haiku_generator(p.get("topic",""))
    elif action=="acronym_generator":  result=acronym_generator(p.get("word",""))
    elif action=="number_facts":       result=number_facts(p.get("number",7))
    elif action=="prime_check":        result=prime_check(p.get("number",17))
    elif action=="fibonacci":          result=fibonacci(int(p.get("n",10)))
    elif action=="factorize":          result=factorize(p.get("number",360))
    elif action=="base_convert":       result=base_convert(p.get("number","255"),int(p.get("from_base",10)),int(p.get("to_base",2)))
    elif action=="statistics_calc":    result=statistics_calc(p.get("numbers",""))
    elif action=="countdown_timer":    result=countdown_timer(int(p.get("seconds",60)),speak_fn)
    elif action=="stopwatch_lap":      result=stopwatch_lap(p.get("label","lap"))
    elif action=="world_clock":        result=world_clock()

    if result:
        print(f"\n\033[96m[JARVIS]\033[0m {result}")
    return result

def execute_v42(action, params={}, speak_fn=None):
    """V4.2 — Finance, Study, Content, Lifestyle, Code Gen, Science."""
    p = params; result = ""
    try:
        from plugins.finance_tools import (
            currency_convert, currency_list, emi_calculator, loan_amortization,
            simple_interest, compound_interest, sip_calculator, ppf_calculator,
            fd_calculator, roi_calculator, breakeven_calculator, inflation_calculator,
            retirement_calculator, set_budget, show_budget, add_bill, show_bills,
            mark_bill_paid, add_savings_goal, update_savings, show_savings_goals,
            add_investment, show_portfolio, income_tax_india, gst_calculator
        )
        from plugins.study_tools import (
            add_flashcard, review_flashcard, reveal_card, rate_card, list_decks,
            export_deck, import_deck, add_note, get_note, list_notes, search_notes,
            update_note, delete_note, pin_note, export_notes, log_study_session,
            show_study_stats, study_streak, add_vocab, quiz_vocab, reveal_vocab,
            master_vocab, show_vocab, generate_quiz, explain_wrong_answer,
            summarize_for_study, create_mind_map, mnemonics_generator
        )
        from plugins.system_advanced import (
            full_system_info, os_version, installed_updates, check_admin,
            system_locale, bios_info, list_env_vars, get_env_var, get_path_entries,
            list_scheduled_tasks, create_scheduled_task, delete_scheduled_task,
            run_scheduled_task, list_drivers, check_driver_issues, list_drives,
            check_disk_health, disk_cleanup_analysis, list_users, list_groups,
            current_user_info, logged_in_users, list_fonts, clipboard_to_file,
            file_to_clipboard, performance_baseline, reset_network_stack,
            wifi_available_networks, bluetooth_devices, windows_activation_status
        )
        from plugins.content_tools import (
            content_calendar, social_media_strategy, viral_hook_generator,
            caption_generator, thread_generator, youtube_description, youtube_title_ideas,
            blog_outline, seo_keywords, newsletter_template, press_release,
            product_description, ad_copy, cold_email_template, resume_bullet_point,
            grammar_check, tone_analyzer, paraphrase, expand_text, condense_text,
            formal_to_casual, casual_to_formal, bullet_to_paragraph, paragraph_to_bullets,
            active_to_passive, passive_to_active, add_examples, simplify_jargon,
            hashtag_generator, bio_generator, engagement_response, collaboration_pitch,
            content_ideas, trending_topics_prompt
        )
        from plugins.lifestyle_tools import (
            recipe_from_ingredients, recipe_substitute, meal_plan_week, nutrition_info,
            cooking_conversion, food_pairing, calorie_burn, bmi_diet_plan,
            travel_itinerary, packing_list, travel_budget_calculator, visa_requirements,
            currency_tips, local_phrases, best_time_to_visit, travel_insurance_guide,
            days_until, age_calculator, date_difference, what_day_is, countdown_to_event,
            random_activity, inspirational_quote, this_day_in_history, fun_facts,
            riddle, would_you_rather, personality_quiz, life_hack, decision_matrix,
            eisenhower_matrix, smart_goal, habit_stacking
        )
        from plugins.code_generator import (
            scaffold_flask_app, scaffold_fastapi_app, scaffold_cli_tool,
            scaffold_sqlite_manager, scaffold_class, scaffold_test_file,
            scaffold_dockerfile, scaffold_env_file, generate_gitignore, ai_generate_module
        )
        from plugins.science_tools import (
            newton_second_law, kinetic_energy, potential_energy, ohms_law,
            electric_power, projectile_motion, speed_of_light_calc, pendulum_period,
            wavelength_frequency, element_info, molar_mass, ph_calculator,
            boiling_point_altitude, planet_info, light_years_to_km, age_of_universe,
            solar_system_scale, dna_complement, mrna_from_dna, gc_content
        )
    except ImportError as e:
        return f"Plugin import error: {e}"

    # ── Finance ──────────────────────────────────────────────────────────────
    if   action=="currency_convert":    result=currency_convert(p.get("amount",1),p.get("from","USD"),p.get("to","INR"))
    elif action=="currency_list":       result=currency_list()
    elif action=="emi_calculator":      result=emi_calculator(p.get("principal",100000),p.get("rate",10),p.get("years",5))
    elif action=="loan_amortization":   result=loan_amortization(p.get("principal",100000),p.get("rate",10),p.get("years",5))
    elif action=="simple_interest":     result=simple_interest(p.get("principal",10000),p.get("rate",8),p.get("years",3))
    elif action=="compound_interest":   result=compound_interest(p.get("principal",10000),p.get("rate",8),p.get("years",5))
    elif action=="sip_calculator":      result=sip_calculator(p.get("monthly",5000),p.get("rate",12),p.get("years",10))
    elif action=="ppf_calculator":      result=ppf_calculator(p.get("annual",50000),p.get("years",15))
    elif action=="fd_calculator":       result=fd_calculator(p.get("principal",100000),p.get("rate",7),p.get("years",3))
    elif action=="roi_calculator":      result=roi_calculator(p.get("invested",10000),p.get("returns",15000))
    elif action=="breakeven_calculator":result=breakeven_calculator(p.get("fixed_cost",50000),p.get("variable_cost",100),p.get("selling_price",200))
    elif action=="inflation_calculator":result=inflation_calculator(p.get("amount",10000),p.get("rate",6),p.get("years",10))
    elif action=="retirement_calculator":result=retirement_calculator(p.get("current_age",25),p.get("retirement_age",60),p.get("monthly_expense",30000))
    elif action=="set_budget":          result=set_budget(p.get("category","food"),p.get("amount",5000))
    elif action=="show_budget":         result=show_budget()
    elif action=="add_bill":            result=add_bill(p.get("name",""),p.get("amount",0),p.get("due_day",1))
    elif action=="show_bills":          result=show_bills()
    elif action=="mark_bill_paid":      result=mark_bill_paid(p.get("name",""))
    elif action=="add_savings_goal":    result=add_savings_goal(p.get("name",""),p.get("target",0),p.get("deadline",""))
    elif action=="update_savings":      result=update_savings(p.get("name",""),p.get("amount",0))
    elif action=="show_savings_goals":  result=show_savings_goals()
    elif action=="add_investment":      result=add_investment(p.get("symbol",""),p.get("shares",1),p.get("price",0))
    elif action=="show_portfolio":      result=show_portfolio()
    elif action=="income_tax_india":    result=income_tax_india(p.get("income",500000),p.get("regime","new"))
    elif action=="gst_calculator":      result=gst_calculator(p.get("amount",1000),p.get("rate",18),p.get("type","exclusive"))
    # ── Study ────────────────────────────────────────────────────────────────
    elif action=="add_flashcard":       result=add_flashcard(p.get("deck","default"),p.get("question",""),p.get("answer",""))
    elif action=="review_flashcard":    result=review_flashcard(p.get("deck","default"))
    elif action=="reveal_card":         result=reveal_card(p.get("id",1))
    elif action=="rate_card":           result=rate_card(p.get("id",1),p.get("rating","good"))
    elif action=="list_decks":          result=list_decks()
    elif action=="export_deck":         result=export_deck(p.get("deck","default"))
    elif action=="import_deck":         result=import_deck(p.get("filename",""),p.get("deck","imported"))
    elif action=="add_note":            result=add_note(p.get("title",""),p.get("content",""),p.get("tags",""))
    elif action=="get_note":            result=get_note(p.get("id",""))
    elif action=="list_notes":          result=list_notes(p.get("tag",""))
    elif action=="search_notes":        result=search_notes(p.get("query",""))
    elif action=="update_note":         result=update_note(p.get("id",1),p.get("content",""))
    elif action=="delete_note":         result=delete_note(p.get("id",1))
    elif action=="pin_note":            result=pin_note(p.get("id",1))
    elif action=="export_notes":        result=export_notes(p.get("filename","notes_export.md"))
    elif action=="log_study_session":   result=log_study_session(p.get("subject",""),p.get("duration",30))
    elif action=="show_study_stats":    result=show_study_stats()
    elif action=="study_streak":        result=study_streak()
    elif action=="add_vocab":           result=add_vocab(p.get("word",""),p.get("meaning",""),p.get("example",""))
    elif action=="quiz_vocab":          result=quiz_vocab(p.get("language","english"))
    elif action=="reveal_vocab":        result=reveal_vocab(p.get("id",1))
    elif action=="master_vocab":        result=master_vocab(p.get("id",1))
    elif action=="show_vocab":          result=show_vocab(p.get("language","english"))
    elif action=="generate_quiz":       result=generate_quiz(p.get("topic",""),int(p.get("questions",5)))
    elif action=="explain_wrong_answer":result=explain_wrong_answer(p.get("question",""),p.get("your_answer",""),p.get("correct_answer",""))
    elif action=="summarize_for_study": result=summarize_for_study(p.get("text",""))
    elif action=="create_mind_map":     result=create_mind_map(p.get("topic",""))
    elif action=="mnemonics_generator": result=mnemonics_generator(p.get("items",""))
    # ── System Advanced ───────────────────────────────────────────────────────
    elif action=="full_system_info":    result=full_system_info()
    elif action=="os_version":          result=os_version()
    elif action=="installed_updates":   result=installed_updates()
    elif action=="check_admin":         result=check_admin()
    elif action=="system_locale":       result=system_locale()
    elif action=="bios_info":           result=bios_info()
    elif action=="list_env_vars":       result=list_env_vars(p.get("filter",""))
    elif action=="get_env_var":         result=get_env_var(p.get("name","PATH"))
    elif action=="get_path_entries":    result=get_path_entries()
    elif action=="list_scheduled_tasks":result=list_scheduled_tasks()
    elif action=="create_scheduled_task":result=create_scheduled_task(p.get("name",""),p.get("command",""),p.get("schedule","DAILY"),p.get("time","09:00"))
    elif action=="delete_scheduled_task":result=delete_scheduled_task(p.get("name",""))
    elif action=="run_scheduled_task":  result=run_scheduled_task(p.get("name",""))
    elif action=="list_drivers":        result=list_drivers()
    elif action=="check_driver_issues": result=check_driver_issues()
    elif action=="list_drives":         result=list_drives()
    elif action=="check_disk_health":   result=check_disk_health()
    elif action=="disk_cleanup_analysis":result=disk_cleanup_analysis()
    elif action=="list_users":          result=list_users()
    elif action=="list_groups":         result=list_groups()
    elif action=="current_user_info":   result=current_user_info()
    elif action=="logged_in_users":     result=logged_in_users()
    elif action=="list_fonts":          result=list_fonts()
    elif action=="clipboard_to_file":   result=clipboard_to_file(p.get("filename","clipboard_dump.txt"))
    elif action=="file_to_clipboard":   result=file_to_clipboard(p.get("filename",""))
    elif action=="performance_baseline":result=performance_baseline()
    elif action=="reset_network_stack": result=reset_network_stack()
    elif action=="wifi_available_networks":result=wifi_available_networks()
    elif action=="bluetooth_devices":   result=bluetooth_devices()
    elif action=="windows_activation_status":result=windows_activation_status()
    # ── Content ───────────────────────────────────────────────────────────────
    elif action=="content_calendar":    result=content_calendar(p.get("topic",""),int(p.get("days",7)))
    elif action=="social_media_strategy":result=social_media_strategy(p.get("niche",""),p.get("goal",""))
    elif action=="viral_hook_generator":result=viral_hook_generator(p.get("topic",""),int(p.get("count",5)))
    elif action=="caption_generator":   result=caption_generator(p.get("description",""),p.get("platform","instagram"))
    elif action=="thread_generator":    result=thread_generator(p.get("topic",""),int(p.get("tweets",8)))
    elif action=="youtube_description": result=youtube_description(p.get("title",""),p.get("points",""))
    elif action=="youtube_title_ideas": result=youtube_title_ideas(p.get("topic",""),int(p.get("count",10)))
    elif action=="blog_outline":        result=blog_outline(p.get("topic",""))
    elif action=="seo_keywords":        result=seo_keywords(p.get("topic",""),int(p.get("count",20)))
    elif action=="newsletter_template": result=newsletter_template(p.get("niche",""))
    elif action=="press_release":       result=press_release(p.get("event",""),p.get("company",""),p.get("date",""))
    elif action=="product_description": result=product_description(p.get("product",""),p.get("features",""),p.get("audience",""))
    elif action=="ad_copy":             result=ad_copy(p.get("product",""),p.get("platform",""),p.get("objective",""))
    elif action=="cold_email_template": result=cold_email_template(p.get("sender_role",""),p.get("recipient_role",""),p.get("offer",""))
    elif action=="resume_bullet_point": result=resume_bullet_point(p.get("role",""),p.get("achievement",""),p.get("metric",""))
    elif action=="grammar_check":       result=grammar_check(p.get("text",""))
    elif action=="tone_analyzer":       result=tone_analyzer(p.get("text",""))
    elif action=="paraphrase":          result=paraphrase(p.get("text",""),p.get("style","standard"))
    elif action=="expand_text":         result=expand_text(p.get("text",""),int(p.get("words",200)))
    elif action=="condense_text":       result=condense_text(p.get("text",""),int(p.get("words",50)))
    elif action=="formal_to_casual":    result=formal_to_casual(p.get("text",""))
    elif action=="casual_to_formal":    result=casual_to_formal(p.get("text",""))
    elif action=="bullet_to_paragraph": result=bullet_to_paragraph(p.get("text",""))
    elif action=="paragraph_to_bullets":result=paragraph_to_bullets(p.get("text",""))
    elif action=="active_to_passive":   result=active_to_passive(p.get("text",""))
    elif action=="passive_to_active":   result=passive_to_active(p.get("text",""))
    elif action=="add_examples":        result=add_examples(p.get("text",""))
    elif action=="simplify_jargon":     result=simplify_jargon(p.get("text",""),p.get("field","technology"))
    elif action=="hashtag_generator":   result=hashtag_generator(p.get("topic",""),p.get("platform","instagram"))
    elif action=="bio_generator":       result=bio_generator(p.get("name",""),p.get("role",""),p.get("niche",""))
    elif action=="engagement_response": result=engagement_response(p.get("comment",""))
    elif action=="collaboration_pitch": result=collaboration_pitch(p.get("your_niche",""),p.get("their_niche",""),p.get("proposal",""))
    elif action=="content_ideas":       result=content_ideas(p.get("niche",""),int(p.get("count",15)))
    elif action=="trending_topics_prompt":result=trending_topics_prompt(p.get("niche",""))
    # ── Lifestyle ────────────────────────────────────────────────────────────
    elif action=="recipe_from_ingredients":result=recipe_from_ingredients(p.get("ingredients",""),p.get("cuisine","any"))
    elif action=="recipe_substitute":   result=recipe_substitute(p.get("ingredient",""))
    elif action=="meal_plan_week":      result=meal_plan_week(p.get("diet","balanced"),int(p.get("people",1)))
    elif action=="nutrition_info":      result=nutrition_info(p.get("food",""),p.get("quantity","100g"))
    elif action=="cooking_conversion":  result=cooking_conversion(p.get("amount",1),p.get("from","cup"),p.get("to","ml"))
    elif action=="food_pairing":        result=food_pairing(p.get("food",""))
    elif action=="calorie_burn":        result=calorie_burn(p.get("activity","walking"),p.get("duration",30),p.get("weight",70))
    elif action=="bmi_diet_plan":       result=bmi_diet_plan(p.get("bmi",22),p.get("goal","maintain"))
    elif action=="travel_itinerary":    result=travel_itinerary(p.get("destination",""),int(p.get("days",5)))
    elif action=="packing_list":        result=packing_list(p.get("destination",""),p.get("days",7),p.get("season","summer"),p.get("activities","sightseeing"))
    elif action=="travel_budget_calculator":result=travel_budget_calculator(p.get("destination",""),int(p.get("days",7)))
    elif action=="visa_requirements":   result=visa_requirements(p.get("from","India"),p.get("to",""))
    elif action=="currency_tips":       result=currency_tips(p.get("destination",""))
    elif action=="local_phrases":       result=local_phrases(p.get("language",""),int(p.get("count",20)))
    elif action=="best_time_to_visit":  result=best_time_to_visit(p.get("destination",""))
    elif action=="travel_insurance_guide":result=travel_insurance_guide()
    elif action=="days_until":          result=days_until(p.get("date","2025-12-31"))
    elif action=="age_calculator":      result=age_calculator(p.get("birthdate","2000-01-01"))
    elif action=="date_difference":     result=date_difference(p.get("date1",""),p.get("date2",""))
    elif action=="what_day_is":         result=what_day_is(p.get("date",""))
    elif action=="countdown_to_event":  result=countdown_to_event(p.get("event",""),p.get("date",""))
    elif action=="random_activity":     result=random_activity()
    elif action=="inspirational_quote": result=inspirational_quote()
    elif action=="this_day_in_history": result=this_day_in_history()
    elif action=="fun_facts":           result=fun_facts(p.get("topic","random"))
    elif action=="riddle":              result=riddle()
    elif action=="would_you_rather":    result=would_you_rather()
    elif action=="personality_quiz":    result=personality_quiz(p.get("trait","leadership"))
    elif action=="life_hack":           result=life_hack(p.get("problem",""))
    elif action=="decision_matrix":     result=decision_matrix(p.get("options",""),p.get("criteria",""))
    elif action=="eisenhower_matrix":   result=eisenhower_matrix(p.get("tasks",""))
    elif action=="smart_goal":          result=smart_goal(p.get("goal",""))
    elif action=="habit_stacking":      result=habit_stacking(p.get("existing",""),p.get("new",""))
    # ── Code Generator ────────────────────────────────────────────────────────
    elif action=="scaffold_flask_app":  result=scaffold_flask_app(p.get("name","MyApp"))
    elif action=="scaffold_fastapi_app":result=scaffold_fastapi_app(p.get("name","MyAPI"))
    elif action=="scaffold_cli_tool":   result=scaffold_cli_tool(p.get("name","mytool"))
    elif action=="scaffold_sqlite_manager":result=scaffold_sqlite_manager(p.get("name",""),p.get("table","records"),p.get("columns","name,value"))
    elif action=="scaffold_class":      result=scaffold_class(p.get("name","MyClass"),p.get("attributes","name,value"),p.get("methods","process,validate"))
    elif action=="scaffold_test_file":  result=scaffold_test_file(p.get("filename","main.py"))
    elif action=="scaffold_dockerfile": result=scaffold_dockerfile(p.get("type","python"),int(p.get("port",5000)))
    elif action=="scaffold_env_file":   result=scaffold_env_file(p.get("variables","DATABASE_URL,SECRET_KEY,API_KEY"))
    elif action=="generate_gitignore":  result=generate_gitignore(p.get("type","python"))
    elif action=="ai_generate_module":  result=ai_generate_module(p.get("description",""),p.get("language","python"))
    # ── Science ───────────────────────────────────────────────────────────────
    elif action=="newton_second_law":   result=newton_second_law(p.get("force"),p.get("mass"),p.get("acceleration"))
    elif action=="kinetic_energy":      result=kinetic_energy(p.get("mass",1),p.get("velocity",10))
    elif action=="potential_energy":    result=potential_energy(p.get("mass",1),p.get("height",10))
    elif action=="ohms_law":            result=ohms_law(p.get("voltage"),p.get("current"),p.get("resistance"))
    elif action=="electric_power":      result=electric_power(p.get("voltage"),p.get("current"),p.get("resistance"))
    elif action=="projectile_motion":   result=projectile_motion(p.get("velocity",20),p.get("angle",45))
    elif action=="speed_of_light_calc": result=speed_of_light_calc(p.get("distance",384400))
    elif action=="pendulum_period":     result=pendulum_period(p.get("length",1))
    elif action=="wavelength_frequency":result=wavelength_frequency(p.get("value",1e9),p.get("given","frequency"))
    elif action=="element_info":        result=element_info(p.get("element","Fe"))
    elif action=="molar_mass":          result=molar_mass(p.get("formula","H2O"))
    elif action=="ph_calculator":       result=ph_calculator(p.get("concentration",1e-7))
    elif action=="boiling_point_altitude":result=boiling_point_altitude(p.get("altitude",1000))
    elif action=="planet_info":         result=planet_info(p.get("planet","mars"))
    elif action=="light_years_to_km":   result=light_years_to_km(p.get("ly",1))
    elif action=="age_of_universe":     result=age_of_universe()
    elif action=="solar_system_scale":  result=solar_system_scale(p.get("reference","basketball"))
    elif action=="dna_complement":      result=dna_complement(p.get("sequence","ATCG"))
    elif action=="mrna_from_dna":       result=mrna_from_dna(p.get("dna","ATCG"))
    elif action=="gc_content":          result=gc_content(p.get("sequence","ATCGGGCC"))

    if result:
        print(f"\n\033[96m[JARVIS]\033[0m {result}")
    return result