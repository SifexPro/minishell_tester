import subprocess
import re
import os

###################### CONFIG ######################
LOG = True
LOG_SUCCEDED = False
CLEAN = True
minishell_path = "./minishell"
mini_dir="mini_tests"
bash_dir="bash_tests"
####################################################

if not os.path.exists(mini_dir):
	os.mkdir(mini_dir)
if not os.path.exists(bash_dir):
	os.mkdir(bash_dir)

command = [
    "ls",
	"echo test",
]

command_files = [
    "echo \"Hello, world!\" > _DIR_/test1",
	"cat _DIR_/test1",
	"< _DIR_/test1 wc -l",
	"< _DIR_/test1 cat | wc -l",
	#"< _DIR_/test1 cat | wc -l | cat",
	"cat _DIR_/test1 | gzip > _DIR_/file_res/test1.gz"
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

def run_command_in_shells(mini_command, bash_command):
	"""Exec command in minishell and bash --posix"""

	# Minishell
	minishell_process = subprocess.run(minishell_path, input=mini_command, text=True, capture_output=True)

	# bash --posix
	bash_cmd = ["bash", "--posix", "-c", bash_command]
	bash_process = subprocess.run(bash_cmd, text=True, capture_output=True)

	detected_prompt = custom_prompt(minishell_process.stdout, bash_process.stdout)
	minishell_status = extract_exit_code(minishell_process.stdout, bash_process.stdout)

	if (len(minishell_process.stderr) == 0 and len(minishell_process.stdout) > 0):
		minishell_stdout_clean = clean_output(minishell_process.stdout, detected_prompt)
	else:
		minishell_stdout_clean = ""
	
	if (len(minishell_stdout_clean) > 0):
		minishell_stdout_clean += "\n"
	
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

def compare_files(file1, file2):
	try:
		with open(file1, 'r') as f1, open(file2, 'r') as f2:
			if f1.read() == f2.read():
				return True
			else:
				if (LOG):
					print(f"❌ |{f1.read()}|")
					print(f"✅ |{f2.read()}|")
				return False
	except FileNotFoundError:
		if (LOG):
			print("❌ One of the files does not exist")
		return False
	except Exception as e:
		if (LOG):
			print(f"❌ An error occured: {e}")
		return False
	
def log_res(failed, mini_res, bash_res):
	if (failed):
		if (mini_res['stdout'] != bash_res['stdout']):
			print(f"❌ stdout: |{mini_res['stdout']}|")
			print(f"✅ stdout: |{bash_res['stdout']}|")
		if (mini_res['stderr'] != bash_res['stderr']):
			print(f"❌ stderr: {mini_res['stderr']}")
			print(f"✅ stderr: {bash_res['stderr']}")
		if (mini_res['returncode'] != bash_res['returncode']):
			print(f"❌ returncode: {mini_res['returncode']}")
			print(f"✅ returncode: {bash_res['returncode']}")
	elif (LOG_SUCCEDED):
		print(f"✅ stdout: {mini_res['stdout']}")
		print(f"✅ stdout: {bash_res['stdout']}")
		print(f"✅ stderr: {mini_res['stderr']}")
		print(f"✅ stderr: {bash_res['stderr']}")
		print(f"✅ returncode: {mini_res['returncode']}")
		print(f"✅ returncode: {bash_res['returncode']}")

def	launch_test_with_file():
	"""Launch tests with file"""
	count = 0
	for i in range(len(command_files)):
		if (i != 0):
			print()
		print(f"\033[33mCommand [{i}]: \"{command_files[i]}\"\033[0m")
		mini_command = command_files[i].replace("_DIR_", mini_dir)
		bash_command = command_files[i].replace("_DIR_", bash_dir)
	
		res = run_command_in_shells(mini_command, bash_command)
		file1 = re.search(r'\S+/\S+', mini_command).group(0)
		file2 = re.search(r'\S+/\S+', mini_command).group(0)
		
		is_file_equal = compare_files(file1, file2)
		if res["minishell"] == res["bash"] and is_file_equal:
			print("✅ Success")
			count += 1
			if (LOG):
				log_res(False, res["minishell"], res["bash"])
		else:
			print("❌Fail")
			if (LOG):
				log_res(True, res["minishell"], res["bash"])
	return count

def	launch_test_without_file():
	"""Launch tests without file"""
	count = 0
	for i in range(len(command)):
		if (i != 0):
			print()
		print(f"\033[33mCommand [{i}]: \"{command[i]}\"\033[0m")
	
		res = run_command_in_shells(command[i], command[i])

		if res["minishell"] == res["bash"]:
			print("✅ Success")
			count += 1
			if (LOG):
				log_res(False, res["minishell"], res["bash"])
		else:
			print("❌Fail")
			if (LOG):
				log_res(True, res["minishell"], res["bash"])
	return count

print(f"\033[0;35mCommand with file :\033[0m\n")
succeded_with_file = launch_test_with_file()
failed_with_file = len(command_files) - succeded_with_file
total_with_file = len(command_files)

print(f"\n\033[0;35mCommand without file :\033[0m\n")
succeded_without_file = launch_test_without_file()
failed_without_file = len(command) - succeded_without_file
total_without_file = len(command)

print(f"\n\033[0;35mResults :\033[0m\n")

succeded_total = succeded_with_file + succeded_without_file
failed_total = failed_with_file + failed_without_file
total_total = total_with_file + total_without_file

print(f"\033[33mWithout_file :\033[0m")
print(f"\033[0;32m✅ Succeded: {succeded_total}/{total_total}\033[0m")
print(f"\033[0;31m❌ Failed: {failed_total}/{total_total}\033[0m")