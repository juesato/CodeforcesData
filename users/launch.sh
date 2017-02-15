for i in {0..12}
do
    python get_users.py $i &
done
wait
exit 0