import subprocess

print("--- Starting XVFB Fix Test ---")

# This test will attempt a dry run for a single user.
# We are hardcoding the action and dry run mode for safety.
USERNAME = "GS3229" # Use one of your existing usernames
PASSWORD = "Uc@nwin2"  # The password for that user
ACTION = "TimeOut"
IS_DRY_RUN = "True"

command = [
    "python3", 
    "beehive_automator.py",
    USERNAME,
    PASSWORD,
    ACTION,
    IS_DRY_RUN
]

# Run the command and capture the result
result = subprocess.run(command, capture_output=True, text=True)

print("\n--- Test Results ---")
# Print the output from the automator script
print("STDOUT from automator:\n" + result.stdout)
print("STDERR from automator:\n" + result.stderr)

if result.returncode == 0:
    print("\n✅ TEST SUCCEEDED: The browser started correctly within the virtual screen.")
else:
    print("\n❌ TEST FAILED: The browser still crashed. See errors above.")


