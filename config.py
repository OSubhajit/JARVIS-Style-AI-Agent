# config.py — JARVIS V4 Master Configuration

import os

# ── AI ────────────────────────────────────────────────────────────────────────
OLLAMA_URL     = "http://localhost:11434/api/generate"
OLLAMA_LIST    = "http://localhost:11434/api/tags"
MODEL_NAME     = "gemma3"
MODEL_FAST     = "gemma3"       # for quick tasks
MODEL_SMART    = "gemma3"       # for complex tasks (switch to llama3 etc.)
AI_TIMEOUT     = 60
AI_TEMPERATURE = 0.7

# ── Voice ─────────────────────────────────────────────────────────────────────
VOICE_ENABLED         = True
VOICE_LANGUAGE        = "en-IN"
VOICE_TIMEOUT         = 7
SPEECH_RATE           = 165
SPEECH_VOLUME         = 1.0
WAKE_WORD             = "jarvis"
WAKE_WORD_ACTIVE      = True
USE_WHISPER           = False    # set True if whisper installed (more accurate)
WHISPER_MODEL         = "base"   # tiny/base/small/medium/large

# ── REST API ──────────────────────────────────────────────────────────────────
API_ENABLED  = True
API_HOST     = "0.0.0.0"
API_PORT     = 5000
API_SECRET   = "jarvis-v4-secret"

# ── Telegram Bot ──────────────────────────────────────────────────────────────
TELEGRAM_ENABLED  = False
TELEGRAM_TOKEN    = ""           # get from @BotFather
TELEGRAM_CHAT_ID  = ""           # your chat ID

# ── Notifications (ntfy.sh) ───────────────────────────────────────────────────
NTFY_ENABLED = False
NTFY_TOPIC   = "jarvis-notifications"   # unique topic name

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_FILE        = "data/jarvis.db"
MAX_CONVERSATION_LEN = 30
CLIPBOARD_HISTORY    = 50

# ── Monitoring ────────────────────────────────────────────────────────────────
CPU_ALERT    = 90
RAM_ALERT    = 88
DISK_ALERT   = 95
TEMP_ALERT   = 85    # celsius
MON_INTERVAL = 30

# ── Webcam / Vision ───────────────────────────────────────────────────────────
CAMERA_INDEX          = 0
MOTION_SENSITIVITY    = 25
FACE_RECOGNITION      = False    # set True if face_recognition installed
INTRUDER_ALERT_EMAIL  = False

# ── Productivity ──────────────────────────────────────────────────────────────
DEFAULT_CITY      = "Hailakandi"
DEFAULT_TIMEZONE  = "Asia/Kolkata"
POMODORO_WORK     = 25     # minutes
POMODORO_BREAK    = 5      # minutes
NEWS_SOURCES      = [
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.feedburner.com/ndtvnews-top-stories",
]

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_ADDRESS  = ""
EMAIL_PASSWORD = ""
SMTP_HOST      = "smtp.gmail.com"
SMTP_PORT      = 587
IMAP_HOST      = "imap.gmail.com"
IMAP_PORT      = 993

# ── Security ──────────────────────────────────────────────────────────────────
VAULT_KEY_FILE      = "data/vault.key"
AUTO_LOCK_MINUTES   = 0     # 0 = disabled
HONEYPOT_FILES      = ["data/honeypot.txt"]

# ── Developer ─────────────────────────────────────────────────────────────────
DEFAULT_CODE_LANG = "python"
SANDBOX_TIMEOUT   = 10      # seconds to run sandboxed code

# ── Smart Home ────────────────────────────────────────────────────────────────
MQTT_BROKER    = "localhost"
MQTT_PORT      = 1883
HA_URL         = "http://localhost:8123"
HA_TOKEN       = ""

# ── Paths ─────────────────────────────────────────────────────────────────────
SCREENSHOT_DIR = "screenshots"
RECORDING_DIR  = "recordings"
BACKUP_DIR     = "backups"
DOWNLOAD_DIR   = "downloads"

