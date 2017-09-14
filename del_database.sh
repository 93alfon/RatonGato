#$ echo $DATABASE_URL
#postgres://lfpbjeowocfshx:1s7WGSUN_dsm2U-dYJPs7b1B9G@ec2-23-23-176-135.compute-1.amazonaws.com:5432/dfdsqva1919p8e

export PGUSER=lfpbjeowocfshx
export PGPASSWORD=1s7WGSUN_dsm2U-dYJPs7b1B9G
export PGHOST=ec2-23-23-176-135.compute-1.amazonaws.com
export PGDATABASE=dfdsqva1919p8e

echo "delete from server_move;" | psql
echo "delete from server_game;" | psql
echo "delete from server_counter;" | psql
echo "delete from auth_user;" | psql

