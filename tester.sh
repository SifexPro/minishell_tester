#!/bin/bash

LOG=1
tests_dir="tests"

# ajouter tests d'erreur
commands=(
    "cat $tests_dir/test1"
	"< $tests_dir/test1 wc -l"
	"< $tests_dir/test1 wc -l | cat"
	"< $tests_dir/test1 wc -l | cat | wc -l"
	"< $tests_dir/test1 wc -l | cat > $tests_dir/file_res/test1" # check out
	"< $tests_dir/test1 wc -l | cat >> $tests_dir/file_res/test2" # check out
	"<< stop cat | wc -l\\nzzz\\nzzz\\nzzz\\nstop"
	"<< stop cat | wc -l | wc -l\\nzzz\\nzzz\\nzzz\\nstop"

)

expected_results=(
    "a\\na\\na\\na\\na" #0
	"5" #1
	"5" #2
	"1" #3
	"" #4
	"" #5
	"3" #6
	"1" #7
)

num_commands=${#commands[@]}

file_contents=("a\\na\\na\\na\\na"
"0")

if [ ! -d "$tests_dir" ]; then
    mkdir "$tests_dir"
fi

if [ ! -d "$tests_dir/file_res" ]; then
   	mkdir "$tests_dir/file_res"
fi

for ((i = 0; i < ${#file_contents[@]}; i++)); do
    file_name="test$((i + 1))"
    file_path="$tests_dir/$file_name"
	echo -e "${file_contents[i]}" > "$file_path"
    
    # Confirmation
    echo "Fichier '$file_path' créé avec succès."
done

failures=0

for ((i=0; i<num_commands; i++)); do
	clean_command=$(echo "${commands[i]}" | sed 's/\\n/\n/g')

    echo "Command [$i] : \"$clean_command\""

	OUTPUT=$(bash --posix -c "$clean_command")
	expected_output=$(echo "${expected_results[i]}" | sed 's/\\n/\n/g')
    
    if [ "$OUTPUT" == "$expected_output" ]; then
        echo "✅ Success"
		if [ "$LOG" -eq 1 ]; then
			echo "✅ : |$OUTPUT|"
		fi
    else
        echo "❌ Failed"
		failures=$((failures + 1))
		if [ "$LOG" -eq 1 ]; then
			echo "❌ : |$OUTPUT|"
			echo "✅ : |${expected_results[i]}|"
		fi
    fi


    echo "--------------------------------------"
done

echo -e "\\n\\nRESULTS:"
echo "✅ : $((num_commands - failures))/$num_commands"
if [ "$failures" -gt 0 ]; then
	echo "❌ : $failures/$num_commands"
fi

# Clean up
rm -rf "$tests_dir"