# ── Hotkeys ───────────────────────────────────────────────────────────────────
HOTKEYS = {
    "ctrl+shift+j": "activate_jarvis",
    "ctrl+shift+s": "take_screenshot",
    "ctrl+shift+m": "volume_mute",
    "ctrl+shift+p": "play_pause",
    "ctrl+shift+r": "start_recording",
}

# ── Safety ────────────────────────────────────────────────────────────────────
BLOCKED_KEYWORDS = [
    "rm -rf", "format c:", "del /f /s /q c:\\",
    "system32", ":(){:|:&};:", "deltree", "rd /s /q c:\\",
]
CONFIRM_REQUIRED = [
    "shutdown", "restart", "delete_file", "kill_process",
    "forget_everything", "format_drive", "send_email",
    "clear_vault", "wipe_database", "uninstall_app",
]

# ── All Commands ──────────────────────────────────────────────────────────────
COMMANDS = {
    # Apps
    "open_browser":"start chrome","open_firefox":"start firefox",
    "open_edge":"start msedge","open_notepad":"notepad",
    "open_explorer":"explorer","open_calculator":"calc",
    "open_cmd":"start cmd","open_powershell":"start powershell",
    "open_task_manager":"taskmgr","open_paint":"mspaint",
    "open_vscode":"code","open_spotify":"start spotify",
    "open_discord":"start discord","open_settings":"start ms-settings:",
    "open_control_panel":"control","open_device_manager":"devmgmt.msc",
    # System
    "flush_dns":"ipconfig /flushdns",
    "lock_screen":"rundll32.exe user32.dll,LockWorkStation",
    "shutdown":"shutdown /s /t 10","restart":"shutdown /r /t 10",
    "cancel_shutdown":"shutdown /a",
    "sleep":"rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
    # All others handled in executor
    **{k: None for k in [
        # Web
        "search_google","search_youtube","search_wikipedia","search_github",
        "open_url","get_weather","get_news","get_crypto_price","get_stock_price",
        "translate_text","check_website","download_file","speed_test",
        "ip_geolocation","dns_lookup","whois_lookup","check_breach",
        "get_crypto_alert","wifi_passwords","scrape_url",
        # Files
        "create_file","delete_file","read_file","write_to_file","rename_file",
        "copy_file","move_file","list_files","search_file","zip_files",
        "unzip_file","get_file_info","open_file","ocr_image",
        "pdf_merge","pdf_split","pdf_to_text","find_duplicates",
        "organize_downloads","batch_rename","file_watch","text_diff",
        "image_resize","image_convert","extract_metadata",
        # System
        "show_cpu","show_ram","show_disk","show_battery","show_gpu",
        "show_temp","system_report","list_processes","kill_process",
        "show_ip","show_wifi","ping_host","scan_ports","arp_scan",
        "clear_temp","empty_recycle_bin","get_startup_apps",
        "add_to_startup","remove_from_startup","flush_memory",
        "list_services","start_service","stop_service",
        "power_plan","list_windows","focus_window","minimize_window",
        "maximize_window","close_window","take_screenshot","screen_record",
        "get_wifi_passwords","network_speed","boot_analyzer",
        # Media
        "volume_up","volume_down","volume_mute","volume_set",
        "play_pause","next_track","prev_track",
        "show_clipboard","copy_to_clipboard","clear_clipboard",
        "clipboard_history","download_youtube","shazam",
        # Vision
        "webcam_snapshot","motion_detect","face_recognize","intruder_alert",
        "scan_qr_webcam","color_picker","object_detect","read_screen",
        # Productivity
        "set_reminder","show_reminders","delete_reminder","set_alarm",
        "start_timer","stop_timer","start_pomodoro","stop_pomodoro",
        "calculate","convert_units","generate_qr","send_email","read_emails",
        "add_alias","list_aliases","remove_alias","generate_password",
        "tell_joke","get_time","get_date","get_calendar","add_calendar_event",
        "habit_track","habit_show","mood_log","mood_show",
        "add_task","list_tasks","complete_task","delete_task",
        "start_focus","stop_focus","daily_briefing","pomodoro_status",
        "log_expense","show_expenses",
        # Vault & Security
        "vault_add","vault_get","vault_list","vault_delete","clear_vault",
        "totp_add","totp_get","encrypt_file","decrypt_file","shred_file",
        "check_password_strength","file_integrity_check","honeypot_status",
        # Dev Tools
        "run_code","git_status","git_pull","git_push","git_log","git_diff",
        "validate_yaml","stop_server","git_commit_message","install_package",
        "git_commit","http_request","format_json","encode_base64",
        "decode_base64","hash_text","regex_test","serve_folder",
        "generate_readme","generate_tests","analyze_deps",
        "docker_ps","docker_start","docker_stop","docker_logs",
        # Automation
        "record_macro","play_macro","list_macros","schedule_job",
        "list_jobs","cancel_job","file_watcher_start","rules_add","rules_list",
        "backup_folder","restore_backup","auto_organize",
        # Mobile/Remote
        "adb_devices","adb_screenshot","adb_install","send_notification","send_push_notification",
        "telegram_send","wake_on_lan",
        # Smart Home
        "mqtt_publish","mqtt_subscribe","ha_toggle","ha_state","ha_list",
        # Memory
        "remember_this","what_do_you_know","forget_this","forget_everything",
        "show_history","export_memory","summarize_text","explain_topic",
        "chat","unknown",
    ]}
}

