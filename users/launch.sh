for i in {21..34}
do
    python get_users.py $i &
done
wait
exit 0
