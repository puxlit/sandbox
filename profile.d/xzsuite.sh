function xzsuite {(
	set -eu

	(( $# >= 1 && $# <= 2 )) || { 2>&1 echo 'usage: xzsuite [source file] [destination directory]'; exit 1; }
	source_name="$(basename "$1")"
	source_file="$(greadlink -e "$1")" && [[ -f "${source_file}" ]] || { 2>&1 echo 'Source file does not exist'; exit 1; }
	dest_dir="$(greadlink -e "${2:-.}")" && [[ -d "${dest_dir}" ]] || { 2>&1 echo 'Destination directory does not exist'; exit 1; }
	temp_dir="$(mktemp -d)" || { 2>&1 echo 'Failed to create temporary directory'; exit 1; }

	best_size="$(stat -f%z "${source_file}")"
	for compression_preset_level in 0 0e 1 1e 2 2e 3 3e 4 4e 5 5e 6 6e 7 7e 8 8e 9 9e; do
		candidate_file="${temp_dir}/${source_name}.${compression_preset_level}.xz"
		xz --verbose --compress --keep --stdout --check=sha256 "-${compression_preset_level}" "${source_file}" >"${candidate_file}"
		candidate_size="$(stat -f%z "${candidate_file}")"
		if (( candidate_size < best_size )); then
			best_candidate_file="${candidate_file}"
			best_size="${candidate_size}"
		fi
	done

	ls -lS "${source_file}" "${temp_dir}/${source_name}."{0,0e,1,1e,2,2e,3,3e,4,4e,5,5e,6,6e,7,7e,8,8e,9,9e}".xz"
	if [[ -n "${best_candidate_file:+x}" ]]; then
		echo "<$(basename "${best_candidate_file}")> is the best; this will be moved to <${dest_dir}>..."
	else
		echo "Uncompressed source file is the best; nothing will be done..."
	fi
	read -rsn1 -p 'Press any key to continue...'; echo
	if [[ -n "${best_candidate_file:+x}" ]]; then
		mv "${best_candidate_file}" "${dest_dir}/"
	fi
	rm -fR "${temp_dir}"
)}