# ── New V4.1 Commands ─────────────────────────────────────────────────────────
NEW_COMMANDS = {
    # Text Tools
    "word_count","case_upper","case_lower","case_title","case_camel","case_snake",
    "case_kebab","case_pascal","case_reverse","case_alternate","remove_duplicates",
    "sort_lines","remove_empty_lines","trim_whitespace","add_line_numbers",
    "find_replace","extract_emails","extract_urls","extract_phones","extract_numbers",
    "count_words_freq","rot13","morse_encode","morse_decode","binary_encode",
    "binary_decode","hex_encode","hex_decode","lorem_ipsum","random_sentence",
    "random_quote","random_name","random_color","random_number","flip_coin","roll_dice",
    "readability_score","detect_language","palindrome_check","anagram_check",
    # Health
    "bmi_calculate","calories_needed","ideal_weight","water_goal","log_water",
    "show_water_today","log_sleep","show_sleep_week","log_workout","show_workouts",
    "workout_streak","personal_records","log_weight","show_weight_history",
    "log_calories","show_calories_today","health_tip","breathing_exercise",
    # Network Advanced
    "ssl_check","traceroute","subdomain_scan","mac_lookup","network_interfaces",
    "open_connections","bandwidth_monitor","firewall_status","shared_folders",
    "check_port_open","dns_records","http_headers","find_my_public_ip",
    "reverse_dns","port_to_service","vpn_check",
    # Advanced AI
    "code_review","explain_code","fix_code","translate_code","generate_code",
    "optimize_code","add_docstrings","write_email","improve_writing","write_essay",
    "write_linkedin_post","write_tweet","debate_topic","pros_cons","fact_check",
    "what_if","interview_prep","study_plan","rag_index_file","rag_query",
    "daily_word","eli5",
    # Analytics
    "command_stats","productivity_report","weekly_summary","mood_trends",
    "habit_analytics","expense_breakdown","sleep_analytics","ascii_bar_chart",
    "generate_report","disk_usage_breakdown",
    # Creative
    "ascii_banner","ascii_art_from_image","draw_box","progress_bar",
    "random_color_palette","generate_username","generate_api_key","generate_uuid",
    "story_generator","meme_text","rhyme_words","haiku_generator","acronym_generator",
    "number_facts","prime_check","fibonacci","factorize","base_convert",
    "statistics_calc","countdown_timer","stopwatch_lap","world_clock",
}
for _c in NEW_COMMANDS:
    COMMANDS[_c] = None

