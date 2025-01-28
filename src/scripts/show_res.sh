#!/usr/bin/env bash

resdir="./results"
prettydir="./pretty_results"
file=$(find "$resdir" -type f | fzf)
basename=$(basename -- "$file")
filename="${basename%.*}"
pretty_file_name="$prettydir/$filename".pretty.json
pretty=false

if [[ $(command -v prettier) && ! (-f "$pretty_file_name") ]] ; then
    echo "INFO: making $file pretty!"
    cp "$file" "$pretty_file_name"
    prettier "$pretty_file_name" --write
    pretty=true
fi

if [[ $(command -v bat) && $pretty ]]; then
    bat "$basename".pretty.json
elif [[ $(command -v bat) ]]; then
    bat "$file"
else
    cat "$file"
fi
