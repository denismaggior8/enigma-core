# Upload Enigma Core (this may take a while)
echo "Transferring Enigma Core..."
cd dist                                                                                                                                  
find . -type d -exec ampy --port $ESPPORT mkdir {} \; 2>/dev/null
find . -type f -exec ampy --port $ESPPORT put {} {} \;
cd ..