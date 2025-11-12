SRC_DIR="src"
BUILD_DIR="dist"
PACKAGE_DIR=enigmacore

cd $SRC_DIR
for file in $(find . | grep -v __pycache__); 
do
    if [ -d "${file}" ];
    then
        echo "Processing dir $file ..."
        if [ $file == "." ];
        then
            mkdir -p ../$BUILD_DIR/$PACKAGE_DIR
        fi
        mkdir -p ../$BUILD_DIR/$PACKAGE_DIR/$file
    else
        echo "Processing file $file ..."
        if [[ $file == *.py ]];
        then
            mpy-cross $file -o ../$BUILD_DIR/$PACKAGE_DIR/$(echo $file | sed 's/\.py$/\.mpy/')
        fi
    fi
done
micropython -m mip install github:denismaggior8/micropython-enigma-python --target ../$BUILD_DIR
cd ..