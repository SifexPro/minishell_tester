import subprocess
import re

###################### CONFIG ######################
LOG = False
CLEAN = True
minishell_path = "./minishell"
tests_dir="tests"
####################################################

command = [
    "ls",
	"echo test",
]

command_files = [
    "ls",
	"echo test",
]

def clean_ansi_codes(output):
    """Remove ANSI color codes from output"""
    return re.sub(r"\x1B\[[0-9;]*m", "", output)

def clean_output(output, regex):
    """Remove custom prompt and ANSI color codes from output"""
    output = clean_ansi_codes(output)

    lines = output.splitlines()
    cleaned_lines = []

    for line in lines:
        if re.match(regex, line):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def extract_exit_code(output_with_prompt, output_without_prompt):
	"""Extract exit code from output"""

	cleaned_with_prompt = clean_ansi_codes(output_with_prompt).strip()
    
	pattern =  re.sub(r'\d+', r'(\\d+)', re.escape(cleaned_with_prompt.splitlines()[-1]), count=1)
      
	matches = re.findall(pattern, cleaned_with_prompt)

	return matches[-1] if matches else None 

def custom_prompt(output_with_prompt, output_without_prompt):
	"""Extract custom prompt from output"""

	cleaned_with_prompt = clean_ansi_codes(output_with_prompt).strip()
     
	res = re.sub(r'\d+', r'\\d+', re.escape(cleaned_with_prompt.splitlines()[-1]), count=1)
    
	return res

def run_command_in_shells(command, file_path):
	"""Exec command in minishell and bash --posix"""

	bash_command = command
	if (file_path):
		bash_command = bash_command.replace("mini_test", "bash_test")

	# Minishell
	minishell_process = subprocess.run(minishell_path, input=command, text=True, capture_output=True)

	# bash --posix
	bash_cmd = ["bash", "--posix", "-c", bash_command]
	bash_process = subprocess.run(bash_cmd, text=True, capture_output=True)

	detected_prompt = custom_prompt(minishell_process.stdout, bash_process.stdout)
	minishell_status = extract_exit_code(minishell_process.stdout, bash_process.stdout)

	if (len(minishell_process.stderr) == 0):
		minishell_stdout_clean = clean_output(minishell_process.stdout, detected_prompt) + "\n"
	else:
		minishell_stdout_clean = ""
	
	res = {
        "minishell": {
            "stdout": minishell_stdout_clean,
            "stderr": minishell_process.stderr,
            "returncode": int(minishell_status)
        },
        "bash": {
            "stdout": bash_process.stdout,
            "stderr": bash_process.stderr,
            "returncode": bash_process.returncode
        }
    }

	return res

def log_res(failed, mini_res, bash_res):
	if (failed):
		if (mini_res['stdout'] != bash_res['stdout']):
			print(f"❌ stdout: {mini_res['stdout']}")
			print(f"✅ stdout: {bash_res['stdout']}")
		if (mini_res['stderr'] != bash_res['stderr']):
			print(f"❌ stderr: {mini_res['stderr']}")
			print(f"✅ stderr: {bash_res['stderr']}")
		if (mini_res['returncode'] != bash_res['returncode']):
			print(f"❌ returncode: {mini_res['returncode']}")
			print(f"✅ returncode: {bash_res['returncode']}")
	else:
		print(f"✅ stdout: {mini_res['stdout']}")
		print(f"✅ stdout: {bash_res['stdout']}")
		print(f"✅ stderr: {mini_res['stderr']}")
		print(f"✅ stderr: {bash_res['stderr']}")
		print(f"✅ returncode: {mini_res['returncode']}")
		print(f"✅ returncode: {bash_res['returncode']}")


def	launch_test_without_file():
	for i in range(len(command)):
		print(f"\n\033[33mCommand [{i}]: \"{command[i]}\"\033[0m")
	
		res = run_command_in_shells(command[i], False)

		if res["minishell"] == res["bash"]:
			print("✅ Success")
			if (LOG):
				log_res(False, res["minishell"], res["bash"])
		else:
			print("❌Fail")
			if (LOG):
				log_res(True, res["minishell"], res["bash"])

launch_test_without_file()