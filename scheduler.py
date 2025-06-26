import datetime
import pytz
import holidays
import user_manager
import subprocess

# ##############################################################################
#                               PRODUCTION SCRIPT
# ##############################################################################

# --- Production Configuration ---
TIMEZONE = 'Asia/Kolkata'
TIME_IN_HOUR, TIME_IN_MINUTE = 20, 30
TIME_OUT_HOUR, TIME_OUT_MINUTE = 6, 45
MAHARASHTRA_HOLIDAYS = holidays.IN(state='MH')
IS_DRY_RUN = "False" 

# ##############################################################################

def notify(message):
    """Calls the notifier script to send a message to the group."""
    print(f"Sending notification: {message}")
    subprocess.run(["python3", "notifier.py", message])

def get_action_for_now():
    """Determines the required action for the live scheduler."""
    now_pune = datetime.datetime.now(pytz.timezone(TIMEZONE))
    today_pune_date = now_pune.date()
    weekday = today_pune_date.weekday()

    if today_pune_date in MAHARASHTRA_HOLIDAYS:
        return "Holiday", MAHARASHTRA_HOLIDAYS.get(today_pune_date)
    if weekday == 6:
        return "Sunday", None
    
    is_time_for_in = (now_pune.hour, now_pune.minute) == (TIME_IN_HOUR, TIME_IN_MINUTE)
    is_time_for_out = (now_pune.hour, now_pune.minute) == (TIME_OUT_HOUR, TIME_OUT_MINUTE)

    if weekday < 5 and is_time_for_in: return "TimeIn", today_pune_date.strftime('%Y-%m-%d')
    if weekday == 5 and is_time_for_out: return "TimeOut", today_pune_date.strftime('%Y-%m-%d')
    if 0 < weekday < 5 and is_time_for_out: return "TimeOut", today_pune_date.strftime('%Y-%m-%d')
    
    return None, None

def main():
    """Main production function executed by the cron job."""
    print(f"\n--- Scheduler running in LIVE mode at {datetime.datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')} ---")
    action, date_info = get_action_for_now()
    
    if not action:
        print("No action required at this time.")
        return

    if action in ["Holiday", "Sunday"]:
        notify(f"📋 *Automation Skipped* 📋\n\nToday is {action}" + (f" ({date_info})" if date_info else "") + ". No actions will be performed.")
        return

    notify(f"🔔 *Starting {action} Automation* 🔔")
    all_users = user_manager.load_users()
    if not all_users:
        notify("SCHEDULER ERROR: No users found.")
        return

    success_users, failure_users, leave_users = [], [], []

    for user_id, details in all_users.items():
        if not isinstance(details, dict) or "beehive_username" not in details:
            print(f"ERROR: Corrupt data for user_id: {user_id}. Skipping.")
            continue
            
        username = details["beehive_username"]
        if date_info in details.get("leave_dates", []):
            leave_users.append(username)
            continue
        
        command = ["python3", "beehive_automator.py", username, details["beehive_password"], action, IS_DRY_RUN]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            success_users.append(username)
        else:
            failure_users.append(username)
            print(f"--- ERROR for user {username} ---\n{result.stdout}\n{result.stderr}\n--- END ERROR ---")

    summary_message = f"✅ *Automation Summary for {action}* ✅\n\n"
    if success_users: summary_message += f"Successfully processed: {', '.join(success_users)}\n"
    if failure_users: summary_message += f"Failed for: {', '.join(failure_users)}\n"
    if leave_users: summary_message += f"Skipped (on leave): {', '.join(leave_users)}\n"
    if success_users or failure_users or leave_users:
        notify(summary_message)

if __name__ == "__main__":
    main()
