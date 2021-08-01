# must be run with `source activate.sh`

if [ -z "${IDLESITE_ENV+x}" ]; then
	export IDLESITE_ENV=$(pwd)
	PATHCOMPONENT="$(readlink -f $IDLESITE_ENV)/commands"
	export PATH="$PATH:$PATHCOMPONENT"
	unset PATHCOMPONENT

	CMDS="$(find commands/ -type f -executable -printf "%P ")"
	for CMD in $CMDS; do
		eval complete $($CMD --completion) $CMD
	done
	complete -W "$CMDS" -E
fi
