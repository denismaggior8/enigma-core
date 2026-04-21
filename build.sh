SRC_DIR="src"
BUILD_DIR="dist"
ENIGMA_PYTHON_VERSION="3.1.2"

cd $SRC_DIR
for file in $(find . | grep -v __pycache__); 
do
    if [ -d "${file}" ];
    then
        echo "Processing dir $file ..."
        if [ $file == "." ];
        then
            rm -rf ../$BUILD_DIR
        fi
        mkdir -p ../$BUILD_DIR/$file
    else
        echo "Processing file $file ..."
        if [[ $file == *.py ]];
        then
            if [[ $file != "./main.py" ]] && [[ $file != "./boot.py" ]]; then
                echo "Compiling"
                mpy-cross $file -o ../$BUILD_DIR/$(echo $file | sed 's/\.py$/\.mpy/')
            else
                echo "Copying, not compiling"
                cp $file ../$BUILD_DIR/$file
            fi
        fi
    fi
done
micropython -m mip install github:denismaggior8/micropython-enigma-python@$ENIGMA_PYTHON_VERSION --target ../$BUILD_DIR
cd ..