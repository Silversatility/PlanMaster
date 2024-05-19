[[ -z "$1" ]] && echo "ERROR: npm command as argument required" && exit 2

cd src/frontend/
echo "$1: $(date +'%F %H:%M:%S') Installing node dependecies..."
npm install --loglevel=error
npm run $1
