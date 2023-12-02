function dateseq {(
	set -eu

	(( $# >= 2 && $# <= 3 )) || { 2>&1 echo 'usage: dateseq [start date] [stop date] [step days]'; exit 1; }
	curr_date="$1"
	stop_date="$2"
	step_days="${3:-1}"
	[[ "${step_days}" =~ ^-?[1-9][0-9]*$ ]] || { 2>&1 echo 'Step days must be a non-zero integer'; exit 1; }

	while true; do
		if (( step_days > 0 )); then
			[[ "${curr_date}" < "${stop_date}" ]] || break
		else
			[[ "${curr_date}" > "${stop_date}" ]] || break
		fi
		echo "${curr_date}"
		curr_date="$(gdate --date="${curr_date} + ${step_days} days" +%Y-%m-%d)"
	done
)}
