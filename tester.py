import subprocess
import re

###################### CONFIG ######################
LOG=1
CLEAN=1
minishell_path = "./minishell"
tests_dir="tests"

command = [
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
	diff = cleaned_with_prompt.replace(output_without_prompt, "").strip()
    
	pattern =  re.sub(r'\d+', r'(\\d+)', re.escape(diff.splitlines()[-1]), count=1) if diff else None
      
	matches = re.findall(pattern, cleaned_with_prompt)

	return matches[-1] if matches else None 

def custom_prompt(output_with_prompt, output_without_prompt):
	"""Extract custom prompt from output"""

	cleaned_with_prompt = clean_ansi_codes(output_with_prompt).strip()

	diff = cleaned_with_prompt.replace(output_without_prompt, "").strip()
     
	res =  re.sub(r'\d+', r'\\d+', re.escape(diff.splitlines()[-1]), count=1) if diff else None
    
	return res

def run_command_in_shells(command):
	"""Exec command in minishell and bash --posix"""

	# Minishell
	minishell_process = subprocess.run(minishell_path, input=command, text=True, capture_output=True)

	# bash --posix
	bash_cmd = ["bash", "--posix", "-c", command]
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

command = "wc -p"
res = run_command_in_shells(command)

# Affichage des résultats
print("=== Minishell ===")
print(f"-> stdout: -{res['minishell']['stdout']}-")
print(f"-> stderr: -{res['minishell']['stderr']}-")
print(f"-> returncode: -{res['minishell']['returncode']}-")

print("\n=== Bash --posix ===")
print(f"stdout: -{res['bash']['stdout']}-")
print(f"stderr: -{res['bash']['stderr']}-")
print(f"returncode: -{res['bash']['returncode']}-")

# Vérification si les sorties sont identiques
if res["minishell"] == res["bash"]:
    print("\n✅ Les sorties sont identiques !")
else:
    print("\n❌ Les sorties diffèrent !")