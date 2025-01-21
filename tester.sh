#!/bin/bash

###################### CONFIG ######################
LOG=1
CLEAN=0
tests_dir="tests"

###################### TESTS ######################

########### COMMANDS ###########
commands=(
    "cat $tests_dir/test1"
	"< $tests_dir/test1 wc -l"
	"echo "hello" > $tests_dir/file_res/test1" # check out
	"cat $tests_dir/test1 | wc -l"
	"cat $tests_dir/test1 | wc -l | cat"
	"< $tests_dir/test1 wc -l | cat"
	"< $tests_dir/test1 wc -l | cat | wc -l"
	"< $tests_dir/test1 wc -l | cat > $tests_dir/file_res/test2" # check out
	"echo "append" >> $tests_dir/file_res/test2" # check out
	"< $tests_dir/test1 wc -l | cat >> $tests_dir/file_res/test2" # check out
	"<< stop cat\\nzzz\\nzzz\\nzzz\\nstop"
	"<< stop cat | wc -l\\nzzz\\nzzz\\nzzz\\nstop"
	"<< stop cat | wc -l | wc -l\\nzzz\\nzzz\\nzzz\\nstop"
	"cat $tests_dir/test1 | gzip > $tests_dir/file_res/test1.gz" # check out
	#"MY_VAR='erratas on the track'"
	#"echo \$MY_VAR"
	"<< stop wc -w\n1 2 3\n4 5\n6\nstop"
)
# ajouter tests d'erreur

########### EXPECTED RESULTS ###########
expected_results=(
    "a\na\na\na\na" #0
	"5" #1
	""
	"5"
	"5"
	"5"
	"1"
	""
	""
	""
	"zzz\nzzz\nzzz"
	"3"
	"1"
	""
	#""
	#"erratas on the track"
	"6"
)

########### FILES CHECKS ###########
file_contents_check=("hello"
"5\nappend\n5")

########### TESTER ###########
num_commands=${#commands[@]}

file_contents=("a\na\na\na\na"
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
done

for ((i = 0; i < ${#file_contents_check[@]}; i++)); do
    file_name="test_check$((i + 1))"
    file_path="$tests_dir/file_res/$file_name"
	echo -e "${file_contents_check[i]}" > "$file_path"
done

failures=0

echo -e "\\nCommands:"

for ((i=0; i<num_commands; i++)); do
	clean_command=$(echo "${commands[i]}" | sed 's/\\n/\n/g')

    echo "Command [$i] : \"$clean_command\""

	OUTPUT=$(bash --posix -c "$clean_command")
	#echo "Output : $OUTPUT"
	#expected_output=$(echo -e "${expected_results[i]}")
    expected_output=$(echo -e "${expected_results[i]}")

    if [ "$OUTPUT" == "$expected_output" ]; then
        echo "✅ Success"
		if [ "$LOG" -eq 1 ]; then
			echo "✅ : |$OUTPUT|"
			echo "✅ : |$expected_output|"
		fi
    else
        echo "❌ Failed"
		failures=$((failures + 1))
		if [ "$LOG" -eq 1 ]; then
			echo "❌ : |$OUTPUT|"
			echo "✅ : |$expected_output|"
		fi
    fi


    echo "--------------------------------------"
done

echo -e "\\nFILES:"

for ((i = 0; i < ${#file_contents_check[@]}; i++)); do
    file1_name="test$((i + 1))"
    file2_name="test_check$((i + 1))"

    file1="$tests_dir/file_res/$file1_name"
	file2="$tests_dir/file_res/$file2_name"

	if cmp -s $file1 $file2; then
		echo "✅ : $file1_name == $file2_name"
	else
		echo "❌ : $file1_name != $file2_name"
		failures=$((failures + 1))
	fi
done

echo -e "\\n\\nRESULTS:"
echo "✅ : $((num_commands + ${#file_contents_check[@]} - failures))/$((num_commands + ${#file_contents_check[@]}))"
if [ "$failures" -gt 0 ]; then
	echo "❌ : $failures/$((num_commands + ${#file_contents_check[@]}))"
fi

# Clean up
if [ "$CLEAN" -eq 1 ]; then
	rm -rf "$tests_dir"
fi