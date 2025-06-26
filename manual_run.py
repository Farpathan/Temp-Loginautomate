import subprocess
import datetime
import pytz
import user_manager
import notifier

# ##############################################################################
#                             MANUAL TRIGGER SCRIPT
#
# Use this script to manually trigger a Time-In or Time-Out action for all users.
# It is designed to be run directly from the server's command line.
#
# How to run:
# 1. Connect to your server.
# 2. Navigate to your project directory.
# 3. Run the command: python3 manual_run.py
# ##############################################################################

def run_manual_flow(action, is_dry_run):
    """
    Executes the chosen automation flow for all users.
    
    Args:
        action (str): The action to perform ("TimeIn" or "TimeOut").
        is_dry_run (str): "True" to run in test mode, "False" for a live run.
    """
    run_mode = "DRY RUN" if is_dry_run == "True" else "LIVE RUN"
    
    # Announce the start of the manual run in the Telegram group
    notifier.send_notification(f"🔥 *Starting MANUAL {run_mode} for {action}* 🔥")
    
    all_users = user_manager.load_users()

    if not all_users:
        notifier.send_notification("MANUAL RUN FAILED: No users found to process.")
        return

    # We need the current date to check against leave schedules
    date_info = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d')
    
    success_users, failure_users, leave_users = [], [], []

    for user_id, details in all_users.items():
        if not isinstance(details, dict) or "beehive_username" not in details:
            print(f"ERROR: Corrupt data for user_id: {user_id}. Skipping.")
            continue
            
        username = details["beehive_username"]
        
        # Check if the user is on leave today
        if date_info in details.get("leave_dates", []):
            leave_users.append(username)
            continue
        
        print(f"\n--- Running for user: {username} ---")
        command = ["python3", "beehive_automator.py", username, details["beehive_password"], action, is_dry_run]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            success_users.append(username)
        else:
            failure_users.append(username)
            # Print the detailed error from the automator script to the terminal
            print(f"--- ERROR for user {username} ---\n{result.stdout}\n{result.stderr}\n--- END ERROR ---")

    # --- Send Final Summary Notification ---
    summary_message = f"✅ *MANUAL {run_mode} Summary for {action}* ✅\n\n"
    if success_users: summary_message += f"Successfully processed: {', '.join(success_users)}\n"
    if failure_users: summary_message += f"Failed for: {', '.join(failure_users)}\n"
    if leave_users: summary_message += f"Skipped (on leave): {', '.join(leave_users)}\n"
    
    if success_users or failure_users or leave_users:
        notifier.send_notification(summary_message)
    
    print("\n--- MANUAL RUN COMPLETE ---")


if __name__ == "__main__":
    # --- Interactive Menu ---
    print("--- Beehive Manual Trigger ---")
    
    # 1. Choose the action
    action_choice = input("Select action:\n  1: Time In\n  2: Time Out\nEnter choice (1 or 2): ")
    if action_choice == '1':
        action_to_run = "TimeIn"
    elif action_choice == '2':
        action_to_run = "TimeOut"
    else:
        print("Invalid choice. Exiting.")
        exit()

    # 2. Choose the mode (Dry Run or Live)
    mode_choice = input(f"\nHow do you want to run '{action_to_run}'?\n  1: Dry Run (Safe test, no clicks)\n  2: LIVE RUN (Performs real clicks)\nEnter choice (1 or 2): ")
    if mode_choice == '1':
        is_dry_run_str = "True"
        print("\nStarting a safe DRY RUN...")
    elif mode_choice == '2':
        is_dry_run_str = "False"
        # Add a final confirmation for a live run to prevent accidents
        confirm_live = input("!!! WARNING: You are about to perform a LIVE RUN. Are you sure? (yes/no): ")
        if confirm_live.lower() != 'yes':
            print("Live run canceled. Exiting.")
            exit()
        print("\nStarting a LIVE RUN...")
    else:
        print("Invalid choice. Exiting.")
        exit()

    # 3. Execute the chosen flow
    run_manual_flow(action_to_run, is_dry_run_str)
