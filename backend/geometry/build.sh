#!/bin/bash
set -e

# Get conda environment path
CONDA_ENV=$(conda info --envs | grep '*' | awk '{print $NF}')

# Create build directory
rm -rf build
mkdir -p build
cd build

# Configure CMake
cmake ../core/cpp_extensions \
    -DCMAKE_BUILD_TYPE=Release \
    -DPython_ROOT_DIR="${CONDA_ENV}" \
    -DPython_EXECUTABLE="${CONDA_ENV}/bin/python" \
    -DPYTHON_EXECUTABLE="${CONDA_ENV}/bin/python" \
    -DBOOST_ROOT="${CONDA_ENV}" \
    -DBOOST_INCLUDEDIR="${CONDA_ENV}/include" \
    -DBOOST_LIBRARYDIR="${CONDA_ENV}/lib" \
    -DBoost_NO_SYSTEM_PATHS=ON

# Build
cmake --build . -- -j4

# Copy the built libraries to the correct location
mkdir -p ../core/cpp_extensions/lib
cp *.so ../core/cpp_extensions/lib/

cd ..
