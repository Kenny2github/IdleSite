# must be run with `source activate.sh`

if [ -z "${IDLESITE_ENV+x}" ]; then
	export IDLESITE_ENV=$(pwd)
	PATHCOMPONENT="$(readlink -f $IDLESITE_ENV)/commands"
	export PATH="$PATH:$PATHCOMPONENT"
	unset PATHCOMPONENT
fi

for CMD in commands/*; do
	CMD=$(basename "$CMD")
	# skip non-executable files
	if [ ! -x "commands/$CMD" ]; then continue; fi
	echo $CMD
done