# ── V4.2 Commands ─────────────────────────────────────────────────────────────
V42_COMMANDS = {k: None for k in [
    # Finance
    "currency_convert","currency_list","emi_calculator","loan_amortization",
    "simple_interest","compound_interest","sip_calculator","ppf_calculator",
    "fd_calculator","roi_calculator","breakeven_calculator","inflation_calculator",
    "retirement_calculator","set_budget","show_budget","add_bill","show_bills",
    "mark_bill_paid","add_savings_goal","update_savings","show_savings_goals",
    "add_investment","show_portfolio","income_tax_india","gst_calculator",
    # Study
    "add_flashcard","review_flashcard","reveal_card","rate_card","list_decks",
    "export_deck","import_deck","add_note","get_note","list_notes","search_notes",
    "update_note","delete_note","pin_note","export_notes","log_study_session",
    "show_study_stats","study_streak","add_vocab","quiz_vocab","reveal_vocab",
    "master_vocab","show_vocab","generate_quiz","explain_wrong_answer",
    "summarize_for_study","create_mind_map","mnemonics_generator",
    # System Advanced
    "full_system_info","os_version","installed_updates","check_admin",
    "system_locale","bios_info","list_env_vars","get_env_var","get_path_entries",
    "list_scheduled_tasks","create_scheduled_task","delete_scheduled_task",
    "run_scheduled_task","list_drivers","check_driver_issues","list_drives",
    "check_disk_health","disk_cleanup_analysis","list_users","list_groups",
    "current_user_info","logged_in_users","list_fonts","clipboard_to_file",
    "file_to_clipboard","performance_baseline","reset_network_stack",
    "wifi_available_networks","bluetooth_devices","windows_activation_status",
    # Content
    "content_calendar","social_media_strategy","viral_hook_generator",
    "caption_generator","thread_generator","youtube_description","youtube_title_ideas",
    "blog_outline","seo_keywords","newsletter_template","press_release",
    "product_description","ad_copy","cold_email_template","resume_bullet_point",
    "grammar_check","tone_analyzer","paraphrase","expand_text","condense_text",
    "formal_to_casual","casual_to_formal","bullet_to_paragraph","paragraph_to_bullets",
    "active_to_passive","passive_to_active","add_examples","simplify_jargon",
    "hashtag_generator","bio_generator","engagement_response","collaboration_pitch",
    "content_ideas","trending_topics_prompt",
    # Lifestyle
    "recipe_from_ingredients","recipe_substitute","meal_plan_week","nutrition_info",
    "cooking_conversion","food_pairing","calorie_burn","bmi_diet_plan",
    "travel_itinerary","packing_list","travel_budget_calculator","visa_requirements",
    "currency_tips","local_phrases","best_time_to_visit","travel_insurance_guide",
    "days_until","age_calculator","date_difference","what_day_is",
    "countdown_to_event","random_activity","inspirational_quote",
    "this_day_in_history","fun_facts","riddle","would_you_rather",
    "personality_quiz","life_hack","decision_matrix","eisenhower_matrix",
    "smart_goal","habit_stacking",
    # Code Generator
    "scaffold_flask_app","scaffold_fastapi_app","scaffold_cli_tool",
    "scaffold_sqlite_manager","scaffold_class","scaffold_test_file",
    "scaffold_dockerfile","scaffold_env_file","generate_gitignore",
    "ai_generate_module",
    # Science
    "newton_second_law","kinetic_energy","potential_energy","ohms_law",
    "electric_power","projectile_motion","speed_of_light_calc","pendulum_period",
    "wavelength_frequency","element_info","molar_mass","ph_calculator",
    "boiling_point_altitude","planet_info","light_years_to_km","age_of_universe",
    "solar_system_scale","dna_complement","mrna_from_dna","gc_content",
]}
COMMANDS.update(V42_COMMANDS)
