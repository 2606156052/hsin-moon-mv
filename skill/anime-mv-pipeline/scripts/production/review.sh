#!/bin/zsh
# usage: review.sh S02_t1 S03_t1 ...  -> sheets/<id>.jpg (10 frames each) and sheets/batch.jpg (stack)
F=${FFMPEG:-ffmpeg}
cd "${0:A:h}"
list=()
for id in "$@"; do
  [ -f clips/$id.mp4 ] || continue
  n=$("$F" -i clips/$id.mp4 2>&1 | grep -oE "Duration: [0-9:.]+" | awk -F'[:. ]' '{print ($3*60+$4)*30}')
  step=$(( n / 10 )); [ $step -lt 1 ] && step=1
  "$F" -y -loglevel error -i clips/$id.mp4 -vf "select='not(mod(n\,$step))',scale=384:-1,tile=5x2,pad=iw:ih+16:0:16:black" -frames:v 1 sheets/$id.jpg
  list+=(sheets/$id.jpg)
done
[ ${#list} -gt 0 ] && "$F" -y -loglevel error $(for f in $list; do echo -i $f; done) -filter_complex "vstack=inputs=${#list}" sheets/batch.jpg 2>/dev/null || cp $list[1] sheets/batch.jpg
echo ${#list} sheets
