#! /bin/bash

months=("Jan" "Feb" "Mar" "Apr" "May" "Jun" "Jul" "Aug" "Sep" "Oct" "Nov" "Dec")
numbered_months=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12")

for i in "${!months[@]}"; do
    file_name="${numbered_months[$i]}_${months[$i]}.md"
    # touch "$file_name"
    echo "This is the file for ${months[$i]}" > "$file_name"
done

